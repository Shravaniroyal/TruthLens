from types import SimpleNamespace

import truthlens.jobs as jobs
import truthlens.review as review


def _fake_case(name, label):
    return SimpleNamespace(
        filename=name,
        content_hash="a" * 64,
        doc_type="pan",
        analysis=SimpleNamespace(verdict=SimpleNamespace(label=label, confidence=90.0)),
        fields=SimpleNamespace(to_public_dict=lambda: {"pan": "XXXXX1234X"}),
        to_public_dict=lambda: {"filename": name, "verdict": label},
    )


def test_batch_job_queues_fake_not_real(tmp_path, monkeypatch):
    monkeypatch.setattr(jobs, "settings", SimpleNamespace(data_dir=tmp_path, retention_days=30))
    store = review.ReviewStore(tmp_path / "reviews")
    monkeypatch.setattr(review, "_default_store", store)

    labels = {"a.jpg": "FAKE", "b.jpg": "REAL"}
    monkeypatch.setattr(jobs, "analyze_document", lambda data, name, run_model=True: _fake_case(name, labels[name]))
    monkeypatch.setattr(
        jobs, "evaluate_workflow",
        lambda wf, types: SimpleNamespace(to_dict=lambda: {"complete": True}),
    )

    jobs._write({
        "job_id": "t1", "status": "queued", "workflow_id": "wf", "operator": "op",
        "case_id": "job-t1", "queued": 0, "results": [], "workflow": None, "error": None,
        "created_at": "2026-11-28T00:00:00+00:00",
    })
    jobs._run_job("t1", "wf", [("a.jpg", b"x"), ("b.jpg", b"y")])

    rec = jobs.get_job("t1")
    assert rec["status"] == "completed"
    assert rec["queued"] == 1
    items = store.list(case_id="job-t1")
    assert len(items) == 1
    assert items[0].filename == "a.jpg"
