"""
Central configuration for TruthLens.

Reads from environment variables when set; falls back to sensible defaults.
Use a `.env` file locally (see `.env.example`) — never commit secrets to git.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# Project root = parent of the `truthlens/` package directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load `.env` early so every module sees the same settings (API keys stay out of code).
try:
    from dotenv import load_dotenv

    load_dotenv(PROJECT_ROOT / ".env")
except ImportError:
    pass


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    """Immutable runtime settings — loaded once at startup."""

    # ── Paths ────────────────────────────────────────────────────────────────
    project_root: Path = PROJECT_ROOT
    model_path: Path = field(
        default_factory=lambda: Path(
            os.getenv(
                "TRUTHLENS_MODEL_PATH",
                str(PROJECT_ROOT / "models" / "best_truthlens_v4.pth"),
            )
        )
    )
    log_dir: Path = field(
        default_factory=lambda: Path(
            os.getenv("TRUTHLENS_LOG_DIR", str(PROJECT_ROOT / "logs"))
        )
    )

    # ── Model / inference ────────────────────────────────────────────────────
    img_size: int = int(os.getenv("TRUTHLENS_IMG_SIZE", "224"))
    imagenet_mean: tuple[float, float, float] = (0.485, 0.456, 0.406)
    imagenet_std: tuple[float, float, float] = (0.229, 0.224, 0.225)

    # Verdict thresholds (adaptive 3-class — tuned for Indian doc FPR)
    threshold_fake: float = float(os.getenv("TRUTHLENS_THRESHOLD_FAKE", "0.85"))
    threshold_real: float = float(os.getenv("TRUTHLENS_THRESHOLD_REAL", "0.60"))

    # ── Security / upload limits ─────────────────────────────────────────────
    max_upload_bytes: int = int(os.getenv("TRUTHLENS_MAX_UPLOAD_MB", "10")) * 1024 * 1024
    max_image_pixels: int = int(os.getenv("TRUTHLENS_MAX_IMAGE_PIXELS", "25000000"))
    allowed_extensions: frozenset[str] = frozenset(
        ext.strip().lower()
        for ext in os.getenv(
            "TRUTHLENS_ALLOWED_EXTENSIONS",
            "jpg,jpeg,png,bmp,tiff,webp,pdf",
        ).split(",")
    )
    max_pdf_pages: int = int(os.getenv("TRUTHLENS_MAX_PDF_PAGES", "10"))

    # ── Product / API ────────────────────────────────────────────────────────
    api_key: str = os.getenv("TRUTHLENS_API_KEY", "")
    data_dir: Path = field(
        default_factory=lambda: Path(
            os.getenv("TRUTHLENS_DATA_DIR", str(PROJECT_ROOT / "data"))
        )
    )
    retention_days: int = int(os.getenv("TRUTHLENS_RETENTION_DAYS", "7"))
    blur_min_variance: float = float(os.getenv("TRUTHLENS_BLUR_MIN_VAR", "50"))

    # ── Logging ──────────────────────────────────────────────────────────────
    log_level: str = os.getenv("TRUTHLENS_LOG_LEVEL", "INFO").upper()
    log_to_console: bool = _env_bool("TRUTHLENS_LOG_CONSOLE", True)
    audit_log_enabled: bool = _env_bool("TRUTHLENS_AUDIT_LOG", True)

    # ── Future gov API placeholders (load from env when you get access) ─────
    setu_client_id: str = os.getenv("SETU_CLIENT_ID", "")
    setu_client_secret: str = os.getenv("SETU_CLIENT_SECRET", "")
    setu_env: str = os.getenv("SETU_ENV", "sandbox")  # sandbox | production

    # ── App metadata ─────────────────────────────────────────────────────────
    app_version: str = "5.0.0"
    model_version: str = "v4"


# Singleton used across the application
settings = Settings()
