"""
Official cross-verification adapter.

Live government / Setu calls are NOT made until keys exist.
The forensic model is never retrained from this module.
"""

from __future__ import annotations

from dataclasses import dataclass

from truthlens.config import settings
from truthlens.fields import ExtractedFields
from truthlens.logging_setup import get_logger

log = get_logger("official")

DISCLAIMER = (
    "Visual forensic screening is not a legal identity certificate. "
    "Official cross-check stays disconnected until licensed API keys are configured."
)


@dataclass(frozen=True)
class OfficialResult:
    status: str
    provider: str
    message: str
    matched: bool | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "provider": self.provider,
            "message": self.message,
            "matched": self.matched,
            "disclaimer": DISCLAIMER,
        }


def cross_verify(fields: ExtractedFields) -> OfficialResult:
    """
    Stub official check. When SETU_CLIENT_ID is empty → not_configured.
    When keys exist, still no network call until a real adapter is enabled.
    """
    has_keys = bool(settings.setu_client_id and settings.setu_client_secret)
    if not has_keys:
        log.info("Official verify skipped | status=not_configured")
        return OfficialResult(
            status="not_configured",
            provider="setu",
            message=(
                "Official API keys are not set. Forensic AI + OCR/QR still ran. "
                "Add SETU_CLIENT_ID and SETU_CLIENT_SECRET later — the model will not be retrained."
            ),
            matched=None,
        )

    log.info("Official keys present | env=%s | live adapter not enabled", settings.setu_env)
    return OfficialResult(
        status="keys_present_stub",
        provider="setu",
        message=(
            f"Setu credentials loaded (env={settings.setu_env}) but live HTTP verify is "
            "disabled until sandbox onboarding is complete. Fields were not sent to any government API."
        ),
        matched=None,
    )
