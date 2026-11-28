# ============================================================
# TRUTHLENS v5.0.0 — STREAMLIT APP (entry point)
# UI layer only — all logic lives in the `truthlens/` package
# Run:  streamlit run app.py
# ============================================================

from __future__ import annotations

import io
import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import streamlit as st  # noqa: E402
from PIL import Image  # noqa: E402

# Load .env before any settings are read (optional — requires python-dotenv)
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from truthlens.bgv import WORKFLOWS, evaluate_workflow  # noqa: E402
from truthlens.config import settings  # noqa: E402
from truthlens.exceptions import TruthLensError  # noqa: E402
from truthlens.fields import ExtractedFields  # noqa: E402
from truthlens.logging_setup import get_logger, new_request_id, setup_logging  # noqa: E402
from truthlens.model import load_model  # noqa: E402
from truthlens.ocr import ocr_status  # noqa: E402
from truthlens.official import DISCLAIMER, cross_verify  # noqa: E402
from truthlens.pdfio import load_pages  # noqa: E402
from truthlens.pipeline import analyze_document  # noqa: E402
from truthlens.review import get_store, queue_case  # noqa: E402
from truthlens.security import validate_upload  # noqa: E402
from truthlens.casepack import build_case_pack

# Headline numbers shown on the page. Edit here if the reported figures change.
METRIC_ACCURACY = "97.73%"
METRIC_TRAIN_IMAGES = "14,992"
METRIC_AUC = "0.9965"

setup_logging()
log = get_logger("app")

