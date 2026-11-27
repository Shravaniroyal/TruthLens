"""On-disk batch jobs and optional image retention cleanup."""

from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from truthlens.bgv import evaluate_workflow
from truthlens.config import settings
from truthlens.logging_setup import get_logger
from truthlens.pipeline import analyze_document

log = get_logger("jobs")
_lock = threading.Lock()


def _jobs_dir() -> Path:
    path = settings.data_dir / "jobs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _job_path(job_id: str) -> Path:
    return _jobs_dir() / f"{job_id}.json"


def create_job(workflow_id: str, operator: str, files: list[tuple[str, bytes]]) -> str:
    job_id = uuid.uuid4().hex[:12]
    record = {
        "job_id": job_id,
        "status": "queued",
        "workflow_id": workflow_id,
        "operator": operator,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "file_count": len(files),
        "results": [],
        "workflow": None,
        "error": None,
    }
    _write(record)
    thread = threading.Thread(
        target=_run_job,
        args=(job_id, workflow_id, files),
        daemon=True,
        name=f"truthlens-job-{job_id}",
    )
    thread.start()
    return job_id


def get_job(job_id: str) -> dict[str, Any] | None:
    path = _job_path(job_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write(record: dict[str, Any]) -> None:
    with _lock:
        _job_path(record["job_id"]).write_text(
            json.dumps(record, indent=2), encoding="utf-8"
        )


def _run_job(job_id: str, workflow_id: str, files: list[tuple[str, bytes]]) -> None:
    rec = get_job(job_id)
    if rec is None:
        return
    rec["status"] = "running"
    _write(rec)
    results: list[dict[str, Any]] = []
    types: list[str] = []
    try:
        for name, data in files:
            case = analyze_document(data, name, run_model=True)
            payload = case.to_public_dict()
            results.append(payload)
            types.append(case.doc_type)
            rec["results"] = results
            _write(rec)
        rec["workflow"] = evaluate_workflow(workflow_id, types).to_dict()
        rec["status"] = "completed"
        rec["completed_at"] = datetime.now(timezone.utc).isoformat()
        _write(rec)
        log.info("Job %s completed | files=%d", job_id, len(files))
    except Exception as exc:
        log.exception("Job %s failed", job_id)
        rec["status"] = "failed"
        rec["error"] = type(exc).__name__
        rec["results"] = results
        _write(rec)


def purge_old_jobs() -> int:
    """Delete job JSON older than retention_days. Does not keep uploaded bytes."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.retention_days)
    removed = 0
    for path in _jobs_dir().glob("*.json"):
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
            created = datetime.fromisoformat(rec.get("created_at", "1970-01-01+00:00"))
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            if created < cutoff:
                path.unlink(missing_ok=True)
                removed += 1
        except Exception:
            continue
    if removed:
        log.info("Retention purged %d job files", removed)
    return removed
