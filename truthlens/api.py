"""FastAPI product API — same pipeline as Streamlit. Model is not retrained."""

from __future__ import annotations


from contextlib import asynccontextmanager

from typing import Any

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, UploadFile
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from truthlens import __version__
from truthlens.bgv import WORKFLOWS, evaluate_workflow
from truthlens.config import settings
from truthlens.exceptions import AuthError, TruthLensError
from truthlens.jobs import create_job, get_job, purge_old_jobs
from truthlens.review import purge_old_reviews
from truthlens.logging_setup import setup_logging
from truthlens.official import DISCLAIMER, cross_verify
from truthlens.fields import ExtractedFields
from truthlens.pipeline import analyze_document
from truthlens.review import ReviewStore, make_router

setup_logging()


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = settings.api_key
    if not expected:
        return
    if x_api_key != expected:
        raise HTTPException(status_code=401, detail=AuthError.user_message)


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        settings.data_dir.mkdir(parents=True, exist_ok=True)
        purge_old_jobs()
    purge_old_reviews()
        yield

    app = FastAPI(
        
        title="TruthLens API",
        version=__version__,
        description=(
            "Document forensic screening + OCR/QR + BGV checklists. "
            "Official government verify is a stub until API keys are added."
            
        ),
        lifespan=lifespan,
    )

    review_store = ReviewStore(settings.data_dir / "reviews")
    app.include_router(make_router(review_store))

    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost", "http://127.0.0.1", "http://localhost:8501"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


    @app.get("/health")
    def health() -> dict[str, Any]:
        official = cross_verify(ExtractedFields())
        return {
            "ok": True,
            "version": __version__,
            "model_version": settings.model_version,
            "official_status": official.status,
            "disclaimer": DISCLAIMER,
        }

    @app.get("/v1/workflows")
    def list_workflows(_: None = Depends(require_api_key)) -> dict[str, Any]:
        return {
            "workflows": {
                k: {"label": v["label"], "required": v["required"], "optional": v["optional"]}
                for k, v in WORKFLOWS.items()
            }
        }

    @app.post("/v1/analyze")
    async def analyze(
        file: UploadFile = File(...),
        _: None = Depends(require_api_key),
    ) -> dict[str, Any]:
        data = await file.read()
        name = file.filename or "upload.jpg"
        try:
            case = analyze_document(data, name, run_model=True)
        except TruthLensError as exc:
            raise HTTPException(status_code=400, detail=exc.user_message) from exc
        return case.to_public_dict()

    @app.post("/v1/batch")
    async def batch(
        files: list[UploadFile] = File(...),
        workflow_id: str = Form("job_joining"),
        operator: str = Form("anonymous"),
        _: None = Depends(require_api_key),
    ) -> dict[str, Any]:
        if workflow_id not in WORKFLOWS:
            raise HTTPException(status_code=400, detail="Unknown workflow_id")
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded")
        packed: list[tuple[str, bytes]] = []
        for item in files:
            packed.append((item.filename or "upload.jpg", await item.read()))
        job_id = create_job(workflow_id, operator, packed)
        return {"job_id": job_id, "status": "queued", "file_count": len(packed)}

    @app.get("/v1/jobs/{job_id}")
    def job_status(job_id: str, _: None = Depends(require_api_key)) -> dict[str, Any]:
        rec = get_job(job_id)
        if rec is None:
            raise HTTPException(status_code=404, detail="Job not found")
        return rec

    class BgvPreviewIn(BaseModel):
        workflow_id: str
        doc_types: list[str]

    @app.post("/v1/bgv/preview")
    def bgv_preview(body: BgvPreviewIn, _: None = Depends(require_api_key)) -> dict[str, Any]:
        try:
            return evaluate_workflow(body.workflow_id, body.doc_types).to_dict()
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("truthlens.api:app", host="0.0.0.0", port=8000, reload=False)
