"""
Forensic explainer — human-readable fraud reasons for Indian documents.

Combines three signals per document zone (field region):
  1. Grad-CAM heatmap  (40%) — where the CNN focused
  2. ELA map           (38%) — JPEG re-compression artifacts
  3. Noise map         (22%) — local pixel noise inconsistencies

Zone layouts are defined per doc type (Aadhaar / PAN / DL / generic).
Each zone maps to pre-written forensic reason templates.
"""

from __future__ import annotations

import io

import cv2
import numpy as np
from PIL import Image, ImageChops

from truthlens.logging_setup import get_logger

log = get_logger("forensic")

# Normalized bounding boxes (x1, y1, x2, y2) as fractions of image size
ZONES: dict[str, dict[str, tuple[float, float, float, float]]] = {
    "aadhaar": {
        "header": (0, 0.00, 1, 0.18),
        "photo": (0, 0.18, 0.23, 0.65),
        "name_field": (0.23, 0.18, 0.75, 0.35),
        "dob_field": (0.23, 0.35, 0.75, 0.50),
        "address_field": (0.23, 0.50, 0.75, 0.78),
        "uid_number": (0, 0.78, 1, 1),
        "qr_code": (0.75, 0.18, 1, 0.78),
    },
    "pan": {
        "header": (0, 0.00, 1, 0.18),
        "pan_number": (0, 0.18, 0.78, 0.34),
        "photo": (0, 0.34, 0.23, 0.72),
        "name_field": (0.23, 0.34, 0.78, 0.50),
        "father_name": (0.23, 0.50, 0.78, 0.64),
        "dob_field": (0.23, 0.64, 0.78, 0.80),
        "signature": (0.23, 0.80, 0.78, 0.92),
        "qr_code": (0.78, 0.18, 1, 0.92),
    },
    "dl": {
        "header": (0, 0.00, 1, 0.18),
        "dl_number": (0.23, 0.18, 0.78, 0.32),
        "photo": (0, 0.18, 0.23, 0.68),
        "name_field": (0.23, 0.32, 0.78, 0.46),
        "dob_field": (0.23, 0.46, 0.78, 0.58),
        "validity": (0.23, 0.58, 0.78, 0.70),
        "vehicle_class": (0.23, 0.70, 0.78, 0.84),
        "qr_code": (0.78, 0.18, 1, 0.84),
    },
    "generic": {
        "header": (0, 0.00, 1, 0.18),
        "photo": (0, 0.18, 0.23, 0.65),
        "name_field": (0.23, 0.18, 1, 0.34),
        "id_number": (0, 0.65, 1, 0.80),
        "date_field": (0.23, 0.34, 0.75, 0.50),
        "address_field": (0.23, 0.50, 1, 0.65),
        "signature": (0, 0.80, 1, 1),
    },
}

LABELS: dict[str, str] = {
    "header": "document header / issuing authority",
    "photo": "photograph area",
    "name_field": "name field",
    "dob_field": "date of birth field",
    "uid_number": "12-digit Aadhaar number",
    "pan_number": "PAN number",
    "dl_number": "driving licence number",
    "father_name": "father name field",
    "id_number": "ID number",
    "date_field": "date field",
    "address_field": "address field",
    "signature": "signature area",
    "qr_code": "QR code region",
    "validity": "validity dates",
    "vehicle_class": "vehicle class field",
}

REASONS: dict[str, list[str]] = {
    "name_field": [
        "Name field shows font inconsistency — characters appear from a different typeface than surrounding text.",
        "Pixel sharpness in the name area is abnormally high — text was likely digitally typed over the original.",
        "JPEG compression artifacts in the name field differ from the rest of the document.",
    ],
    "uid_number": [
        "12-digit Aadhaar number shows digit-level pixel inconsistency — stroke widths differ between digits.",
        "ELA map shows elevated error levels on the UID row — re-compression artifacts indicate modification.",
    ],
    "pan_number": [
        "PAN number character spacing is non-uniform — single character alteration is the most common PAN fraud pattern.",
        "ELA isolates the PAN number as highest-anomaly region.",
    ],
    "photo": [
        "Photograph boundary shows compression discontinuity — photo JPEG signature differs from document background.",
        "Noise texture at photo edges does not blend naturally — photograph was composited onto the document.",
    ],
    "dob_field": [
        "Date of birth field has high ELA score — re-saving artifacts indicate this date was modified.",
        "Text anti-aliasing in the DOB area differs from other printed text.",
    ],
    "dl_number": [
        "Driving licence number shows re-compression artifacts inconsistent with state transport printing.",
    ],
    "father_name": [
        "Father name field shows different font-rendering than the name field above.",
    ],
    "header": [
        "Document header anomaly — government logo or authority text may have been modified.",
    ],
    "address_field": [
        "Address field has localized compression anomaly — certain lines have different JPEG history.",
    ],
    "signature": [
        "Signature boundary shows artifacts inconsistent with authentic ink scanning.",
    ],
    "validity": [
        "Validity dates have elevated ELA score — the Valid Till date may have been extended.",
    ],
    "id_number": [
        "ID number region shows pixel-level manipulation consistent with digit replacement.",
    ],
}


def run_ela(pil_image: Image.Image, quality: int = 90) -> tuple[np.ndarray, Image.Image]:
    """
    Error Level Analysis — re-save at given JPEG quality and diff against original.
    Bright regions in the output indicate areas with different compression history.
    """
    orig = pil_image.convert("RGB")
    buf = io.BytesIO()
    orig.save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    resaved = Image.open(buf).convert("RGB")
    diff = ImageChops.difference(orig, resaved)
    diff_arr = np.array(diff, dtype=np.float32)
    mx = diff_arr.max()
    scaled = (
        np.clip(diff_arr * (255.0 / mx), 0, 255).astype(np.uint8)
        if mx > 0
        else diff_arr.astype(np.uint8)
    )
    return scaled.astype(np.float32), Image.fromarray(scaled)


