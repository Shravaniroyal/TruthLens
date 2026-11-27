"""
Security utilities for TruthLens.

Validates uploads before they reach the ML pipeline:
  - File size and extension checks
  - Magic-byte (content) validation — extension alone is not trusted
  - Decompression-bomb protection via pixel limits
  - Safe filename sanitization (path traversal prevention)

When gov APIs are added, store credentials only in environment variables.
"""

from __future__ import annotations

import hashlib
import io
import re
from dataclasses import dataclass

from PIL import Image, UnidentifiedImageError

from truthlens.config import settings
from truthlens.exceptions import ImageProcessingError, SecurityValidationError
from truthlens.logging_setup import audit_event, get_logger

log = get_logger("security")

# Magic bytes for allowed image formats
_MAGIC_SIGNATURES: dict[str, tuple[bytes, ...]] = {
    "jpg": (b"\xff\xd8\xff",),
    "jpeg": (b"\xff\xd8\xff",),
    "png": (b"\x89PNG\r\n\x1a\n",),
    "bmp": (b"BM",),
    "webp": (b"RIFF",),  # RIFF....WEBP — checked further below
    "tiff": (b"II*\x00", b"MM\x00*"),
    "pdf": (b"%PDF",),
}

# Only allow safe characters in stored/displayed filenames
_UNSAFE_FILENAME = re.compile(r"[^a-zA-Z0-9._-]+")


@dataclass(frozen=True)
class ValidatedUpload:
    """Result of a successful upload security check."""

    safe_filename: str
    extension: str
    size_bytes: int
    content_hash: str  # SHA-256 hex — for audit logs, not PII
    width: int
    height: int
    media_kind: str  # "image" | "pdf"


def sanitize_filename(filename: str) -> str:
    """
    Strip path components and unsafe characters from an uploaded filename.
    Prevents path-traversal attacks like '../../etc/passwd.jpg'.
    """
    # Keep only the base name — drops any directory segments
    base = filename.replace("\\", "/").split("/")[-1].strip()
    if not base or base in {".", ".."}:
        base = "upload"
    safe = _UNSAFE_FILENAME.sub("_", base)
    return safe[:200]  # cap length


def _extension_of(filename: str) -> str:
    parts = filename.rsplit(".", 1)
    return parts[-1].lower() if len(parts) == 2 else ""


def _matches_magic(data: bytes, ext: str) -> bool:
    """Verify file header bytes match the claimed extension."""
    if ext not in _MAGIC_SIGNATURES:
        return False
    for sig in _MAGIC_SIGNATURES[ext]:
        if not data.startswith(sig):
            continue
        # WEBP: RIFF header + WEBP at offset 8
        if ext == "webp" and len(data) >= 12:
            return data[8:12] == b"WEBP"
        return True
    return False


def validate_upload(file_bytes: bytes, original_filename: str) -> ValidatedUpload:
    """
    Run all upload security checks. Raises SecurityValidationError or
    ImageProcessingError with a safe user_message on failure.
    """
    safe_name = sanitize_filename(original_filename)
    ext = _extension_of(safe_name)
    size = len(file_bytes)

    log.debug("Validating upload | name=%s | ext=%s | size=%d", safe_name, ext, size)

    if size == 0:
        audit_event("upload_rejected", reason="empty_file")
        raise SecurityValidationError("Empty file", user_message="The uploaded file is empty.")

    if size > settings.max_upload_bytes:
        audit_event("upload_rejected", reason="file_too_large", size_bytes=size)
        raise SecurityValidationError(
            f"File exceeds {settings.max_upload_bytes} bytes",
            user_message=f"File too large. Maximum size is {settings.max_upload_bytes // (1024*1024)} MB.",
        )

    if ext not in settings.allowed_extensions:
        audit_event("upload_rejected", reason="bad_extension", ext=ext)
        raise SecurityValidationError(
            f"Extension '{ext}' not allowed",
            user_message="Unsupported file type. Please upload JPG, PNG, BMP, TIFF, WebP, or PDF.",
        )

    if not _matches_magic(file_bytes[:16], ext):
        audit_event("upload_rejected", reason="magic_mismatch", ext=ext)
        raise SecurityValidationError(
            "Magic bytes do not match extension",
            user_message="File content does not match its extension. Upload may be corrupted or disguised.",
        )

    content_hash = hashlib.sha256(file_bytes).hexdigest()
    width, height = 0, 0
    media_kind = "pdf" if ext == "pdf" else "image"

    if media_kind == "image":
        # Decode image and enforce pixel limit (decompression bomb protection)
        Image.MAX_IMAGE_PIXELS = settings.max_image_pixels
        try:
            with Image.open(io.BytesIO(file_bytes)) as img:
                img.verify()
            with Image.open(io.BytesIO(file_bytes)) as img:
                img = img.convert("RGB")
                width, height = img.size
                pixels = width * height
                if pixels > settings.max_image_pixels:
                    audit_event("upload_rejected", reason="too_many_pixels", pixels=pixels)
                    raise SecurityValidationError(
                        f"Image has {pixels} pixels",
                        user_message="Image resolution is too large. Please upload a smaller file.",
                    )
        except SecurityValidationError:
            raise
        except UnidentifiedImageError as exc:
            audit_event("upload_rejected", reason="decode_failed", hash=content_hash[:16])
            raise ImageProcessingError(str(exc)) from exc
        except Exception as exc:
            log.exception("Unexpected error decoding upload")
            audit_event("upload_rejected", reason="decode_error", hash=content_hash[:16])
            raise ImageProcessingError(str(exc)) from exc

    audit_event(
        "upload_validated",
        hash=content_hash[:16],
        ext=ext,
        size_kb=round(size / 1024, 1),
        dims=f"{width}x{height}" if media_kind == "image" else "pdf",
    )
    log.info(
        "Upload validated | hash=%s… | kind=%s | %d KB",
        content_hash[:12],
        media_kind,
        size // 1024,
    )

    return ValidatedUpload(
        safe_filename=safe_name,
        extension=ext,
        size_bytes=size,
        content_hash=content_hash,
        width=width,
        height=height,
        media_kind=media_kind,
    )


def load_image_from_bytes(file_bytes: bytes) -> Image.Image:
    """Decode validated bytes into a PIL RGB image."""
    try:
        return Image.open(io.BytesIO(file_bytes)).convert("RGB")
    except Exception as exc:
        raise ImageProcessingError(str(exc)) from exc


def redact_secrets(text: str) -> str:
    """
    Mask common PII patterns before writing to logs.
    Use when OCR or API responses are logged in future integrations.
    """
    # Mask 12-digit Aadhaar (with or without spaces)
    text = re.sub(r"\b\d{4}\s?\d{4}\s?\d{4}\b", "XXXX-XXXX-####", text)
    # Mask PAN: ABCDE1234F
    text = re.sub(r"\b[A-Z]{5}\d{4}[A-Z]\b", "XXXXX####X", text, flags=re.IGNORECASE)
    return text
