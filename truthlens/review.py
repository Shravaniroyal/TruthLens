"""
Reviewer queue for TruthLens (Phase 1).

FAKE / UNCERTAIN results are queued. A human reviewer marks each one
accepted / rejected / need_original, with their name and a timestamp.

Privacy: only masked fields, filename and content hash are stored.
Never pass full Aadhaar / PAN numbers into this module.
"""

from __future__ import annotations

import json
import re
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

REVIEW_LABELS = {"FAKE", "UNCERTAIN"}
DECISIONS = {"accepted", "rejected", "need_original"}
STATUSES = {"pending"} | DECISIONS
_ID_RE = re.compile(r"^[a-f0-9]{12}$")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def should_review(verdict_label: str) -> bool:
    return verdict_label.upper() in REVIEW_LABELS


@dataclass
class ReviewItem:
    id: str
    created_at: str
    filename: str
    content_hash: str
    doc_type: str
    verdict: str
    confidence: float
    fields_masked: dict[str, Any] = field(default_factory=dict)
    workflow: str = ""
    case_id: str = ""
    operator: str = ""
    status: str = "pending"
    reviewer: str = ""
    note: str = ""
    decided_at: str = ""


class ReviewStore:
    """One JSON file per item under `directory`."""

    def __init__(self, directory: Path) -> None:
        self.dir = Path(directory)
        self.dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _path(self, item_id: str) -> Path:
        if not _ID_RE.match(item_id):
            raise KeyError(item_id)
        return self.dir / f"{item_id}.json"

    def add(
        self,
        *,
        filename: str,
        content_hash: str,
        doc_type: str,
        verdict: str,
        confidence: float,
        fields_masked: dict[str, Any] | None = None,
        workflow: str = "",
        case_id: str = "",
        operator: str = "",
    ) -> ReviewItem:
        item = ReviewItem(
            id=uuid.uuid4().hex[:12],
            created_at=_now(),
            filename=filename,
            content_hash=content_hash,
            doc_type=doc_type,
            verdict=verdict.upper(),
            confidence=float(confidence),
            fields_masked=fields_masked or {},
            workflow=workflow,
            case_id=case_id,
            operator=operator,
        )
        with self._lock:
            self._write(item)
        return item

    def add_if_needed(self, verdict: str, **kwargs: Any) -> ReviewItem | None:
        """Queue only FAKE / UNCERTAIN results. Returns None for REAL."""
        if not should_review(verdict):
            return None
        return self.add(verdict=verdict, **kwargs)

    def get(self, item_id: str) -> ReviewItem:
        path = self._path(item_id)
        if not path.exists():
            raise KeyError(item_id)
        return ReviewItem(**json.loads(path.read_text(encoding="utf-8")))

    def list(self, status: str | None = None, case_id: str | None = None) -> list[ReviewItem]:
        items = []
        for p in sorted(self.dir.glob("*.json")):
            try:
                items.append(ReviewItem(**json.loads(p.read_text(encoding="utf-8"))))
            except Exception:
                continue
        if status:
            items = [i for i in items if i.status == status]
        if case_id:
            items = [i for i in items if i.case_id == case_id]
        return sorted(items, key=lambda i: i.created_at)

    def decide(self, item_id: str, decision: str, reviewer: str, note: str = "") -> ReviewItem:
        if decision not in DECISIONS:
            raise ValueError(f"decision must be one of {sorted(DECISIONS)}")
        if not reviewer.strip():
            raise ValueError("reviewer name is required")
        with self._lock:
            item = self.get(item_id)
            item.status = decision
            item.reviewer = reviewer.strip()
            item.note = note.strip()[:500]
            item.decided_at = _now()
            self._write(item)
        return item

    def _write(self, item: ReviewItem) -> None:
        tmp = self._path(item.id).with_suffix(".tmp")
        tmp.write_text(json.dumps(asdict(item), indent=2), encoding="utf-8")
        tmp.replace(self._path(item.id))


class DecisionBody(BaseModel):
    decision: str
    reviewer: str
    note: str = ""


def make_router(store: ReviewStore) -> APIRouter:
    router = APIRouter(prefix="/v1/reviews", tags=["review"])

    @router.get("")
    def list_reviews(status: str | None = None, case_id: str | None = None) -> dict[str, Any]:
        if status and status not in STATUSES:
            raise HTTPException(400, f"status must be one of {sorted(STATUSES)}")
        return {"items": [asdict(i) for i in store.list(status, case_id)]}

    @router.get("/{item_id}")
    def get_review(item_id: str) -> dict[str, Any]:
        try:
            return asdict(store.get(item_id))
        except KeyError:
            raise HTTPException(404, "review item not found")

    @router.post("/{item_id}/decision")
    def decide(item_id: str, body: DecisionBody) -> dict[str, Any]:
        try:
            return asdict(store.decide(item_id, body.decision, body.reviewer, body.note))
        except KeyError:
            raise HTTPException(404, "review item not found")
        except ValueError as exc:
            raise HTTPException(400, str(exc))

    return router


# --- shared store + helper used by the API and batch jobs ---
_default_store: ReviewStore | None = None


def get_store() -> ReviewStore:
    global _default_store
    if _default_store is None:
        from truthlens.config import settings

        _default_store = ReviewStore(settings.data_dir / "reviews")
    return _default_store


def queue_case(case: Any, *, workflow: str = "", case_id: str = "", operator: str = "") -> ReviewItem | None:
    """Queue a pipeline CaseResult if its verdict is FAKE or UNCERTAIN.
    Stores only masked fields. Returns None for REAL or when no model ran."""
    if case.analysis is None:
        return None
    v = case.analysis.verdict
    return get_store().add_if_needed(
        v.label,
        filename=case.filename,
        content_hash=case.content_hash[:16],
        doc_type=case.doc_type,
        confidence=v.confidence,
        fields_masked=case.fields.to_public_dict(),
        workflow=workflow,
        case_id=case_id,
        operator=operator,
    )
