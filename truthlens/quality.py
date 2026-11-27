"""Capture-quality gates for camera / WhatsApp scans."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image

from truthlens.config import settings


@dataclass(frozen=True)
class QualityReport:
    blur_variance: float
    mean_brightness: float
    is_blurry: bool
    is_glare: bool
    is_too_dark: bool
    usable: bool
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "blur_variance": round(self.blur_variance, 1),
            "mean_brightness": round(self.mean_brightness, 1),
            "is_blurry": self.is_blurry,
            "is_glare": self.is_glare,
            "is_too_dark": self.is_too_dark,
            "usable": self.usable,
            "warnings": list(self.warnings),
        }


def assess_quality(img: Image.Image) -> QualityReport:
    rgb = np.array(img.convert("RGB"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    blur_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    mean_b = float(gray.mean())

    warnings: list[str] = []
    is_blurry = blur_var < settings.blur_min_variance
    is_glare = mean_b > 245
    is_too_dark = mean_b < 25

    if is_blurry:
        warnings.append("Image looks blurry — retake with a steady camera.")
    if is_glare:
        warnings.append("Possible glare / overexposure — avoid flash on plastic cards.")
    if is_too_dark:
        warnings.append("Image is too dark — use even lighting.")

    usable = not (is_blurry and is_too_dark)
    return QualityReport(
        blur_variance=blur_var,
        mean_brightness=mean_b,
        is_blurry=is_blurry,
        is_glare=is_glare,
        is_too_dark=is_too_dark,
        usable=usable,
        warnings=tuple(warnings),
    )
