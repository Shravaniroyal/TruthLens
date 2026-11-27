"""Render PDF pages to RGB images without system Poppler (pypdfium2)."""

from __future__ import annotations

from PIL import Image

from truthlens.config import settings
from truthlens.exceptions import ImageProcessingError
from truthlens.logging_setup import get_logger

log = get_logger("pdfio")


def render_pdf_pages(file_bytes: bytes) -> list[Image.Image]:
    try:
        import pypdfium2 as pdfium
    except ImportError as exc:
        raise ImageProcessingError(
            "pypdfium2 is required for PDF support",
            user_message="PDF support is not installed. Run: pip install pypdfium2",
        ) from exc

    try:
        pdf = pdfium.PdfDocument(file_bytes)
    except Exception as exc:
        raise ImageProcessingError(
            str(exc),
            user_message="Could not read this PDF. Export pages as JPG/PNG or try another file.",
        ) from exc

    n = len(pdf)
    if n == 0:
        raise ImageProcessingError("Empty PDF", user_message="The PDF has no pages.")
    limit = min(n, settings.max_pdf_pages)
    if n > settings.max_pdf_pages:
        log.info("PDF has %d pages; rendering first %d", n, settings.max_pdf_pages)

    pages: list[Image.Image] = []
    try:
        for i in range(limit):
            page = pdf[i]
            bitmap = page.render(scale=2)
            pil = bitmap.to_pil().convert("RGB")
            pages.append(pil)
            page.close()
    finally:
        pdf.close()
    return pages


def load_pages(file_bytes: bytes, media_kind: str) -> list[Image.Image]:
    if media_kind == "pdf":
        return render_pdf_pages(file_bytes)
    from truthlens.security import load_image_from_bytes

    return [load_image_from_bytes(file_bytes)]
