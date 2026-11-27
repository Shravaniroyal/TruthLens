"""
OCR helper. Uses Tesseract when installed; otherwise returns empty text
and the rest of the pipeline (QR, filename, visual model) still runs.

Use ocr_status() to find out whether OCR is really available, so callers
can show a visible warning instead of failing silently.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

from PIL import Image

from truthlens.logging_setup import get_logger
from truthlens.security import redact_secrets

log = get_logger("ocr")

_WINDOWS_DEFAULT = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
_status_cache: dict | None = None
_warned = False

OCR_WARNING = (
    "OCR is unavailable (Tesseract not found). Document type, field extraction "
    "and QR-vs-text matching are limited; results rely on filename and the visual model only."
)


def _configure_tesseract_path(pytesseract) -> None:
    custom = os.environ.get("TRUTHLENS_TESSERACT_CMD", "").strip()
    if custom and Path(custom).exists():
        pytesseract.pytesseract.tesseract_cmd = custom
    elif not shutil.which("tesseract") and _WINDOWS_DEFAULT.exists():
        pytesseract.pytesseract.tesseract_cmd = str(_WINDOWS_DEFAULT)


def ocr_status(refresh: bool = False) -> dict:
    """Return {"available": bool, "version": str|None, "warning": str|None}."""
    global _status_cache
    if _status_cache is not None and not refresh:
        return _status_cache
    try:
        import pytesseract
    except ImportError:
        _status_cache = {
            "available": False,
            "version": None,
            "warning": OCR_WARNING + " (pytesseract package not installed)",
        }
        return _status_cache
    _configure_tesseract_path(pytesseract)
    try:
        version = str(pytesseract.get_tesseract_version())
        _status_cache = {"available": True, "version": version, "warning": None}
    except Exception as exc:
        _status_cache = {
            "available": False,
            "version": None,
            "warning": f"{OCR_WARNING} ({type(exc).__name__})",
        }
    return _status_cache


def ocr_image(img: Image.Image) -> str:
    global _warned
    status = ocr_status()
    if not status["available"]:
        if not _warned:
            log.warning(status["warning"])
            _warned = True
        return ""
    import pytesseract

    try:
        text = pytesseract.image_to_string(img.convert("RGB")) or ""
    except Exception as exc:
        log.warning("OCR failed on this image (%s)", type(exc).__name__)
        return ""
    return text.strip()


def ocr_log_safe(text: str) -> str:
    return redact_secrets(text[:500] if text else "")