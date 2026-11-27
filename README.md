# TruthLens v5.0.0

Document forensic screening for Indian colleges and employers: a visual tamper-detection model (EfficientNet-B4) combined with OCR, QR checks, and background-verification (BGV) checklists, available as a Streamlit app and a REST API.

> **Important disclaimer**
> TruthLens is a **visual tamper-screening and document-triage tool**. It answers one question: *does this image look edited?* It does **not** verify that an Aadhaar, PAN, marksheet or any other document is genuine, and it is **not** legal KYC, UIDAI eKYC, or an official verification service. Always confirm important documents with the issuing authority. Official-source verification (DigiLocker / Setu) is a stub and is **not enabled**.

---

## What it does

| Layer | Question it answers | Status |
|---|---|---|
| Forensic model (EfficientNet-B4 v4) + Grad-CAM + ELA | Was this image edited? | Complete |
| OCR + QR + field extraction | What document is it, and does the QR match the printed text? | Working (needs Tesseract) |
| BGV checklists | Is the document kit complete for this workflow? | Working |
| Official source check | Does an issuing authority agree? | **Stub, `not_configured`** |

**Verdict logic** (`truthlens/verdict.py`): `FAKE` if fake probability is 85% or higher, `REAL` if real probability is 60% or higher, otherwise `UNCERTAIN`. A `REAL` verdict means "no tampering detected", not "this document is genuine".

**Reported accuracy:** about 98% on the held-out test set for **tamper detection**. Print-scan, WhatsApp-compressed and glare-affected photos have not yet been stress-tested.

## Features

- Single-document analysis with Grad-CAM heatmap and ELA-based explanations
- Batch BGV workflows: `college_admission`, `job_joining`, `vendor_kyc`
- PDF support (pages are analysed individually)
- OCR (Tesseract), QR scanning, and masked PAN / Aadhaar / DL field extraction
- Aadhaar Verhoeff checksum check
- Upload validation (extension, magic bytes), rotating logs, audit log, redaction of IDs in logs
- REST API with optional API-key auth
- Synthetic Indian document generators (research only, not real IDs)

## Quick start

**Requirements:** Python 3.10, [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) (recommended), Git.

```powershell
git clone https://github.com/Shravaniroyal/TruthLens.git
cd TruthLens
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

**Model weights** are not in the repo (they are gitignored). Place the trained weights at:

```text
models/best_truthlens_v4.pth
```

### Run the web app

```powershell
streamlit run app.py
```

Open http://localhost:8501. Tabs: **Single**, **Batch BGV**, **Official check**.

### Run the API

```powershell
python -m uvicorn truthlens.api:app --host 0.0.0.0 --port 8000
```

Open http://127.0.0.1:8000/docs for the interactive API docs.

| Endpoint | Purpose |
|---|---|
| `GET /health` | Version, model version, OCR and official-check status |
| `GET /v1/workflows` | Available BGV workflows |
| `POST /v1/analyze` | Analyse one image or PDF |
| `POST /v1/batch` | Analyse a set of documents for a workflow |
| `GET /v1/jobs/{id}` | Fetch a batch job result |

## Configuration

Copy `.env.example` to `.env`. Common settings:

| Variable | Meaning |
|---|---|
| `TRUTHLENS_API_KEY` | If set, API requests must authenticate (see `/docs` for the header). Empty means no auth, which is fine for local use only. |
| `TRUTHLENS_TESSERACT_CMD` | Full path to `tesseract.exe` if it is not on PATH. |
| `SETU_*` | Reserved for future official-API integration. Leave empty. |

The `/health` endpoint and the web app both show a warning when Tesseract is not found. Without OCR, document-type detection and field matching are limited.

## Tests

```powershell
python -m unittest tests.test_verhoeff tests.test_product_layer -v
```

The tests do not load the model or call any external API.

## Docker (experimental, untested)

```powershell
docker compose up --build
```

API on port 8000, UI on port 8501. Mount the weights file into `models/`. This path has not been fully tested yet.

## Project layout

```text
app.py                  Streamlit UI
truthlens/pipeline.py   Single entry point used by UI and API
truthlens/api.py        FastAPI app
truthlens/analyzer.py   CNN + Grad-CAM
truthlens/ocr.py        Tesseract wrapper + status check
truthlens/qrscan.py     QR decoding and QR-vs-OCR comparison
truthlens/fields.py     Masked PAN / Aadhaar / DL extraction, checksum
truthlens/doc_types.py  Document type detection
truthlens/bgv.py        Workflow checklists
truthlens/official.py   Official-source stub (no network calls)
truthlens/security.py   Upload validation, redaction
tests/                  Unit tests
research_scripts/       Thesis-era helper scripts (not part of the product)
```

## Privacy

- Full Aadhaar / PAN numbers are masked in outputs and redacted in logs.
- Job files are purged after the retention period. Uploaded images are not stored long-term.
- Do not collect more identity documents than you need. Prefer marksheets and certificates for pilots, and obtain consent from every person whose document you process.

## Limitations and roadmap

- Not a legal verification tool (see disclaimer).
- Not yet stress-tested on print-scan, WhatsApp-compressed or glare-affected photos.
- Planned: reviewer queue, case PDF pack, roles, consented pilot, and official-source verification through DigiLocker / Setu as an organisation.

## Author

Shravani R S, M.Tech (Data Science and Artificial Intelligence), IIIT Dharwad.
Supervised by Dr. Utkarsh Mahadeo Khaire.