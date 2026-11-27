"""QR / barcode payload read via OpenCV (no extra decoder binary)."""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image


@dataclass(frozen=True)
class QrResult:
    found: bool
    payload: str
    payload_preview: str

    def to_dict(self) -> dict[str, object]:
        return {
            "found": self.found,
            "payload_preview": self.payload_preview,
        }


def _preview(payload: str, limit: int = 80) -> str:
    if not payload:
        return ""
    cleaned = payload.replace("\n", " ")
    return cleaned[:limit] + ("…" if len(cleaned) > limit else "")


def scan_qr(img: Image.Image) -> QrResult:
    rgb = np.array(img.convert("RGB"))
    detector = cv2.QRCodeDetector()
    data, _, _ = detector.detectAndDecode(rgb)
    if data:
        return QrResult(found=True, payload=data, payload_preview=_preview(data))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    data, _, _ = detector.detectAndDecode(gray)
    if data:
        return QrResult(found=True, payload=data, payload_preview=_preview(data))
    return QrResult(found=False, payload="", payload_preview="")
