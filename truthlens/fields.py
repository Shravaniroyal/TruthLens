"""
Indian ID field validators and PII-safe extraction from OCR/QR text.

Full identifiers are never stored in returned reports — only masked forms
and checksum validity flags.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field

# PAN: 5 letters, 4 digits, 1 letter
PAN_RE = re.compile(r"\b([A-Z]{5}[0-9]{4}[A-Z])\b", re.IGNORECASE)
# 12-digit Aadhaar with optional spaces
AADHAAR_RE = re.compile(r"\b(\d{4}[\s-]?\d{4}[\s-]?\d{4})\b")
# Indian DL: 2 letters + 2 digits + rest (state-wise formats vary)
DL_RE = re.compile(r"\b([A-Z]{2}[\s-]?\d{2}[\s-]?\d{4,11})\b", re.IGNORECASE)
DOB_RE = re.compile(
    r"\b((?:0?[1-9]|[12]\d|3[01])[/\-.](?:0?[1-9]|1[0-2])[/\-.](?:19|20)\d{2})\b"
)

# Verhoeff algorithm tables for Aadhaar checksum
_D = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 2, 3, 4, 0, 6, 7, 8, 9, 5),
    (2, 3, 4, 0, 1, 7, 8, 9, 5, 6),
    (3, 4, 0, 1, 2, 8, 9, 5, 6, 7),
    (4, 0, 1, 2, 3, 9, 5, 6, 7, 8),
    (5, 9, 8, 7, 6, 0, 4, 3, 2, 1),
    (6, 5, 9, 8, 7, 1, 0, 4, 3, 2),
    (7, 6, 5, 9, 8, 2, 1, 0, 4, 3),
    (8, 7, 6, 5, 9, 3, 2, 1, 0, 4),
    (9, 8, 7, 6, 5, 4, 3, 2, 1, 0),
)
_P = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 5, 7, 6, 2, 8, 3, 0, 9, 4),
    (5, 8, 0, 3, 7, 9, 6, 1, 4, 2),
    (8, 9, 1, 6, 0, 4, 3, 5, 2, 7),
    (9, 4, 5, 3, 1, 2, 6, 8, 7, 0),
    (4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
    (2, 7, 9, 3, 8, 0, 6, 4, 1, 5),
    (7, 0, 4, 6, 9, 1, 3, 2, 5, 8),
)


def aadhaar_checksum_ok(digits: str) -> bool:
    """Return True if 12-digit string passes Verhoeff checksum."""
    compact = re.sub(r"\D", "", digits)
    if len(compact) != 12 or not compact.isdigit():
        return False
    c = 0
    for i, ch in enumerate(reversed(compact)):
        c = _D[c][_P[i % 8][int(ch)]]
    return c == 0


def mask_aadhaar(digits: str) -> str:
    compact = re.sub(r"\D", "", digits)
    if len(compact) < 4:
        return "XXXX-XXXX-XXXX"
    return f"XXXX-XXXX-{compact[-4:]}"


def mask_pan(pan: str) -> str:
    pan = pan.upper().replace(" ", "")
    if len(pan) != 10:
        return "XXXXX####X"
    return f"XXXXX{pan[5:9]}X"


def _sha16(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


@dataclass
class ExtractedFields:
    doc_hints: list[str] = field(default_factory=list)
    pan_masked: str | None = None
    pan_valid_format: bool = False
    aadhaar_masked: str | None = None
    aadhaar_checksum_ok: bool = False
    dl_masked: str | None = None
    dob: str | None = None
    name_guess: str | None = None
    field_hashes: dict[str, str] = field(default_factory=dict)

    def to_public_dict(self) -> dict[str, object]:
        """JSON-safe payload with no full ID numbers."""
        return {
            "pan_masked": self.pan_masked,
            "pan_valid_format": self.pan_valid_format,
            "aadhaar_masked": self.aadhaar_masked,
            "aadhaar_checksum_ok": self.aadhaar_checksum_ok,
            "dl_masked": self.dl_masked,
            "dob": self.dob,
            "name_guess": self.name_guess,
        }


def extract_fields(text: str) -> ExtractedFields:
    """Parse OCR/QR text into masked fields. Input may contain PII — do not log it."""
    result = ExtractedFields()
    if not text:
        return result

    pan_m = PAN_RE.search(text)
    if pan_m:
        pan = pan_m.group(1).upper()
        result.pan_valid_format = True
        result.pan_masked = mask_pan(pan)
        result.field_hashes["pan"] = _sha16(pan)
        result.doc_hints.append("pan")

    aad_m = AADHAAR_RE.search(text)
    if aad_m:
        raw = aad_m.group(1)
        compact = re.sub(r"\D", "", raw)
        result.aadhaar_checksum_ok = aadhaar_checksum_ok(compact)
        result.aadhaar_masked = mask_aadhaar(compact)
        result.field_hashes["aadhaar"] = _sha16(compact)
        result.doc_hints.append("aadhaar")

    dl_m = DL_RE.search(text)
    if dl_m and not result.pan_valid_format:
        dl = re.sub(r"[\s-]", "", dl_m.group(1).upper())
        result.dl_masked = dl[:2] + "****" + dl[-2:] if len(dl) >= 4 else "****"
        result.field_hashes["dl"] = _sha16(dl)
        result.doc_hints.append("dl")

    dob_m = DOB_RE.search(text)
    if dob_m:
        result.dob = dob_m.group(1)

    name_m = re.search(
        r"(?:name|naam)\s*[:\-]?\s*([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,3})",
        text,
        re.IGNORECASE,
    )
    if name_m:
        result.name_guess = name_m.group(1).strip()[:80]

    return result
