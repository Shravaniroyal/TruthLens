# ============================================================
# TRUTHLENS v5.0.0 — STREAMLIT APP (entry point)
# UI layer only — all logic lives in the `truthlens/` package
# Run:  streamlit run app.py
# ============================================================

from __future__ import annotations

import io
import json

import matplotlib
import matplotlib.pyplot as plt
import streamlit as st
from PIL import Image

matplotlib.use("Agg")

# Load .env before any settings are read (optional — requires python-dotenv)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from truthlens.bgv import WORKFLOWS, evaluate_workflow
from truthlens.config import settings
from truthlens.exceptions import TruthLensError
from truthlens.fields import ExtractedFields
from truthlens.logging_setup import get_logger, new_request_id, setup_logging
from truthlens.model import load_model
from truthlens.official import DISCLAIMER, cross_verify
from truthlens.pipeline import analyze_document
from truthlens.pdfio import load_pages
from truthlens.security import validate_upload

# ── Initialize logging on first import ───────────────────────────────────────
setup_logging()
log = get_logger("app")

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TruthLens – Document Fraud Detection",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS (UI only — no business logic) ─────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');
:root {
  --cyan:#00f5d4; --red:#ff3b5c; --bg:#03050a; --text:#e8f4fd; --muted:#6b8cae;
}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif!important;background:#03050a!important;color:#e8f4fd!important;}
.stApp{background:#03050a!important;background-image:linear-gradient(rgba(0,245,212,.025) 1px,transparent 1px),linear-gradient(90deg,rgba(0,245,212,.025) 1px,transparent 1px)!important;background-size:60px 60px!important;}
#MainMenu,footer,header{visibility:hidden!important;}
.nav-bar{background:rgba(3,5,10,.95);border-bottom:1px solid rgba(0,245,212,.12);padding:18px 48px;display:flex;align-items:center;justify-content:space-between;margin:-6rem -6rem 0 -6rem;}
.logo-text{font-family:'Syne',sans-serif!important;font-size:24px;font-weight:800;color:#e8f4fd;}
.logo-text span{color:#00f5d4;}
.nav-tag{font-family:'Space Mono',monospace;font-size:11px;color:#6b8cae;letter-spacing:1px;}
.hero-section{text-align:center;padding:80px 40px 60px;}
.hero-badge{display:inline-flex;align-items:center;gap:8px;background:rgba(0,245,212,.08);border:1px solid rgba(0,245,212,.2);border-radius:100px;padding:6px 18px;font-family:'Space Mono',monospace;font-size:11px;color:#00f5d4;margin-bottom:28px;}
.hero-title{font-family:'Syne',sans-serif!important;font-size:72px;font-weight:800;line-height:1;letter-spacing:-3px;margin:0 0 20px;color:#e8f4fd;}
.hero-title .accent{color:#00f5d4;}
.hero-sub{font-size:18px;color:#6b8cae;max-width:600px;margin:0 auto;line-height:1.7;font-weight:300;}
.metrics-row{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:#1a2a4a;border:1px solid #1a2a4a;border-radius:16px;overflow:hidden;margin:40px 0;}
.metric-cell{background:#080d18;padding:28px 32px;text-align:center;}
.metric-num{font-family:'Syne',sans-serif;font-size:36px;font-weight:800;color:#00f5d4;}
.metric-lbl{font-size:12px;color:#6b8cae;margin-top:6px;}
.verdict-fake{background:linear-gradient(135deg,#2d1117,#1a0a0a);border:2px solid #ff3b5c;border-radius:20px;padding:40px;text-align:center;margin:24px 0;}
.verdict-real{background:linear-gradient(135deg,#0d2118,#0a1a0f);border:2px solid #3fb950;border-radius:20px;padding:40px;text-align:center;margin:24px 0;}
.verdict-main-fake{font-family:'Syne',sans-serif;font-size:36px;font-weight:800;color:#ff3b5c;margin:0 0 12px;}
.verdict-main-real{font-family:'Syne',sans-serif;font-size:36px;font-weight:800;color:#3fb950;margin:0 0 12px;}
.verdict-detail{font-size:16px;color:#c9d1d9;}
.verdict-time{font-size:13px;color:#6b8cae;margin-top:10px;font-family:'Space Mono',monospace;}
.section-tag{font-family:'Space Mono',monospace;font-size:11px;color:#00f5d4;letter-spacing:2px;margin-bottom:8px;}
.section-title{font-family:'Syne',sans-serif;font-size:32px;font-weight:800;letter-spacing:-1px;margin-bottom:24px;}
.conf-bar-wrap{margin:8px 0;}
.conf-label{display:flex;justify-content:space-between;font-size:13px;color:#6b8cae;margin-bottom:6px;font-family:'Space Mono',monospace;}
.conf-track{height:8px;background:rgba(255,255,255,.06);border-radius:4px;overflow:hidden;}
.conf-fill-real{height:100%;border-radius:4px;background:linear-gradient(90deg,#00f5d4,#00aaff);}
.conf-fill-fake{height:100%;border-radius:4px;background:linear-gradient(90deg,#ff3b5c,#ff6b6b);}
.reason-box{background:#0d1526;border:1px solid #1a2a4a;border-radius:14px;padding:24px 28px;margin:8px 0;}
.reason-box p{margin:6px 0;font-size:14px;line-height:1.7;color:#c9d1d9;}
.tech-row{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-top:16px;}
.tech-card{background:#0d1526;border:1px solid #1a2a4a;border-radius:14px;padding:24px;}
.tech-card h4{font-family:'Syne',sans-serif;font-size:16px;font-weight:700;margin:12px 0 8px;}
.tech-card p{font-size:13px;color:#6b8cae;line-height:1.6;}
.tech-tag{display:inline-block;margin-top:12px;padding:3px 10px;background:rgba(0,245,212,.08);border:1px solid rgba(0,245,212,.15);border-radius:100px;font-size:10px;color:#00f5d4;font-family:'Space Mono',monospace;}
.footer{border-top:1px solid #1a2a4a;padding:32px 0;text-align:center;margin-top:80px;}
.footer-logo{font-family:'Syne',sans-serif;font-size:20px;font-weight:800;margin-bottom:8px;}
.footer-logo span{color:#00f5d4;}
.footer-info{font-size:13px;color:#6b8cae;line-height:1.8;}
.footer-badges{display:flex;gap:8px;justify-content:center;margin-top:16px;flex-wrap:wrap;}
.footer-badge{padding:4px 12px;border:1px solid #1a2a4a;border-radius:100px;font-size:11px;color:#6b8cae;font-family:'Space Mono',monospace;}
.stButton>button{background:linear-gradient(90deg,#00f5d4,#00aaff)!important;color:#000!important;border:none!important;border-radius:10px!important;padding:14px 32px!important;font-weight:700!important;font-size:15px!important;font-family:'Syne',sans-serif!important;width:100%!important;}
.stDownloadButton>button{background:transparent!important;border:1px solid #1a2a4a!important;color:#00f5d4!important;border-radius:8px!important;font-family:'Space Mono',monospace!important;font-size:13px!important;}
</style>
""", unsafe_allow_html=True)


def _fig_to_pil(fig) -> Image.Image:
    """Convert matplotlib figure to PIL for Streamlit display."""
    buf = io.BytesIO()
    fig.savefig(buf, format="PNG", dpi=150, bbox_inches="tight", facecolor="#03050a")
    buf.seek(0)
    return Image.open(buf).copy()


# ── Static UI sections ─────────────────────────────────────────────────────────
st.markdown("""
<div class="nav-bar">
  <div class="logo-text">🔍 Truth<span>Lens</span></div>
  <div class="nav-tag">AI DOCUMENT FORENSICS · IIIT DHARWAD · M.TECH 2026</div>
  <div class="nav-tag" style="color:#00f5d4">● LIVE</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero-section">
  <div class="hero-badge">AI DOCUMENT FORENSICS – M.TECH THESIS 2026</div>
  <div class="hero-title">Detect <span class="accent">Document</span> Fraud.</div>
  <div class="hero-sub">
    EfficientNet-B4 deep learning + Grad-CAM explainability.<br>
    Supports Indian &amp; Western documents. Shows exactly where and why tampering happened.
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="metrics-row">
  <div class="metric-cell"><div class="metric-num">97.73%</div><div class="metric-lbl">Test Accuracy</div></div>
  <div class="metric-cell"><div class="metric-num">14,992</div><div class="metric-lbl">Training Images</div></div>
  <div class="metric-cell"><div class="metric-num">0.9965</div><div class="metric-lbl">ROC-AUC Score</div></div>
  <div class="metric-cell"><div class="metric-num">IN+WE</div><div class="metric-lbl">Indian + Western Docs</div></div>
</div>
""", unsafe_allow_html=True)


# ── Model startup ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading TruthLens model…")
def _cached_model():
    """Load model once per Streamlit server process."""
    return load_model()


try:
    _model, device = _cached_model()
    st.success(
        f"✅ TruthLens {settings.model_version} ready  |  Device: {device}  |  "
        f"EfficientNet-B4  |  Logs → {settings.log_dir}"
    )
    log.info("Streamlit session started | device=%s", device)
except TruthLensError as exc:
    st.error(f"❌ {exc.user_message}")
    log.error("Model startup failed: %s", exc)
    st.stop()


# ── Upload section ─────────────────────────────────────────────────────────────
st.markdown("<div style='margin-top:40px'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-tag">DOCUMENT ANALYSIS</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Screen documents (visual AI + OCR/QR)</div>', unsafe_allow_html=True)
st.caption(DISCLAIMER)

tab_single, tab_batch, tab_official = st.tabs(
    ["Single document", "Batch BGV", "Official check"]
)

with tab_official:
    off = cross_verify(ExtractedFields())
    st.info(f"**Status:** `{off.status}` — {off.message}")
    st.markdown(
        "Live Setu / DigiLocker keys go in `.env` last. They **do not retrain** the model; "
        "they only compare OCR fields to an official source."
    )

with tab_batch:
    wf_labels = {k: str(v["label"]) for k, v in WORKFLOWS.items()}
    wf_id = st.selectbox(
        "BGV workflow",
        options=list(wf_labels.keys()),
        format_func=lambda k: wf_labels[k],
    )
    batch_files = st.file_uploader(
        "Upload a joining / admissions kit (multiple files)",
        type=sorted(settings.allowed_extensions),
        accept_multiple_files=True,
        key="batch_uploader",
    )
    if batch_files and st.button("Run batch BGV", key="batch_go"):
        rid = new_request_id()
        types: list[str] = []
        rows = []
        with st.spinner("Analyzing kit…"):
            for item in batch_files:
                try:
                    case = analyze_document(item.getvalue(), item.name, request_id=rid)
                    types.append(case.doc_type)
                    vlabel = case.analysis.verdict.label if case.analysis else "—"
                    rows.append(
                        {
                            "file": case.filename,
                            "type": case.doc_type_label,
                            "slot": case.bgv_slot,
                            "verdict": vlabel,
                            "qr": "yes" if case.qr.found else "no",
                            "official": case.official.status,
                        }
                    )
                except TruthLensError as exc:
                    rows.append(
                        {
                            "file": item.name,
                            "type": "rejected",
                            "slot": "—",
                            "verdict": exc.user_message,
                            "qr": "—",
                            "official": "—",
                        }
                    )
        status = evaluate_workflow(wf_id, types)
        if status.complete:
            st.success("Required documents present. Review UNCERTAIN/FAKE rows before you proceed.")
        else:
            st.warning("Missing required slots: " + ", ".join(status.missing_required))
        st.json(status.to_dict())
        st.dataframe(rows, use_container_width=True)

with tab_single:
    col_up, col_info = st.columns([1, 1], gap="large")

    with col_up:
        uploaded = st.file_uploader(
            "Drop your document here",
            type=sorted(settings.allowed_extensions),
            help="Supports: Aadhaar, PAN, Driving Licence, PDFs, mark sheets, invoices",
            key="single_uploader",
        )

    with col_info:
        max_mb = settings.max_upload_bytes // (1024 * 1024)
        st.markdown(f"""
<div style="background:#0d1526;border:1px solid #1a2a4a;border-radius:14px;padding:28px">
  <div style="font-family:'Space Mono',monospace;font-size:11px;color:#00f5d4;
  letter-spacing:2px;margin-bottom:16px">WHAT THIS TOOL ACCEPTS</div>
  <div style="font-size:14px;color:#c9d1d9;line-height:2">
    🇮🇳 Indian docs — Aadhaar, PAN, Driving Licence<br>
    📄 PDF + scanned mark sheets, degree certificates<br>
    🧾 Invoices, salary slips, official forms<br>
    📷 Photos of physical documents
  </div>
  <div style="margin-top:16px;font-size:13px;color:#6b8cae">
    Max file size: {max_mb} MB &nbsp;|&nbsp; Formats: JPG, PNG, BMP, TIFF, WebP, PDF<br>
    🔒 Files validated before analysis — see logs/audit.log
  </div>
</div>""", unsafe_allow_html=True)
    if uploaded:
        file_bytes = uploaded.getvalue()
        try:
            validated = validate_upload(file_bytes, uploaded.name)
            img_pil = load_pages(file_bytes, validated.media_kind)[0]
        except TruthLensError as exc:
            st.error(f"❌ {exc.user_message}")
            log.warning("Upload rejected: %s", exc)
            st.stop()

        st.image(img_pil, caption=f"Uploaded: {validated.safe_filename}", use_container_width=True)

        if st.button("🔍 Analyze Document Now"):
            rid = new_request_id()
            log.info("Analysis requested | request_id=%s | file=%s", rid, validated.safe_filename)

            with st.spinner("Analyzing document…"):
                try:
                    case = analyze_document(file_bytes, uploaded.name, request_id=rid)
                    result = case.analysis
                    if result is None:
                        st.error("Forensic model did not run.")
                        st.stop()
                except TruthLensError as exc:
                    st.error(f"❌ {exc.user_message}")
                    st.stop()

            q = case.quality
            if q.warnings:
                st.warning(" · ".join(q.warnings))
            st.markdown(
                f"**Type:** {case.doc_type_label} · **QR:** "
                f"{'found' if case.qr.found else 'none'} · "
                f"**Official:** `{case.official.status}`"
            )
            if case.qr_vs_ocr_mismatch:
                st.error("QR payload does not match printed (OCR) ID fields.")
            fields = case.fields.to_public_dict()
            if any(fields.values()):
                st.json({"extracted_fields_masked": fields})

            v = result.verdict
            tc = {"FAKE": "#ff3b5c", "UNCERTAIN": "#ffd60a", "REAL": "#3fb950"}[v.label]

            if v.label == "FAKE":
                st.markdown(f"""
<div class="verdict-fake">
  <div class="verdict-main-fake">⚠️ DOCUMENT FRAUD DETECTED</div>
  <div class="verdict-detail">Confidence: <strong>{v.confidence:.1f}%</strong> &nbsp;|&nbsp;
  Real: {v.real_pct:.1f}% &nbsp;|&nbsp; Fake: {v.fake_pct:.1f}%</div>
  <div class="verdict-time">Inference: {result.elapsed_ms:.0f} ms &nbsp;|&nbsp; Request: {rid}</div>
</div>""", unsafe_allow_html=True)
            elif v.label == "UNCERTAIN":
                st.markdown(f"""
<div style="background:linear-gradient(135deg,#1a1505,#0f0d00);border:2px solid #ffd60a;
border-radius:20px;padding:40px;text-align:center;margin:24px 0">
  <div style="font-family:'Syne',sans-serif;font-size:32px;font-weight:800;color:#ffd60a;
  margin-bottom:12px">🔎 NEEDS MANUAL REVIEW</div>
  <div style="font-size:15px;color:#c9d1d9">Real: {v.real_pct:.1f}% &nbsp;|&nbsp; Fake: {v.fake_pct:.1f}%</div>
  <div class="verdict-time">Inference: {result.elapsed_ms:.0f} ms &nbsp;|&nbsp; Request: {rid}</div>
</div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
<div class="verdict-real">
  <div class="verdict-main-real">✅ AUTHENTIC DOCUMENT</div>
  <div class="verdict-detail">Confidence: <strong>{v.confidence:.1f}%</strong> &nbsp;|&nbsp;
  Real: {v.real_pct:.1f}% &nbsp;|&nbsp; Fake: {v.fake_pct:.1f}%</div>
  <div class="verdict-time">Inference: {result.elapsed_ms:.0f} ms &nbsp;|&nbsp; Request: {rid}</div>
</div>""", unsafe_allow_html=True)

            st.markdown(f"""
<div style="background:#0d1526;border:1px solid #1a2a4a;border-radius:14px;padding:28px;margin:8px 0 24px">
  <div class="conf-bar-wrap">
    <div class="conf-label"><span>✅ Real / Authentic</span><span>{v.real_pct:.2f}%</span></div>
    <div class="conf-track"><div class="conf-fill-real" style="width:{v.real_pct:.1f}%"></div></div>
  </div>
  <div style="height:16px"></div>
  <div class="conf-bar-wrap">
    <div class="conf-label"><span>⚠️ Fake / Tampered</span><span>{v.fake_pct:.2f}%</span></div>
    <div class="conf-track"><div class="conf-fill-fake" style="width:{v.fake_pct:.1f}%"></div></div>
  </div>
</div>""", unsafe_allow_html=True)

            st.markdown('<div class="section-tag">EXPLAINABILITY</div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="section-title">🔥 Grad-CAM — Where Did the Model Look?</div>',
                unsafe_allow_html=True,
            )

            fig, axes = plt.subplots(1, 3, figsize=(15, 5))
            fig.patch.set_facecolor("#03050a")
            for ax in axes:
                ax.set_facecolor("#03050a")

            axes[0].imshow(result.img_np)
            axes[0].set_title("Original Document", color="white", fontsize=13, fontweight="bold", pad=10)
            axes[0].axis("off")

            axes[1].imshow(result.heatmap)
            axes[1].set_title(
                "Fraud Heatmap\\n(Red = Suspicious Regions)",
                color=tc, fontsize=13, fontweight="bold", pad=10,
            )
            axes[1].axis("off")

            axes[2].imshow(result.overlay)
            axes[2].set_title(
                f"Overlay — {v.label}\\n({v.confidence:.1f}% confidence)",
                color=tc, fontsize=13, fontweight="bold", pad=10,
            )
            axes[2].axis("off")

            plt.suptitle("TruthLens — Grad-CAM Analysis", color="white", fontsize=15, fontweight="bold", y=1.02)
            plt.tight_layout()
            gcam_pil = _fig_to_pil(fig)
            plt.close()
            st.image(gcam_pil, use_container_width=True)

            if v.label in ("FAKE", "UNCERTAIN"):
                heading = (
                    "🔬 Why Is This Document Fake?"
                    if v.label == "FAKE"
                    else "🔎 Why Is This Document Flagged?"
                )
                st.markdown('<div class="section-tag">FORENSIC ANALYSIS</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="section-title">{heading}</div>', unsafe_allow_html=True)
                try:
                    from forensic_explainer import explain_fraud

                    zone_type = case.doc_type if case.doc_type in ("aadhaar", "pan", "dl") else "generic"
                    reasons, ela_img, _ = explain_fraud(
                        img_pil,
                        result.gradcam,
                        doc_type=zone_type,
                        confidence=result.fake_prob,
                    )
                    st.markdown('<div class="reason-box">', unsafe_allow_html=True)
                    for reason in reasons:
                        st.markdown(reason)
                    st.markdown("</div>", unsafe_allow_html=True)

                    col_hm, col_ela = st.columns(2)
                    with col_hm:
                        st.image(gcam_pil, caption="Grad-CAM — model focus regions", use_container_width=True)
                    with col_ela:
                        st.image(ela_img, caption="ELA Map — digitally modified regions", use_container_width=True)
                except Exception:
                    log.exception("Forensic explainer failed")
                    st.warning("Forensic explainer unavailable. Check logs for details.")

            buf = io.BytesIO()
            gcam_pil.save(buf, format="PNG")
            buf.seek(0)
            st.download_button(
                "⬇️ Download Grad-CAM Report",
                data=buf,
                file_name=f"TruthLens_{validated.safe_filename.rsplit('.', 1)[0]}_report.png",
                mime="image/png",
            )
            st.download_button(
                "⬇️ Download JSON case report",
                data=json.dumps(case.to_public_dict(), indent=2),
                file_name=f"TruthLens_{validated.safe_filename.rsplit('.', 1)[0]}_case.json",
                mime="application/json",
            )


# ── Footer ─────────────────────────────────────────────────────────────────────
st.markdown("<div style='margin-top:80px'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-tag">TECHNOLOGY</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Built on Real Science</div>', unsafe_allow_html=True)
st.markdown("""
<div class="tech-row">
  <div class="tech-card"><div style="font-size:28px">🏗️</div><h4>EfficientNet-B4</h4>
  <p>18.4M parameters trained on 14,992 Western + Indian documents.</p>
  <span class="tech-tag">torchvision</span></div>
  <div class="tech-card"><div style="font-size:28px">🔥</div><h4>Grad-CAM + ELA</h4>
  <p>Spatial attribution + compression forensics explain every verdict.</p>
  <span class="tech-tag">explainable AI</span></div>
  <div class="tech-card"><div style="font-size:28px">🔒</div><h4>Security Layer</h4>
  <p>Upload validation, audit logging, PII-safe logs — ready for gov API integration.</p>
  <span class="tech-tag">production-ready</span></div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="footer">
  <div class="footer-logo">Truth<span>Lens</span></div>
  <div class="footer-info">M.Tech Thesis — IIIT Dharwad | Shravani R S · 2026</div>
  <div class="footer-badges">
    <span class="footer-badge">EfficientNet-B4</span>
    <span class="footer-badge">Grad-CAM</span>
    <span class="footer-badge">ELA</span>
    <span class="footer-badge">Audit Logs</span>
    <span class="footer-badge">REST API</span>
    <span class="footer-badge">OCR / QR</span>
    <span class="footer-badge">BGV batch</span>
  </div>
</div>
""", unsafe_allow_html=True)