def run_noise_map(pil_image: Image.Image) -> np.ndarray:
    """Local noise variance map — edited regions often have different noise texture."""
    gray = np.array(pil_image.convert("L"), dtype=np.float32)
    smooth = cv2.medianBlur(gray.astype(np.uint8), 5).astype(np.float32)
    noise = np.abs(gray - smooth)
    return cv2.GaussianBlur(noise**2, (21, 21), 0)


def _zone_score(arr2d: np.ndarray, zones_dict: dict, w: int, h: int) -> dict[str, float]:
    """Average signal value inside each normalized zone bounding box."""
    scores: dict[str, float] = {}
    for name, (x1f, y1f, x2f, y2f) in zones_dict.items():
        region = arr2d[int(y1f * h): int(y2f * h), int(x1f * w): int(x2f * w)]
        scores[name] = float(region.mean()) if region.size > 0 else 0.0
    return scores


def _norm(d: dict[str, float]) -> dict[str, float]:
    """Normalize score dict to [0, 1] relative to the max value."""
    mx = max(d.values()) if d and max(d.values()) > 0 else 1.0
    return {k: v / mx for k, v in d.items()}


def explain_fraud(
    pil_image: Image.Image,
    gradcam_heatmap_np: np.ndarray | None = None,
    doc_type: str = "generic",
    confidence: float = 0.99,
) -> tuple[list[str], Image.Image, dict]:
    """
    Generate human-readable fraud reasons for a flagged document.

    Returns:
        reasons:  Markdown strings for Streamlit display
        ela_pil:  ELA visualization image
        debug:    Raw zone scores (for logging / future API response)
    """
    w, h = pil_image.size
    zones = ZONES.get(doc_type, ZONES["generic"])
    log.info("Running forensic explainer | doc_type=%s | size=%dx%d", doc_type, w, h)

    ela_arr, ela_pil = run_ela(pil_image)
    noise_map = run_noise_map(pil_image)
    ela_mean = ela_arr.mean(axis=2) if ela_arr.ndim == 3 else ela_arr

    ela_scores = _zone_score(ela_mean, zones, w, h)
    nse_scores = _zone_score(noise_map, zones, w, h)

    gc_scores: dict[str, float] = {}
    if gradcam_heatmap_np is not None:
        hmap = cv2.resize(gradcam_heatmap_np.astype(np.float32), (w, h))
        gc_scores = _zone_score(hmap, zones, w, h)

    ela_n = _norm(ela_scores)
    nse_n = _norm(nse_scores)
    gc_n = _norm(gc_scores) if gc_scores else {z: 0.0 for z in zones}

    # Weighted fusion across the three forensic signals
    composite = {
        z: 0.40 * gc_n.get(z, 0) + 0.38 * ela_n.get(z, 0) + 0.22 * nse_n.get(z, 0)
        for z in zones
    }
    top_zones = sorted(composite.items(), key=lambda x: -x[1])

    reasons: list[str] = []
    pct = confidence * 100
    reasons.append(
        f"⚠️ **Model confidence: {pct:.1f}% FAKE** — "
        f"{'Very high' if pct >= 99 else 'High'} certainty of tampering."
    )

    used: set[str] = set()
    for zone_name, score in top_zones:
        if score < 0.12 or len(reasons) >= 5:
            break
        label = LABELS.get(zone_name, zone_name.replace("_", " ").title())
        templates = REASONS.get(zone_name, [])
        ela_val = ela_scores.get(zone_name, 0)
        ela_hi = ela_n.get(zone_name, 0) > 0.60
        gc_hi = gc_n.get(zone_name, 0) > 0.60

        if not templates:
            reasons.append(
                f"🔴 **Anomaly in {label}**: Region shows patterns inconsistent "
                f"with authentic documents. (ELA: {ela_val:.1f})"
            )
        else:
            idx = min(2 if (ela_hi and gc_hi) else 1 if ela_hi else 0, len(templates) - 1)
            icon = "🔴" if (ela_hi or gc_hi) else "🟡"
            sev = "**Primary tampering**" if zone_name not in used else "**Secondary anomaly**"
            ela_lv = (
                "very high — strong copy-paste" if ela_val > 30
                else "high — likely modified" if ela_val > 18
                else "moderate"
            )
            reasons.append(
                f"{icon} {sev} — **{label.title()}**: {templates[idx]} "
                f"*(ELA: {ela_val:.1f} — {ela_lv})*"
            )
        used.add(zone_name)

    if len(reasons) <= 1:
        reasons.append(
            "🔴 **Overall document structure anomaly**: Pixel statistics differ "
            "significantly from authentic documents of this type."
        )

    log.info(
        "Forensic explainer done | top_zone=%s | score=%.3f | reasons=%d",
        top_zones[0][0] if top_zones else "none",
        top_zones[0][1] if top_zones else 0,
        len(reasons),
    )

    debug = {
        "ela": ela_scores,
        "noise": nse_scores,
        "gradcam": gc_scores,
        "composite": composite,
    }
    return reasons, ela_pil, debug


def ela_to_pil(pil_image: Image.Image, quality: int = 90) -> Image.Image:
    """Convenience wrapper — return only the ELA visualization image."""
    _, ela_pil = run_ela(pil_image, quality=quality)
    return ela_pil
