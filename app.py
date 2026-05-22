# ============================================================
# TRUTHLENS v4 — STREAMLIT APP
# EfficientNet-B4 | Grad-CAM | Forensic Explainer
# Western + Indian Docs (Aadhaar / PAN / Driving Licence)
# 97.73% Accuracy | 0.9965 AUC
# ============================================================

import streamlit as st
import torch
import torch.nn as nn
import numpy as np
import cv2
from PIL import Image
import torchvision.transforms as transforms
import torchvision.models as tv_models
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import os
import time

st.set_page_config(
    page_title="TruthLens – Document Fraud Detection",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;700;800&family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

:root {
  --cyan: #00f5d4; --electric: #00aaff; --red: #ff3b5c;
  --gold: #ffd60a; --bg: #03050a; --surface: #080d18;
  --card: #0d1526; --border: #1a2a4a; --text: #e8f4fd; --muted: #6b8cae;
}
html, body, [class*="css"] {
  font-family: 'DM Sans', sans-serif !important;
  background-color: var(--bg) !important;
  color: var(--text) !important;
}
.stApp {
  background: #03050a !important;
  background-image:
    linear-gradient(rgba(0,245,212,.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,245,212,.025) 1px, transparent 1px) !important;
  background-size: 60px 60px !important;
}
#MainMenu, footer, header { visibility: hidden !important; }

.nav-bar {
  background: rgba(3,5,10,0.95); border-bottom: 1px solid rgba(0,245,212,.12);
  padding: 18px 48px; display: flex; align-items: center;
  justify-content: space-between; margin: -6rem -6rem 0 -6rem;
  backdrop-filter: blur(12px);
}
.logo-text { font-family:'Syne',sans-serif!important; font-size:24px;
  font-weight:800; color:var(--text); letter-spacing:-0.5px; }
.logo-text span { color:#00f5d4; }
.nav-tag { font-family:'Space Mono',monospace; font-size:11px;
  color:#6b8cae; letter-spacing:1px; }

.hero-section { text-align:center; padding:80px 40px 60px; }
.hero-badge {
  display:inline-flex; align-items:center; gap:8px;
  background:rgba(0,245,212,.08); border:1px solid rgba(0,245,212,.2);
  border-radius:100px; padding:6px 18px;
  font-family:'Space Mono',monospace; font-size:11px;
  color:#00f5d4; letter-spacing:1px; margin-bottom:28px;
}
.hero-title { font-family:'Syne',sans-serif!important; font-size:72px;
  font-weight:800; line-height:1; letter-spacing:-3px;
  margin:0 0 20px; color:#e8f4fd; }
.hero-title .accent { color:#00f5d4; }
.hero-sub { font-size:18px; color:#6b8cae; max-width:600px;
  margin:0 auto 16px; line-height:1.7; font-weight:300; }

.metrics-row { display:grid; grid-template-columns:repeat(4,1fr);
  gap:1px; background:#1a2a4a; border:1px solid #1a2a4a;
  border-radius:16px; overflow:hidden; margin:40px 0; }
.metric-cell { background:#080d18; padding:28px 32px; text-align:center; }
.metric-num { font-family:'Syne',sans-serif; font-size:36px;
  font-weight:800; color:#00f5d4; line-height:1; }
.metric-lbl { font-size:12px; color:#6b8cae; margin-top:6px; letter-spacing:.3px; }

.verdict-fake { background:linear-gradient(135deg,#2d1117,#1a0a0a);
  border:2px solid #ff3b5c; border-radius:20px; padding:40px;
  text-align:center; margin:24px 0; }
.verdict-real { background:linear-gradient(135deg,#0d2118,#0a1a0f);
  border:2px solid #3fb950; border-radius:20px; padding:40px;
  text-align:center; margin:24px 0; }
.verdict-main-fake { font-family:'Syne',sans-serif; font-size:36px;
  font-weight:800; color:#ff3b5c; margin:0 0 12px; }
.verdict-main-real { font-family:'Syne',sans-serif; font-size:36px;
  font-weight:800; color:#3fb950; margin:0 0 12px; }
.verdict-detail { font-size:16px; color:#c9d1d9; }
.verdict-time { font-size:13px; color:#6b8cae; margin-top:10px;
  font-family:'Space Mono',monospace; }

.section-tag { font-family:'Space Mono',monospace; font-size:11px;
  color:#00f5d4; letter-spacing:2px; margin-bottom:8px; }
.section-title { font-family:'Syne',sans-serif; font-size:32px;
  font-weight:800; letter-spacing:-1px; margin-bottom:24px; }

.conf-bar-wrap { margin:8px 0; }
.conf-label { display:flex; justify-content:space-between; font-size:13px;
  color:#6b8cae; margin-bottom:6px; font-family:'Space Mono',monospace; }
.conf-track { height:8px; background:rgba(255,255,255,.06);
  border-radius:4px; overflow:hidden; }
.conf-fill-real { height:100%; border-radius:4px;
  background:linear-gradient(90deg,#00f5d4,#00aaff); }
.conf-fill-fake { height:100%; border-radius:4px;
  background:linear-gradient(90deg,#ff3b5c,#ff6b6b); }

.reason-box { background:#0d1526; border:1px solid #1a2a4a;
  border-radius:14px; padding:24px 28px; margin:8px 0; }
.reason-box p { margin:6px 0; font-size:14px; line-height:1.7; color:#c9d1d9; }
.ela-caption { font-size:12px; color:#6b8cae; text-align:center;
  font-family:'Space Mono',monospace; margin-top:8px; }

.tech-row { display:grid; grid-template-columns:repeat(3,1fr);
  gap:16px; margin-top:16px; }
.tech-card { background:#0d1526; border:1px solid #1a2a4a;
  border-radius:14px; padding:24px; }
.tech-card h4 { font-family:'Syne',sans-serif; font-size:16px;
  font-weight:700; margin:12px 0 8px; }
.tech-card p { font-size:13px; color:#6b8cae; line-height:1.6; }
.tech-tag { display:inline-block; margin-top:12px; padding:3px 10px;
  background:rgba(0,245,212,.08); border:1px solid rgba(0,245,212,.15);
  border-radius:100px; font-size:10px; color:#00f5d4;
  font-family:'Space Mono',monospace; }

.footer { border-top:1px solid #1a2a4a; padding:32px 0;
  text-align:center; margin-top:80px; }
.footer-logo { font-family:'Syne',sans-serif; font-size:20px;
  font-weight:800; margin-bottom:8px; }
.footer-logo span { color:#00f5d4; }
.footer-info { font-size:13px; color:#6b8cae; line-height:1.8; }
.footer-badges { display:flex; gap:8px; justify-content:center; margin-top:16px; }
.footer-badge { padding:4px 12px; border:1px solid #1a2a4a;
  border-radius:100px; font-size:11px; color:#6b8cae;
  font-family:'Space Mono',monospace; }

.stButton > button {
  background:linear-gradient(90deg,#00f5d4,#00aaff) !important;
  color:#000 !important; border:none !important; border-radius:10px !important;
  padding:14px 32px !important; font-weight:700 !important;
  font-size:15px !important; font-family:'Syne',sans-serif !important;
  width:100% !important;
}
.stButton > button:hover {
  transform:translateY(-2px) !important;
  box-shadow:0 8px 30px rgba(0,245,212,.3) !important;
}
.stDownloadButton > button {
  background:transparent !important; border:1px solid #1a2a4a !important;
  color:#00f5d4 !important; border-radius:8px !important;
  font-family:'Space Mono',monospace !important; font-size:13px !important;
}
</style>
""", unsafe_allow_html=True)

# ── CONFIG ────────────────────────────────────────────────────────────────────
MODEL_PATH = r'C:\Users\Shravani\TruthLens\models\best_truthlens_v4.pth'
DEVICE     = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

IMG_SIZE   = 224
MEAN       = [0.485, 0.456, 0.406]
STD        = [0.229, 0.224, 0.225]

TRANSFORM  = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize(MEAN, STD),
])

# ── NAV ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="nav-bar">
  <div class="logo-text">🔍 Truth<span>Lens</span></div>
  <div class="nav-tag">AI DOCUMENT FORENSICS · IIIT DHARWAD · M.TECH 2026</div>
  <div class="nav-tag" style="color:#00f5d4">● LIVE</div>
</div>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-section">
  <div class="hero-badge">
    <span style="width:6px;height:6px;background:#00f5d4;border-radius:50%;display:inline-block"></span>
    AI DOCUMENT FORENSICS – M.TECH THESIS 2026
  </div>
  <div class="hero-title">Detect <span class="accent">Document</span> Fraud.</div>
  <div class="hero-sub">
    EfficientNet-B4 deep learning + Grad-CAM explainability.<br>
    Supports Indian &amp; Western documents. Shows exactly where and why tampering happened.
  </div>
</div>
""", unsafe_allow_html=True)

# ── METRICS ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="metrics-row">
  <div class="metric-cell">
    <div class="metric-num">97.73%</div>
    <div class="metric-lbl">Test Accuracy</div>
  </div>
  <div class="metric-cell">
    <div class="metric-num">14,992</div>
    <div class="metric-lbl">Training Images</div>
  </div>
  <div class="metric-cell">
    <div class="metric-num">0.9965</div>
    <div class="metric-lbl">ROC-AUC Score</div>
  </div>
  <div class="metric-cell">
    <div class="metric-num">IN+WE</div>
    <div class="metric-lbl">Indian + Western Docs</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── MODEL ─────────────────────────────────────────────────────────────────────
def build_model():
    """EfficientNet-B4 with same head used during v4 training."""
    m = tv_models.efficientnet_b4(weights=None)
    in_feat = m.classifier[1].in_features
    m.classifier = nn.Sequential(
        nn.Dropout(p=0.4, inplace=True),
        nn.Linear(in_feat, 512),
        nn.ReLU(),
        nn.Dropout(p=0.3),
        nn.Linear(512, 1),
    )
    return m

@st.cache_resource
def load_model():
    m = build_model()
    raw = torch.load(MODEL_PATH, map_location=DEVICE)
    # Strip DataParallel 'module.' prefix if present
    state = {k.replace('module.', ''): v for k, v in raw.items()}
    m.load_state_dict(state)
    m.eval()
    m.to(DEVICE)
    return m

try:
    model = load_model()
    st.success(f"✅ TruthLens v4 ready  |  Device: {DEVICE}  |  "
               f"EfficientNet-B4  |  Indian + Western docs")
except Exception as e:
    st.error(f"❌ Model failed to load: {e}")
    st.stop()


# ── GRAD-CAM ──────────────────────────────────────────────────────────────────
def get_gradcam(model, tensor):
    """Return (cam_np H×W float [0,1], prob float)."""
    grads, acts = [], []

    def fwd_hook(_, __, out):
        acts.append(out)

    def bwd_hook(_, __, grad_out):
        grads.append(grad_out[0])

    target = model.features[-1]
    h1 = target.register_forward_hook(fwd_hook)
    h2 = target.register_backward_hook(bwd_hook)

    tensor = tensor.to(DEVICE).requires_grad_(True)
    out    = model(tensor)
    prob   = torch.sigmoid(out).item()
    model.zero_grad()
    out.squeeze().backward()

    h1.remove(); h2.remove()

    g   = grads[0].squeeze().cpu().numpy()           # C H W
    a   = acts[0].squeeze().detach().cpu().numpy()   # C H W
    w   = g.mean(axis=(1, 2))
    cam = np.maximum((w[:, None, None] * a).sum(0), 0)
    cam = cv2.resize(cam, (IMG_SIZE, IMG_SIZE))
    if cam.max() > 0:
        cam /= cam.max()
    return cam, prob


def analyze(img_pil):
    img_rgb = img_pil.convert('RGB').resize((IMG_SIZE, IMG_SIZE))
    img_np  = np.array(img_rgb)
    tensor  = TRANSFORM(img_rgb).unsqueeze(0)

    t0 = time.time()
    with torch.enable_grad():
        cam, prob = get_gradcam(model, tensor)
    elapsed = time.time() - t0

    heatmap = cv2.applyColorMap((cam * 255).astype(np.uint8), cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    overlay = np.clip(0.55 * img_np + 0.45 * heatmap, 0, 255).astype(np.uint8)

    pred   = 1 if prob > 0.5 else 0
    probs  = [1.0 - prob, prob]   # [real, fake]
    return pred, probs, img_np, heatmap, overlay, elapsed, cam


def get_verdict(pred, probs):
    fake_p = probs[1] * 100
    real_p = probs[0] * 100
    # Raised threshold: need >85% to call FAKE (reduces false positives on Indian docs)
    # 60-85% = UNCERTAIN (needs manual review)
    if fake_p >= 85:
        return "FAKE", fake_p
    elif real_p >= 60:
        return "REAL", real_p
    else:
        return "UNCERTAIN", max(fake_p, real_p)


def fig_to_pil(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='PNG', dpi=150, bbox_inches='tight',
                facecolor='#03050a')
    buf.seek(0)
    return Image.open(buf).copy()


def detect_doc_type(filename):
    fn = filename.lower()
    if any(x in fn for x in ['aadhaar', 'aadhar', 'uid', 'uidai']):
        return 'aadhaar'
    if any(x in fn for x in ['pan', 'income_tax', 'it_dept']):
        return 'pan'
    if any(x in fn for x in ['dl', 'driving', 'licence', 'license', 'motor']):
        return 'dl'
    return 'generic'


# ── UPLOAD SECTION ────────────────────────────────────────────────────────────
st.markdown("<div style='margin-top:40px'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-tag">DOCUMENT ANALYSIS</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Upload a Document</div>', unsafe_allow_html=True)

col_up, col_info = st.columns([1, 1], gap="large")

with col_up:
    uploaded = st.file_uploader(
        "Drop your document here",
        type=['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp'],
        help="Supports: Aadhaar, PAN, Driving Licence, mark sheets, invoices, certificates"
    )

with col_info:
    st.markdown("""
<div style="background:#0d1526;border:1px solid #1a2a4a;border-radius:14px;padding:28px">
  <div style="font-family:'Space Mono',monospace;font-size:11px;color:#00f5d4;
  letter-spacing:2px;margin-bottom:16px">WHAT THIS TOOL ACCEPTS</div>
  <div style="font-size:14px;color:#c9d1d9;line-height:2">
    🇮🇳 &nbsp;Indian docs — Aadhaar, PAN card, Driving Licence<br>
    📄 &nbsp;Scanned mark sheets, degree certificates<br>
    🧾 &nbsp;Invoices, salary slips, official forms<br>
    📷 &nbsp;Photos of physical documents
  </div>
  <div style="margin-top:16px;font-size:13px;color:#6b8cae">
    ✅ &nbsp;Fraud verdict + confidence score<br>
    ✅ &nbsp;Grad-CAM heatmap (where model looked)<br>
    ✅ &nbsp;ELA map + specific fraud reasons<br>
    ✅ &nbsp;Downloadable report
  </div>
</div>""", unsafe_allow_html=True)


if uploaded:
    try:
        img_pil = Image.open(uploaded).convert('RGB')
    except Exception:
        st.error("❌ Could not read the uploaded file. Please upload a valid image.")
        st.stop()

    col_img, col_gap = st.columns([1, 1])
    with col_img:
      st.image(img_pil, caption=f"Uploaded: {uploaded.name}", use_container_width=True)
    analyze_btn = st.button("🔍 Analyze Document Now")

    if analyze_btn:
        with st.spinner("Analyzing document..."):
            pred, probs, img_np, heatmap, overlay, elapsed, cam = analyze(img_pil)

        verdict, conf = get_verdict(pred, probs)

        # ── VERDICT ──────────────────────────────────────────────────────────
        if verdict == "FAKE":
            st.markdown(f"""
<div class="verdict-fake">
  <div class="verdict-main-fake">⚠️ DOCUMENT FRAUD DETECTED</div>
  <div class="verdict-detail">
    Confidence: <strong>{conf:.1f}%</strong> &nbsp;|&nbsp;
    Real: {probs[0]*100:.1f}% &nbsp;|&nbsp;
    Fake: {probs[1]*100:.1f}%
  </div>
  <div class="verdict-time">Inference time: {elapsed*1000:.0f}ms</div>
</div>""", unsafe_allow_html=True)

        elif verdict == "UNCERTAIN":
            st.markdown(f"""
<div style="background:linear-gradient(135deg,#1a1505,#0f0d00);
border:2px solid #ffd60a;border-radius:20px;padding:40px;
text-align:center;margin:24px 0">
  <div style="font-family:'Syne',sans-serif;font-size:32px;font-weight:800;
  color:#ffd60a;margin-bottom:12px">🔎 NEEDS MANUAL REVIEW</div>
  <div style="font-size:15px;color:#c9d1d9">
    Real: {probs[0]*100:.1f}% &nbsp;|&nbsp; Fake: {probs[1]*100:.1f}%
  </div>
  <div style="font-family:'Space Mono',monospace;font-size:12px;
  color:#6b8cae;margin-top:16px">Inference: {elapsed*1000:.0f}ms</div>
</div>""", unsafe_allow_html=True)

        else:
            st.markdown(f"""
<div class="verdict-real">
  <div class="verdict-main-real">✅ AUTHENTIC DOCUMENT</div>
  <div class="verdict-detail">
    Confidence: <strong>{conf:.1f}%</strong> &nbsp;|&nbsp;
    Real: {probs[0]*100:.1f}% &nbsp;|&nbsp;
    Fake: {probs[1]*100:.1f}%
  </div>
  <div class="verdict-time">Inference time: {elapsed*1000:.0f}ms</div>
</div>""", unsafe_allow_html=True)

        # ── CONFIDENCE BARS ───────────────────────────────────────────────────
        st.markdown('<div class="section-tag" style="margin-top:32px">CONFIDENCE BREAKDOWN</div>',
                    unsafe_allow_html=True)
        st.markdown(f"""
<div style="background:#0d1526;border:1px solid #1a2a4a;
border-radius:14px;padding:28px;margin:8px 0 24px">
  <div class="conf-bar-wrap">
    <div class="conf-label">
      <span>✅ Real / Authentic</span><span>{probs[0]*100:.2f}%</span>
    </div>
    <div class="conf-track">
      <div class="conf-fill-real" style="width:{probs[0]*100:.1f}%"></div>
    </div>
  </div>
  <div style="height:16px"></div>
  <div class="conf-bar-wrap">
    <div class="conf-label">
      <span>⚠️ Fake / Tampered</span><span>{probs[1]*100:.2f}%</span>
    </div>
    <div class="conf-track">
      <div class="conf-fill-fake" style="width:{probs[1]*100:.1f}%"></div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

        # ── GRAD-CAM ──────────────────────────────────────────────────────────
        st.markdown('<div class="section-tag">EXPLAINABILITY</div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🔥 Grad-CAM — Where Did the Model Look?</div>',
                    unsafe_allow_html=True)

        tc = '#ff3b5c' if verdict == "FAKE" else '#ffd60a' if verdict == "UNCERTAIN" else '#3fb950'

        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        fig.patch.set_facecolor('#03050a')
        for ax in axes:
            ax.set_facecolor('#03050a')

        axes[0].imshow(img_np)
        axes[0].set_title('Original Document', color='white', fontsize=13,
                          fontweight='bold', pad=10)
        axes[0].axis('off')

        axes[1].imshow(heatmap)
        axes[1].set_title('Fraud Heatmap\n(Red = Suspicious Regions)',
                          color=tc, fontsize=13, fontweight='bold', pad=10)
        axes[1].axis('off')

        axes[2].imshow(overlay)
        axes[2].set_title(f'Overlay — {verdict}\n({conf:.1f}% confidence)',
                          color=tc, fontsize=13, fontweight='bold', pad=10)
        axes[2].axis('off')

        plt.suptitle('TruthLens — Grad-CAM Analysis', color='white',
                     fontsize=15, fontweight='bold', y=1.02)
        plt.tight_layout()
        gcam_pil = fig_to_pil(fig)
        plt.close()

        st.image(gcam_pil, use_container_width=True)

        # ── FORENSIC EXPLAINER (only for FAKE) ───────────────────────────────
        if verdict == "FAKE":
            st.markdown("<div style='height:32px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="section-tag">FORENSIC ANALYSIS</div>',
                        unsafe_allow_html=True)
            st.markdown('<div class="section-title">🔬 Why Is This Document Fake?</div>',
                        unsafe_allow_html=True)

            try:
                from forensic_explainer import explain_fraud

                doc_type = detect_doc_type(uploaded.name)
                reasons, ela_img, _ = explain_fraud(
                    img_pil,
                    cam,
                    doc_type=doc_type,
                    confidence=probs[1]
                )

                st.markdown('<div class="reason-box">', unsafe_allow_html=True)
                for reason in reasons:
                    st.markdown(reason)
                st.markdown('</div>', unsafe_allow_html=True)

                # ELA map alongside heatmap
                st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
                col_hm, col_ela = st.columns(2)
                with col_hm:
                    st.image(gcam_pil,
                             caption="Grad-CAM — regions the model focused on",
                             use_container_width=True)
                with col_ela:
                    st.image(ela_img,
                             caption="ELA Map — bright areas = digitally modified regions",
                             use_container_width=True)

                st.markdown("""
<div style="background:rgba(0,245,212,.04);border:1px solid rgba(0,245,212,.12);
border-radius:10px;padding:16px;margin-top:8px;font-size:13px;color:#6b8cae">
  ℹ️ <strong style="color:#00f5d4">How to read these maps:</strong>
  Grad-CAM (left) shows <em>where</em> the model detected anomalies.
  ELA (right) shows <em>which regions were re-saved at different JPEG quality</em> —
  a signature left by image editing software when text or photos are swapped.
  Bright ELA regions overlapping with Grad-CAM hotspots = strong tampering evidence.
</div>""", unsafe_allow_html=True)

            except Exception as ex:
                st.warning(f"Forensic explainer unavailable: {ex}")

        # ── DOWNLOAD ──────────────────────────────────────────────────────────
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        buf = io.BytesIO()
        gcam_pil.save(buf, format='PNG')
        buf.seek(0)
        st.download_button(
            "⬇️ Download Grad-CAM Report",
            data=buf,
            file_name=f"TruthLens_{uploaded.name.rsplit('.',1)[0]}_report.png",
            mime="image/png"
        )


# ── TECH SECTION ──────────────────────────────────────────────────────────────
st.markdown("<div style='margin-top:80px'></div>", unsafe_allow_html=True)
st.markdown('<div class="section-tag">TECHNOLOGY</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Built on Real Science</div>', unsafe_allow_html=True)
st.markdown("""
<div class="tech-row">
  <div class="tech-card">
    <div style="font-size:28px">🏗️</div>
    <h4>EfficientNet-B4</h4>
    <p>18.4M parameter compound-scaled model trained on 14,992 images —
    Western and Indian government documents.</p>
    <span class="tech-tag">torchvision pretrained</span>
  </div>
  <div class="tech-card">
    <div style="font-size:28px">🔥</div>
    <h4>Grad-CAM + ELA</h4>
    <p>Grad-CAM shows where the model looked. Error Level Analysis reveals
    which regions were digitally modified — together they explain exactly why.</p>
    <span class="tech-tag">explainable AI</span>
  </div>
  <div class="tech-card">
    <div style="font-size:28px">🇮🇳</div>
    <h4>Indian + Western Docs</h4>
    <p>Aadhaar, PAN card, Driving Licence (10 states) + CVPR 2023 DocTamper
    Western documents. First thesis to cover both.</p>
    <span class="tech-tag">dual-domain</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
  <div class="footer-logo">Truth<span>Lens</span></div>
  <div class="footer-info">
    M.Tech Thesis — IIIT Dharwad | Data Science &amp; AI<br>
    Shravani R S · 2026
  </div>
  <div class="footer-badges">
    <span class="footer-badge">CVPR 2023</span>
    <span class="footer-badge">PyTorch</span>
    <span class="footer-badge">EfficientNet-B4</span>
    <span class="footer-badge">Grad-CAM</span>
    <span class="footer-badge">ELA</span>
    <span class="footer-badge">Indian Docs</span>
  </div>
</div>
""", unsafe_allow_html=True)