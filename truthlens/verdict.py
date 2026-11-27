"""
Verdict logic — converts model probabilities into actionable labels.

Three-class adaptive thresholding (tuned to reduce Indian doc false positives):
  FAKE       fake probability >= 85%
  REAL       real  probability >= 60%  (and fake < 85%)
  UNCERTAIN  everything else → route to manual review
"""

from __future__ import annotations

from dataclasses import dataclass

from truthlens.config import settings
from truthlens.logging_setup import get_logger

log = get_logger("verdict")


@dataclass(frozen=True)
class VerdictResult:
    label: str          # REAL | UNCERTAIN | FAKE
    confidence: float   # Display confidence % for the chosen label
    real_pct: float
    fake_pct: float


def get_verdict(real_prob: float, fake_prob: float) -> VerdictResult:
    """
    Apply adaptive thresholds from settings and return a VerdictResult.

    Args:
        real_prob: Probability document is authentic  [0, 1]
        fake_prob: Probability document is tampered [0, 1]
    """
    real_pct = real_prob * 100
    fake_pct = fake_prob * 100

    if fake_pct >= settings.threshold_fake * 100:
        label, conf = "FAKE", fake_pct
    elif real_pct >= settings.threshold_real * 100:
        label, conf = "REAL", real_pct
    else:
        label, conf = "UNCERTAIN", max(fake_pct, real_pct)

    log.info(
        "Verdict=%s | real=%.1f%% | fake=%.1f%% | thresholds(real=%.0f%%, fake=%.0f%%)",
        label,
        real_pct,
        fake_pct,
        settings.threshold_real * 100,
        settings.threshold_fake * 100,
    )

    return VerdictResult(
        label=label,
        confidence=conf,
        real_pct=real_pct,
        fake_pct=fake_pct,
    )
