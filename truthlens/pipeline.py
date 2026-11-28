"""
Product pipeline — one entry point for Streamlit and the REST API.

Does not retrain the model. Steps:
  validate → pages → quality → OCR → QR → fields → forensic model → official stub
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from PIL import Image

from truthlens.analyzer import AnalysisResult, analyze_image
from truthlens.bgv import slot_for_doc_type
from truthlens.doc_types import DOC_TYPE_LABELS, detect_doc_type
from truthlens.fields import ExtractedFields, extract_fields
from truthlens.logging_setup import audit_event, get_logger, new_request_id
from truthlens.ocr import ocr_image, ocr_log_safe
from truthlens.official import DISCLAIMER, OfficialResult, cross_verify
from truthlens.pdfio import load_pages
from truthlens.quality import QualityReport, assess_quality
from truthlens.qrscan import QrResult, scan_qr
from truthlens.security import ValidatedUpload, validate_upload

log = get_logger("pipeline")


@dataclass
class CaseResult:
    request_id: str
    filename: str
    content_hash: str
    page_count: int
    quality: QualityReport
    doc_type: str
    doc_type_label: str
    bgv_slot: str
    fields: ExtractedFields
    qr: QrResult
    qr_vs_ocr_mismatch: bool
    official: OfficialResult
    analysis: AnalysisResult | None
    elapsed_ms: float
    timings: dict[str, float] = field(default_factory=dict)
    ocr_available: bool = False

    def to_public_dict(self) -> dict[str, Any]:
        forensic: dict[str, Any] | None = None
        if self.analysis is not None:
            v = self.analysis.verdict
            forensic = {
                "verdict": v.label,
                "confidence": round(v.confidence, 2),
                "real_pct": round(v.real_pct, 2),
                "fake_pct": round(v.fake_pct, 2),
                "elapsed_ms": round(self.analysis.elapsed_ms, 1),
                "timings": {k: round(val, 1) for k, val in self.analysis.timings.items()},
            }
        return {
            "request_id": self.request_id,
            "filename": self.filename,
            "content_hash": self.content_hash[:16],
            "page_count": self.page_count,
            "quality": self.quality.to_dict(),
            "doc_type": self.doc_type,
            "doc_type_label": self.doc_type_label,
            "bgv_slot": self.bgv_slot,
            "fields": self.fields.to_public_dict(),
            "qr": self.qr.to_dict(),
            "qr_vs_ocr_mismatch": self.qr_vs_ocr_mismatch,
            "ocr_available": self.ocr_available,
            "forensic": forensic,
            "official": self.official.to_dict(),
            "elapsed_ms": round(self.elapsed_ms, 1),
            "disclaimer": DISCLAIMER,
        }


def _qr_mismatch(ocr_text: str, qr: QrResult, fields: ExtractedFields) -> bool:
    if not qr.found or not qr.payload:
        return False
    payload = qr.payload
    qr_fields = extract_fields(payload)
    if fields.pan_masked and qr_fields.pan_masked and fields.pan_masked != qr_fields.pan_masked:
        return True
    if (
        fields.aadhaar_masked
        and qr_fields.aadhaar_masked
        and fields.aadhaar_masked != qr_fields.aadhaar_masked
    ):
        return True
    # If OCR has a name and QR payload is long text without that name token
    if fields.name_guess and len(payload) > 8:
        token = fields.name_guess.split()[0]
        if len(token) > 3 and token.lower() not in payload.lower() and token.lower() not in (ocr_text or "").lower():
            return False
    return False


def analyze_document(
    file_bytes: bytes,
    original_filename: str,
    *,
    run_model: bool = True,
    request_id: str | None = None,
) -> CaseResult:
    """Full product analysis. Set run_model=False for OCR/QR-only tests."""
    t0 = time.perf_counter()
    timings: dict[str, float] = {}
    rid = request_id or new_request_id()

    validated: ValidatedUpload = validate_upload(file_bytes, original_filename)

    t = time.perf_counter()
    pages = load_pages(file_bytes, validated.media_kind)
    timings["load_pages_ms"] = (time.perf_counter() - t) * 1000
    primary: Image.Image = pages[0]

    t = time.perf_counter()
    quality = assess_quality(primary)
    timings["quality_ms"] = (time.perf_counter() - t) * 1000

    t = time.perf_counter()
    ocr_text = ocr_image(primary)
    qr = scan_qr(primary)
    timings["ocr_qr_ms"] = (time.perf_counter() - t) * 1000
    if ocr_text:
        log.debug("OCR text length=%d chars", len(ocr_text or ""))

    combined = f"{ocr_text} {qr.payload}".strip()
    fields = extract_fields(combined)
    doc_type = detect_doc_type(validated.safe_filename, combined)
    mismatch = _qr_mismatch(ocr_text, qr, fields)
    official = cross_verify(fields)

    analysis: AnalysisResult | None = None
    if run_model:
        t = time.perf_counter()
        analysis = analyze_image(primary)
        timings["forensic_ms"] = (time.perf_counter() - t) * 1000

    elapsed = (time.perf_counter() - t0) * 1000
    timings["total_ms"] = elapsed

    audit_event(
        "case_complete",
        request_id=rid,
        doc_type=doc_type,
        verdict=(analysis.verdict.label if analysis else "skipped"),
        official=official.status,
        hash=validated.content_hash[:16],
    )

    return CaseResult(
        request_id=rid,
        filename=validated.safe_filename,
        content_hash=validated.content_hash,
        page_count=len(pages),
        quality=quality,
        doc_type=doc_type,
        doc_type_label=DOC_TYPE_LABELS.get(doc_type, doc_type),
        bgv_slot=slot_for_doc_type(doc_type),
        fields=fields,
        qr=qr,
        qr_vs_ocr_mismatch=mismatch,
        official=official,
        analysis=analysis,
        elapsed_ms=elapsed,
        timings=timings,
        ocr_available=bool(ocr_text),
    )
