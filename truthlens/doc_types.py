"""
Document type detection for Indian identity and BGV documents.

Uses filename keywords plus OCR/QR text. Zone maps in forensic_explainer
only special-case aadhaar / pan / dl; other types use generic zones.
"""

from __future__ import annotations

from truthlens.logging_setup import get_logger

log = get_logger("doc_types")

DOC_TYPE_LABELS: dict[str, str] = {
    "aadhaar": "Aadhaar Card",
    "pan": "PAN Card",
    "dl": "Driving Licence",
    "passport": "Passport",
    "voter": "Voter ID",
    "marksheet": "Marksheet",
    "degree": "Degree certificate",
    "experience": "Experience / relieving letter",
    "caste": "Caste certificate",
    "income": "Income certificate",
    "gst": "GST / tax document",
    "invoice": "Invoice",
    "cheque": "Cancelled cheque",
    "generic": "Generic Document",
}

_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("aadhaar", ("aadhaar", "aadhar", "uidai", "uid")),
    ("pan", ("permanent account", "income tax", "it_dept", "pan card")),
    ("dl", ("driving licence", "driving license", "motor")),
    ("passport", ("passport", "republic of india")),
    ("voter", ("election commission", "epic", "voter")),
    ("marksheet", ("marksheet", "mark sheet", "secondary school", "cbse", "ssc")),
    ("degree", ("university", "bachelor", "master", "convocation", "degree")),
    ("experience", ("relieving", "experience letter", "to whomsoever")),
    ("caste", ("caste certificate", "obc", "sc/st")),
    ("income", ("income certificate", "income proof")),
    ("gst", ("gstin", "goods and services")),
    ("invoice", ("invoice", "tax invoice")),
    ("cheque", ("please pay", "cancelled", "ifsc")),
]


def detect_doc_type(filename: str, text: str = "") -> str:
    """
    Infer document type from filename and optional OCR/QR text.
    Returns a key in DOC_TYPE_LABELS.
    """
    blob = f"{filename} {text}".lower()
    stem = filename.replace("\\", "/").split("/")[-1].lower()

    if any(k in stem for k in ("aadhaar", "aadhar")):
        return "aadhaar"
    if "pan" in stem.split(".")[0].replace("-", "_").split("_"):
        return "pan"
    if stem.startswith("pan.") or "_pan." in stem or "-pan." in stem:
        return "pan"

    import re

    if re.search(r"\b\d{4}\s?\d{4}\s?\d{4}\b", text or ""):
        if any(k in blob for k in ("aadhaar", "aadhar", "uidai", "government of india")):
            return "aadhaar"
    if re.search(r"\b[A-Z]{5}\d{4}[A-Z]\b", text or "", re.I):
        if "pan" in blob or "income" in blob or "tax" in blob:
            return "pan"

    for dtype, keywords in _RULES:
        if any(kw in blob for kw in keywords):
            log.debug("Doc type detected: %s", dtype)
            return dtype

    log.debug("Doc type detected: generic (filename=%s)", filename)
    return "generic"
