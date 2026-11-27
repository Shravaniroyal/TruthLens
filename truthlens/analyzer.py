"""
Analysis pipeline — orchestrates the full fraud detection flow.

Steps:
  1. Preprocess image (resize, normalize)
  2. Grad-CAM inference → fake probability + heatmap
  3. Build overlay visualization arrays
  4. Apply verdict thresholds

All steps are timed and logged for debugging and performance monitoring.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from PIL import Image

from truthlens.config import settings
from truthlens.exceptions import AnalysisError
from truthlens.gradcam import compute_gradcam
from truthlens.logging_setup import audit_event, get_logger
from truthlens.model import load_model
from truthlens.verdict import VerdictResult, get_verdict

log = get_logger("analyzer")


def _build_transform() -> transforms.Compose:
    """ImageNet normalization — must match training preprocessing."""
    return transforms.Compose([
        transforms.Resize((settings.img_size, settings.img_size)),
        transforms.ToTensor(),
        transforms.Normalize(settings.imagenet_mean, settings.imagenet_std),
    ])


TRANSFORM = _build_transform()


@dataclass
class AnalysisResult:
    """Complete output of one document analysis run."""

    verdict: VerdictResult
    real_prob: float
    fake_prob: float
    img_np: np.ndarray          # Original resized RGB array for display
    heatmap: np.ndarray         # JET colormap heatmap
    overlay: np.ndarray         # Blended original + heatmap
    gradcam: np.ndarray         # Raw Grad-CAM [0, 1]
    elapsed_ms: float
    timings: dict[str, float] = field(default_factory=dict)


def analyze_image(img_pil: Image.Image) -> AnalysisResult:
    """
    Run the full TruthLens analysis pipeline on a PIL image.

    Raises AnalysisError if inference fails.
    """
    t_total = time.perf_counter()
    timings: dict[str, float] = {}

    try:
        model, device = load_model()

        # ── Step 1: Preprocess ───────────────────────────────────────────────
        t0 = time.perf_counter()
        img_rgb = img_pil.convert("RGB").resize((settings.img_size, settings.img_size))
        img_np = np.array(img_rgb)
        tensor = TRANSFORM(img_rgb).unsqueeze(0)
        timings["preprocess_ms"] = (time.perf_counter() - t0) * 1000
        log.debug("Preprocess done in %.1f ms", timings["preprocess_ms"])

        # ── Step 2: Grad-CAM inference ───────────────────────────────────────
        t0 = time.perf_counter()
        with torch.enable_grad():
            cam, fake_prob = compute_gradcam(model, tensor, device)
        timings["inference_ms"] = (time.perf_counter() - t0) * 1000
        log.info("Inference done in %.1f ms | fake_prob=%.4f", timings["inference_ms"], fake_prob)

        real_prob = 1.0 - fake_prob

        # ── Step 3: Build visualization arrays ───────────────────────────────
        t0 = time.perf_counter()
        heatmap_bgr = cv2.applyColorMap((cam * 255).astype(np.uint8), cv2.COLORMAP_JET)
        heatmap = cv2.cvtColor(heatmap_bgr, cv2.COLOR_BGR2RGB)
        overlay = np.clip(0.55 * img_np + 0.45 * heatmap, 0, 255).astype(np.uint8)
        timings["visualize_ms"] = (time.perf_counter() - t0) * 1000

        # ── Step 4: Verdict ──────────────────────────────────────────────────
        verdict = get_verdict(real_prob, fake_prob)

        elapsed_ms = (time.perf_counter() - t_total) * 1000
        timings["total_ms"] = elapsed_ms

        audit_event(
            "analysis_complete",
            verdict=verdict.label,
            fake_pct=round(verdict.fake_pct, 1),
            elapsed_ms=round(elapsed_ms, 0),
        )
        log.info(
            "Analysis complete | verdict=%s | total=%.0f ms | breakdown=%s",
            verdict.label,
            elapsed_ms,
            {k: round(v, 1) for k, v in timings.items()},
        )

        return AnalysisResult(
            verdict=verdict,
            real_prob=real_prob,
            fake_prob=fake_prob,
            img_np=img_np,
            heatmap=heatmap,
            overlay=overlay,
            gradcam=cam,
            elapsed_ms=elapsed_ms,
            timings=timings,
        )

    except Exception as exc:
        log.exception("Analysis pipeline failed")
        audit_event("analysis_failed", error=type(exc).__name__)
        if hasattr(exc, "user_message"):
            raise
        raise AnalysisError(str(exc)) from exc
