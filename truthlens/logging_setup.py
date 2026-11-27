"""
Logging setup for TruthLens.

Creates two log streams:
  1. truthlens.log  — general application/debug logs (rotating)
  2. audit.log      — security-relevant events only (uploads, verdicts, errors)

Never log raw document content, Aadhaar numbers, or API secrets.
"""

from __future__ import annotations

import logging
import sys
import uuid
from contextvars import ContextVar
from logging.handlers import RotatingFileHandler
from pathlib import Path

from truthlens.config import settings

# Correlates all log lines for one user analysis session
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    """Inject the current request/session id into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get("-")
        return True


def new_request_id() -> str:
    """Generate and store a short correlation id for one analysis run."""
    rid = uuid.uuid4().hex[:12]
    request_id_var.set(rid)
    return rid


def setup_logging() -> logging.Logger:
    """
    Configure root TruthLens logger. Safe to call multiple times (idempotent).
    Returns the main application logger.
    """
    log_dir: Path = settings.log_dir
    log_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("truthlens")
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, settings.log_level, logging.INFO))
    logger.propagate = False

    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | req=%(request_id)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    req_filter = RequestIdFilter()

    # Rotating file — general logs
    app_handler = RotatingFileHandler(
        log_dir / "truthlens.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    app_handler.setFormatter(fmt)
    app_handler.addFilter(req_filter)
    logger.addHandler(app_handler)

    # Console output for local development
    if settings.log_to_console:
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(fmt)
        console.addFilter(req_filter)
        logger.addHandler(console)

    # Separate audit logger — security and compliance events
    if settings.audit_log_enabled:
        audit = logging.getLogger("truthlens.audit")
        audit.setLevel(logging.INFO)
        audit.propagate = False
        if not audit.handlers:
            audit_handler = RotatingFileHandler(
                log_dir / "audit.log",
                maxBytes=5 * 1024 * 1024,
                backupCount=10,
                encoding="utf-8",
            )
            audit_handler.setFormatter(fmt)
            audit_handler.addFilter(req_filter)
            audit.addHandler(audit_handler)

    logger.info(
        "Logging initialized | level=%s | log_dir=%s",
        settings.log_level,
        log_dir,
    )
    return logger


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the truthlens namespace."""
    setup_logging()
    return logging.getLogger(f"truthlens.{name}")


def audit_event(event: str, **fields: object) -> None:
    """
    Write a structured audit line. Values must not contain PII.
    Example: audit_event("upload_validated", file_hash="abc123", size_kb=240)
    """
    setup_logging()
    audit = logging.getLogger("truthlens.audit")
    extras = " | ".join(f"{k}={v}" for k, v in fields.items())
    audit.info("%s | %s", event, extras if extras else "-")