st.set_page_config(
    page_title="TruthLens – Document Forensics",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS (UI only — no business logic) ─────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important;background:#03050a!important;color:#e8f4fd!important;}
.stApp{background:#03050a!important;background-image:linear-gradient(rgba(0,245,212,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(0,245,212,.025) 1px,transparent 1px)!important;background-size:60px 60px!important;}
#MainMenu,footer,header{visibility:hidden!important;}
.nav-bar{background:rgba(3,5,10,.95);border-bottom:1px solid rgba(0,245,212,.12);padding:18px 48px;display:flex;align-items:center;justify-content:space-between;margin:-6rem -6rem 0 -6rem;}
.logo-text{font-family:'Syne',sans-serif!important;font-size:24px;font-weight:800;color:#e8f4fd;}
.logo-text span{color:#00f5d4;}
.nav-tag{font-family:'Space Mono',monospace;font-size:11px;color:#6b8cae;letter-spacing:1px;}
.hero-section{text-align:center;padding:70px 40px 40px;}
.hero-badge{display:inline-flex;gap:8px;background:rgba(0,245,212,.08);border:1px solid rgba(0,245,212,.2);border-radius:100px;padding:6px 18px;font-family:'Space Mono',monospace;font-size:11px;color:#00f5d4;margin-bottom:28px;}
.hero-title{font-family:'Syne',sans-serif!important;font-size:68px;font-weight:800;line-height:1;letter-spacing:-3px;margin:0 0 20px;color:#e8f4fd;}
.hero-title .accent{color:#00f5d4;}
.hero-sub{font-size:18px;color:#6b8cae;max-width:640px;margin:0 auto;line-height:1.7;font-weight:300;}
.metrics-row{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:#1a2a4a;border:1px solid #1a2a4a;border-radius:16px;overflow:hidden;margin:32px 0;}
.metric-cell{background:#080d18;padding:24px 28px;text-align:center;}
.metric-num{font-family:'Syne',sans-serif;font-size:34px;font-weight:800;color:#00f5d4;}
.metric-lbl{font-size:12px;color:#6b8cae;margin-top:6px;}
.verdict-box{border-radius:20px;padding:36px;text-align:center;margin:24px 0;}
.verdict-fake{background:linear-gradient(135deg,#2d1117,#1a0a0a);border:2px solid #ff3b5c;}
.verdict-unc{background:linear-gradient(135deg,#1a1505,#0f0d00);border:2px solid #ffd60a;}
.verdict-real{background:linear-gradient(135deg,#0d2118,#0a1a0f);border:2px solid #3fb950;}
.verdict-main{font-family:'Syne',sans-serif;font-size:34px;font-weight:800;margin:0 0 12px;}
.verdict-detail{font-size:16px;color:#c9d1d9;}
.verdict-note{font-size:13px;color:#8aa3bf;margin-top:10px;}
.verdict-time{font-size:13px;color:#6b8cae;margin-top:10px;font-family:'Space Mono',monospace;}
.section-tag{font-family:'Space Mono',monospace;font-size:11px;color:#00f5d4;letter-spacing:2px;margin-bottom:8px;}
.section-title{font-family:'Syne',sans-serif;font-size:30px;font-weight:800;letter-spacing:-1px;margin-bottom:20px;}
.conf-label{display:flex;justify-content:space-between;font-size:13px;color:#6b8cae;margin-bottom:6px;font-family:'Space Mono',monospace;}
.conf-track{height:8px;background:rgba(255,255,255,.06);border-radius:4px;overflow:hidden;}
.conf-fill-real{height:100%;border-radius:4px;background:linear-gradient(90deg,#00f5d4,#00aaff);}
.conf-fill-fake{height:100%;border-radius:4px;background:linear-gradient(90deg,#ff3b5c,#ff6b6b);}
.reason-box{background:#0d1526;border:1px solid #1a2a4a;border-radius:14px;padding:24px 28px;margin:8px 0;}
.info-card{background:#0d1526;border:1px solid #1a2a4a;border-radius:14px;padding:28px;}
.footer{border-top:1px solid #1a2a4a;padding:32px 0;text-align:center;margin-top:60px;}
.footer-logo{font-family:'Syne',sans-serif;font-size:20px;font-weight:800;margin-bottom:8px;}
.footer-logo span{color:#00f5d4;}
.footer-info{font-size:13px;color:#6b8cae;line-height:1.8;}
.stButton>button{background:linear-gradient(90deg,#00f5d4,#00aaff)!important;color:#000!important;border:none!important;border-radius:10px!important;padding:12px 28px!important;font-weight:700!important;font-family:'Syne',sans-serif!important;width:100%!important;}
.stButton>button:disabled{opacity:.4!important;}
.stDownloadButton>button{background:transparent!important;border:1px solid #1a2a4a!important;color:#00f5d4!important;border-radius:8px!important;font-family:'Space Mono',monospace!important;font-size:13px!important;}
</style>
""", unsafe_allow_html=True)


# ── Helpers ────────────────────────────────────────────────────────────────────
VERDICT_COLOR = {"FAKE": "#ff3b5c", "UNCERTAIN": "#ffd60a", "REAL": "#3fb950"}


def _rerun() -> None:
    getattr(st, "rerun", None) and st.rerun() or st.experimental_rerun()


def _fig_to_pil(fig) -> Image.Image:
    buf = io.BytesIO()
    fig.savefig(buf, format="PNG", dpi=150, bbox_inches="tight", facecolor="#03050a")
    buf.seek(0)
    return Image.open(buf).copy()


def _gradcam_figure(result, v) -> Image.Image:
    tc = VERDICT_COLOR[v.label]
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.patch.set_facecolor("#03050a")
    for ax in axes:
        ax.set_facecolor("#03050a")
        ax.axis("off")
    axes[0].imshow(result.img_np)
    axes[0].set_title("Original Document", color="white", fontsize=13, fontweight="bold", pad=10)
    axes[1].imshow(result.heatmap)
    axes[1].set_title("Heatmap\n(red = regions the model focused on)", color=tc, fontsize=13, fontweight="bold", pad=10)
    axes[2].imshow(result.overlay)
    axes[2].set_title(f"Overlay — {v.label}\n({v.confidence:.1f}% confidence)", color=tc, fontsize=13, fontweight="bold", pad=10)
    plt.suptitle("TruthLens — Grad-CAM Analysis", color="white", fontsize=15, fontweight="bold", y=1.02)
    plt.tight_layout()
    pil = _fig_to_pil(fig)
    plt.close(fig)
    return pil


def _render_verdict(v, result, rid: str) -> None:
    timing = f'<div class="verdict-time">Inference: {result.elapsed_ms:.0f} ms &nbsp;|&nbsp; Request: {rid}</div>'
    scores = f"Real: {v.real_pct:.1f}% &nbsp;|&nbsp; Fake: {v.fake_pct:.1f}%"
    if v.label == "FAKE":
        st.markdown(f"""
<div class="verdict-box verdict-fake">
  <div class="verdict-main" style="color:#ff3b5c">⚠️ TAMPERING DETECTED</div>
  <div class="verdict-detail">Confidence: <strong>{v.confidence:.1f}%</strong> &nbsp;|&nbsp; {scores}</div>
  <div class="verdict-note">The image shows signs of editing. Send it for manual review.</div>{timing}
</div>""", unsafe_allow_html=True)
    elif v.label == "UNCERTAIN":
        st.markdown(f"""
<div class="verdict-box verdict-unc">
  <div class="verdict-main" style="color:#ffd60a">🔎 NEEDS MANUAL REVIEW</div>
  <div class="verdict-detail">{scores}</div>
  <div class="verdict-note">The model is not confident either way. A person must decide.</div>{timing}
</div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
<div class="verdict-box verdict-real">
  <div class="verdict-main" style="color:#3fb950">✅ NO TAMPERING DETECTED</div>
  <div class="verdict-detail">Confidence: <strong>{v.confidence:.1f}%</strong> &nbsp;|&nbsp; {scores}</div>
  <div class="verdict-note">This is not proof the document is genuine. It only means no edits were found in the image.</div>{timing}
</div>""", unsafe_allow_html=True)

    st.markdown(f"""
<div class="info-card" style="margin:8px 0 24px">
  <div class="conf-label"><span>✅ Looks unedited</span><span>{v.real_pct:.2f}%</span></div>
  <div class="conf-track"><div class="conf-fill-real" style="width:{v.real_pct:.1f}%"></div></div>
  <div style="height:16px"></div>
  <div class="conf-label"><span>⚠️ Looks edited</span><span>{v.fake_pct:.2f}%</span></div>
  <div class="conf-track"><div class="conf-fill-fake" style="width:{v.fake_pct:.1f}%"></div></div>
</div>""", unsafe_allow_html=True)


def _render_single(saved: dict, img_pil: Image.Image, safe_name: str) -> None:
    case = saved["case"]
    result = case.analysis
    v = result.verdict
    rid = saved["rid"]

    if case.quality.warnings:
        st.warning(" · ".join(case.quality.warnings))
    st.markdown(
        f"**Type:** {case.doc_type_label} · **QR:** {'found' if case.qr.found else 'none'} · "
        f"**Official check:** `{case.official.status}`"
    )
    if case.qr_vs_ocr_mismatch:
        st.error("QR payload does not match the printed (OCR) ID fields.")
    fields = case.fields.to_public_dict()
    if any(fields.values()):
        st.json({"extracted_fields_masked": fields})

    _render_verdict(v, result, rid)

    if saved.get("review_id"):
        st.info(f"Added to the **Review queue** (ID `{saved['review_id']}`). A reviewer can accept, reject or ask for the original.")

    st.markdown('<div class="section-tag">EXPLAINABILITY</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🔥 Where did the model look?</div>', unsafe_allow_html=True)
    gcam_pil = saved["gcam"]
    st.image(gcam_pil, use_container_width=True)

    if v.label in ("FAKE", "UNCERTAIN"):
        st.markdown('<div class="section-tag">FORENSIC ANALYSIS</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-title">🔬 Why was this flagged?</div>', unsafe_allow_html=True
        )
        try:
            from forensic_explainer import explain_fraud

            zone_type = case.doc_type if case.doc_type in ("aadhaar", "pan", "dl") else "generic"
            reasons, ela_img, _ = explain_fraud(
                img_pil, result.gradcam, doc_type=zone_type, confidence=result.fake_prob
            )
            st.markdown('<div class="reason-box">', unsafe_allow_html=True)
            for reason in reasons:
                st.markdown(reason)
            st.markdown("</div>", unsafe_allow_html=True)
            col_hm, col_ela = st.columns(2)
            with col_hm:
                st.image(gcam_pil, caption="Grad-CAM — model focus regions", use_container_width=True)
            with col_ela:
                st.image(ela_img, caption="ELA map — regions with different compression", use_container_width=True)
        except Exception:
            log.exception("Forensic explainer failed")
            st.warning("Forensic explainer unavailable. Check logs for details.")

    base = safe_name.rsplit(".", 1)[0]
    buf = io.BytesIO()
    gcam_pil.save(buf, format="PNG")
    buf.seek(0)
    c1, c2 = st.columns(2)
    with c1:
        st.download_button("⬇️ Download Grad-CAM image", data=buf, file_name=f"TruthLens_{base}_report.png", mime="image/png")
    with c2:
        st.download_button(
            "⬇️ Download JSON case report",
            data=json.dumps(case.to_public_dict(), indent=2),
            file_name=f"TruthLens_{base}_case.json",
            mime="application/json",
        )


# ── Tab: single document ──────────────────────────────────────────────────────
def render_single_tab(operator: str, model_ok: bool) -> None:
    col_up, col_info = st.columns([1, 1], gap="large")
    with col_up:
        uploaded = st.file_uploader(
            "Drop your document here",
            type=sorted(settings.allowed_extensions),
            help="Aadhaar, PAN, driving licence, PDFs, marksheets, certificates, invoices",
            key="single_uploader",
        )
    with col_info:
        max_mb = settings.max_upload_bytes // (1024 * 1024)
        st.markdown(f"""
<div class="info-card">
  <div class="section-tag">WHAT THIS TOOL ACCEPTS</div>
  <div style="font-size:14px;color:#c9d1d9;line-height:2">
    🇮🇳 Indian IDs — Aadhaar, PAN, driving licence<br>
    📄 PDFs and scanned marksheets, degree certificates<br>
    🧾 Invoices, salary slips, official forms<br>
    📷 Photos of physical documents
  </div>
  <div style="margin-top:16px;font-size:13px;color:#6b8cae">
    Max file size: {max_mb} MB &nbsp;|&nbsp; JPG, PNG, BMP, TIFF, WebP, PDF<br>
    🔒 Files are validated before analysis. Full ID numbers are masked in outputs and logs.
  </div>
</div>""", unsafe_allow_html=True)

    if not uploaded:
        return
    if not model_ok:
        st.error("The forensic model is not loaded, so analysis is unavailable.")
        return

    file_bytes = uploaded.getvalue()
    try:
        validated = validate_upload(file_bytes, uploaded.name)
        img_pil = load_pages(file_bytes, validated.media_kind)[0]
    except TruthLensError as exc:
        st.error(f"❌ {exc.user_message}")
        log.warning("Upload rejected: %s", exc)
        return

    st.image(img_pil, caption=f"Uploaded: {validated.safe_filename}", use_container_width=True)

    if st.button("🔍 Analyze Document Now"):
        rid = new_request_id()
        log.info("Analysis requested | request_id=%s | file=%s", rid, validated.safe_filename)
        try:
            with st.spinner("Analyzing document…"):
                case = analyze_document(file_bytes, uploaded.name, request_id=rid)
        except TruthLensError as exc:
            st.error(f"❌ {exc.user_message}")
            return
        if case.analysis is None:
            st.error("Forensic model did not run.")
            return
        item = queue_case(case, operator=operator)
        st.session_state["single"] = {
            "hash": validated.content_hash,
            "case": case,
            "rid": rid,
            "review_id": item.id if item else None,
            "gcam": _gradcam_figure(case.analysis, case.analysis.verdict),
        }

    saved = st.session_state.get("single")
    if saved and saved["hash"] == validated.content_hash:
        _render_single(saved, img_pil, validated.safe_filename)


# ── Tab: batch BGV ────────────────────────────────────────────────────────────
def render_batch_tab(operator: str, model_ok: bool) -> None:
    wf_labels = {k: str(v["label"]) for k, v in WORKFLOWS.items()}
    wf_id = st.selectbox("BGV workflow", options=list(wf_labels.keys()), format_func=lambda k: wf_labels[k])
    batch_files = st.file_uploader(
        "Upload a joining / admissions kit (multiple files)",
        type=sorted(settings.allowed_extensions),
        accept_multiple_files=True,
        key="batch_uploader",
    )
    if not batch_files:
        return
    if not model_ok:
        st.error("The forensic model is not loaded, so analysis is unavailable.")
        return

    if st.button("Run batch BGV", key="batch_go"):
        case_id = new_request_id()
        types: list[str] = []
        rows: list[dict] = []
        queued = 0
        with st.spinner("Analyzing kit…"):
            for item in batch_files:
                try:
                    case = analyze_document(item.getvalue(), item.name, request_id=case_id)
                    types.append(case.doc_type)
                    queued_item = queue_case(case, workflow=wf_id, case_id=case_id, operator=operator)
                    queued += 1 if queued_item else 0
                    rows.append({
                        "file": case.filename,
                        "type": case.doc_type_label,
                        "slot": case.bgv_slot,
                        "verdict": case.analysis.verdict.label if case.analysis else "—",
                        "qr": "yes" if case.qr.found else "no",
                        "review": queued_item.id if queued_item else "",
                    })
                except TruthLensError as exc:
                    rows.append({
                        "file": item.name, "type": "rejected", "slot": "—",
                        "verdict": exc.user_message, "qr": "—", "review": "",
                    })
        st.session_state["batch"] = {
            "case_id": case_id,
            "wf_id": wf_id,
            "operator": operator,
            "rows": rows,
            "status": evaluate_workflow(wf_id, types),
            "queued": queued,
        }

    saved = st.session_state.get("batch")
    if not saved:
        return
    status = saved["status"]
    if status.complete:
        st.success("All required document slots are present. Clear the Review queue items before you proceed.")
    else:
        st.warning("Missing required slots: " + ", ".join(status.missing_required))
    if saved["queued"]:
        st.info(f"{saved['queued']} file(s) were added to the Review queue (case `{saved['case_id']}`).")
    st.dataframe(saved["rows"], use_container_width=True)
    with st.expander("Workflow status (raw)"):
        st.json(status.to_dict())
        pack = build_case_pack(
        case_id=saved["case_id"],
        workflow_label=wf_labels[saved["wf_id"]],
        operator=saved["operator"],
        rows=saved["rows"],
        complete=status.complete,
        missing=list(status.missing_required),
        items=get_store().list(case_id=saved["case_id"]),
    )
    st.download_button(
        "⬇️ Download case pack (PDF)",
        data=pack,
        file_name=f"TruthLens_case_{saved['case_id']}.pdf",
        mime="application/pdf",
    )


# ── Tab: review queue ─────────────────────────────────────────────────────────
DECISION_BUTTONS = [
    ("accepted", "✅ Accept"),
    ("rejected", "❌ Reject"),
    ("need_original", "📎 Need original"),
]


def render_review_tab() -> None:
    store = get_store()
    reviewer = st.text_input("Reviewer name (required to decide)", key="reviewer_name")
    show = st.radio(
        "Show", ["pending", "accepted", "rejected", "need_original", "all"], horizontal=True, key="review_filter"
    )
    items = store.list(status=None if show == "all" else show)
    st.caption(f"{len(items)} item(s). Only masked fields are stored here, never full ID numbers.")
    if not items:
        st.info("Nothing here.")
        return

    for item in reversed(items):
        icon = {"FAKE": "🔴", "UNCERTAIN": "🟡"}.get(item.verdict, "⚪")
        title = f"{icon} {item.filename} · {item.verdict} {item.confidence:.1f}% · {item.status}"
        with st.expander(title):
            st.write(
                f"**Type:** {item.doc_type} · **Workflow:** {item.workflow or '—'} · "
                f"**Case:** `{item.case_id or '—'}` · **Operator:** {item.operator or '—'}"
            )
            st.caption(f"Queued {item.created_at} · hash {item.content_hash} · ID {item.id}")
            if any(item.fields_masked.values()):
                st.json(item.fields_masked)
            if item.status == "pending":
                note = st.text_input("Note (optional)", key=f"note_{item.id}")
                if not reviewer.strip():
                    st.caption("Enter your reviewer name above to enable the buttons.")
                cols = st.columns(3)
                for col, (decision, label) in zip(cols, DECISION_BUTTONS):
                    if col.button(label, key=f"{decision}_{item.id}", disabled=not reviewer.strip()):
                        store.decide(item.id, decision, reviewer, note)
                        _rerun()
            else:
                st.success(f"{item.status} by {item.reviewer} at {item.decided_at}" + (f" — {item.note}" if item.note else ""))


# ── Static header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="nav-bar">
  <div class="logo-text">🔍 Truth<span>Lens</span></div>
  <div class="nav-tag">DOCUMENT FORENSIC SCREENING · IIIT DHARWAD · M.TECH 2026</div>
  <div class="nav-tag" style="color:#00f5d4">v5.0.0</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-section">
  <div class="hero-badge">VISUAL TAMPER SCREENING + OCR / QR + BGV CHECKLISTS</div>
  <div class="hero-title">Spot <span class="accent">Edited</span> Documents.</div>
  <div class="hero-sub">
    EfficientNet-B4 with Grad-CAM and ELA explanations.<br>
    Flags images that look edited and sends doubtful ones to a human reviewer.
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="metrics-row">
  <div class="metric-cell"><div class="metric-num">{METRIC_ACCURACY}</div><div class="metric-lbl">Tamper-detection accuracy (test set)</div></div>
  <div class="metric-cell"><div class="metric-num">{METRIC_TRAIN_IMAGES}</div><div class="metric-lbl">Training images</div></div>
  <div class="metric-cell"><div class="metric-num">{METRIC_AUC}</div><div class="metric-lbl">ROC-AUC (test set)</div></div>
  <div class="metric-cell"><div class="metric-num">IN+WE</div><div class="metric-lbl">Indian + Western documents</div></div>
</div>
""", unsafe_allow_html=True)


# ── Model startup (the app keeps running if weights are missing) ──────────────
@st.cache_resource(show_spinner="Loading TruthLens model…")
def _cached_model():
    return load_model()


model_ok = True
try:
    _model, device = _cached_model()
    st.success(f"✅ TruthLens {settings.model_version} ready  |  Device: {device}  |  EfficientNet-B4")
    log.info("Streamlit session started | device=%s", device)
except TruthLensError as exc:
    model_ok = False
    st.error(f"❌ {exc.user_message}")
    log.error("Model startup failed: %s", exc)

_ocr = ocr_status()
if not _ocr["available"]:
    st.warning(_ocr["warning"])

# ── Main UI ────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-tag">DOCUMENT SCREENING</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Screen documents (visual AI + OCR/QR)</div>', unsafe_allow_html=True)
st.caption(DISCLAIMER)

operator = st.text_input("Operator name", value="anonymous", key="operator_name") or "anonymous"

pending_count = len(get_store().list(status="pending"))
tab_single, tab_batch, tab_review, tab_official = st.tabs(
    ["Single document", "Batch BGV", f"Review queue ({pending_count})", "Official check"]
)

with tab_single:
    render_single_tab(operator, model_ok)

with tab_batch:
    render_batch_tab(operator, model_ok)

with tab_review:
    render_review_tab()

with tab_official:
    off = cross_verify(ExtractedFields())
    st.info(f"**Status:** `{off.status}` — {off.message}")
    st.markdown(
        "Setu / DigiLocker access is not enabled. When keys are added to `.env`, they will "
        "**not retrain** the model. They will only compare OCR fields with an official source."
    )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  <div class="footer-logo">Truth<span>Lens</span></div>
  <div class="footer-info">
    M.Tech Thesis — IIIT Dharwad | Shravani R S · Supervised by Dr. Utkarsh Mahadeo Khaire · 2026<br>
    Visual tamper screening only. Not legal KYC and not UIDAI verification.
  </div>
</div>
""", unsafe_allow_html=True)