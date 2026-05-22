<div align="center">

# 🔍 TruthLens

### AI-Powered Document Fraud Detection System

[![Accuracy](https://img.shields.io/badge/Accuracy-98.18%25-brightgreen?style=for-the-badge)](https://github.com/Shravaniroyal/TruthLens)
[![AUC](https://img.shields.io/badge/ROC--AUC-0.9971-blue?style=for-the-badge)](https://github.com/Shravaniroyal/TruthLens)
[![Model](https://img.shields.io/badge/Model-EfficientNet--B4-orange?style=for-the-badge)](https://github.com/Shravaniroyal/TruthLens)
[![Python](https://img.shields.io/badge/Python-3.9+-yellow?style=for-the-badge&logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red?style=for-the-badge&logo=streamlit)](https://streamlit.io)

*M.Tech Thesis Project — IIIT Dharwad, 2026*
*Under the guidance of Dr. Utkarsh Mahadeo Khaire, Assistant Professor*

</div>

---

## 📌 What is TruthLens?

TruthLens is an end-to-end AI system that detects forged documents in under 3 seconds. It covers both **Western business documents** (invoices, bank statements, certificates) and **Indian government identity documents** (Aadhaar cards, PAN cards, Driving Licences) — the first published system to do so.

Document fraud causes an estimated **USD 5 trillion** in annual losses globally. Existing solutions are too slow, too expensive, or inaccessible. TruthLens solves this with:

- ✅ **98.18% accuracy** on a CVPR 2023 benchmark
- ✅ **2.8 second** end-to-end inference on CPU
- ✅ **Explainable verdicts** via Grad-CAM + Error Level Analysis
- ✅ **Indian government document coverage** — first published system
- ✅ **Browser-accessible** — no technical expertise needed

---

## 🏆 Results

| Metric | Value | Research Target |
|--------|-------|----------------|
| Test Accuracy | **98.18%** | > 95% ✅ |
| ROC-AUC | **0.9971** | > 0.99 ✅ |
| Macro F1-Score | **0.98** | > 0.95 ✅ |
| Indian Doc FP Rate | **0.8%** | < 5% ✅ |
| End-to-End Latency (CPU) | **2.80 s** | < 3 s ✅ |
| SOTA Improvement | **+2.08 pp** over DocTamper CVPR 2023 | — |

Statistical significance: z = 5.11, **p < 0.0001**

---

## 🏗️ System Architecture

```
Document Image (JPEG/PNG/WebP)
        │
        ▼
┌─────────────────────┐
│   Preprocessing     │  Resize → 224×224, ImageNet normalisation
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│  EfficientNet-B4    │  18.4M params, fine-tuned on 14,992 images
│  Classification     │
└─────────────────────┘
        │
        ▼
┌─────────────────────┐
│ Adaptive Threshold  │  p < 0.50 → REAL
│    (τ = 0.85)       │  0.50 ≤ p < 0.85 → UNCERTAIN
└─────────────────────┘  p ≥ 0.85 → FAKE
        │
        ▼
┌─────────────────────────────────────────────┐
│              Explainability                  │
│  Grad-CAM heatmap  |  ELA forensic map      │
│  Human-readable forensic explanation        │
└─────────────────────────────────────────────┘
        │
        ▼
  Verdict + Confidence + Downloadable JSON Report
```

---

## 📂 Repository Structure

```
TruthLens/
├── app.py                        # Streamlit web application (main entry point)
├── forensic_explainer.py         # Human-readable forensic explanation generator
├── gradcam_truthlens.py          # Grad-CAM spatial attribution module
├── generate_indian_docs.py       # Synthetic Indian document generator (Aadhaar, PAN, DL)
├── generate_synthetic_documents.py  # Extended synthetic document pipeline
├── build_indian_dataset.py       # Dataset construction pipeline
├── create_fakes.py               # Tampered document generation (ELA artefact injection)
├── TruthLens_Training.ipynb      # Kaggle training notebook (dual T4 GPUs, 30 epochs)
├── requirements.txt              # Python dependencies
└── README.md
```

---

## 🗄️ Dataset

The TruthLens v4 dataset comprises **14,992 document images** from three sources:

| Source | Real | Fake | Total |
|--------|------|------|-------|
| DocTamper CVPR 2023 | 4,200 | 4,200 | 8,400 |
| RVL-CDIP | 1,700 | 0 | 1,700 |
| Synthetic Indian Docs (Aadhaar, PAN, DL) | 2,400 | 2,400 | 4,800 |
| **Total** | **8,300** | **6,600** | **14,992** |

Split: **70% train / 15% validation / 15% test** — perfectly class-balanced.

📦 **Dataset on Kaggle:** [TruthLens v4 Dataset](https://www.kaggle.com) *(link to your Kaggle dataset)*

---

## 🇮🇳 Synthetic Indian Document Pipeline

Real Indian government identity documents are protected under the **Aadhaar Act 2016** — collecting them for research without UIDAI authorisation is not legally permissible.

TruthLens solves this with a novel synthetic generation pipeline (`generate_indian_docs.py`) that produces photorealistic:

- **Aadhaar cards** — UIDAI orange gradient header, Ashoka Emblem, QR code, Devanagari text
- **PAN cards** — Income Tax Department blue/white layout
- **Driving Licences** — 10 Indian states (Karnataka, Maharashtra, Tamil Nadu, AP, Telangana, Rajasthan, UP, Delhi, West Bengal, Gujarat)

Authentic documents saved at JPEG quality 95. Forged variants inject localised re-compression at quality 80, creating realistic ELA artefacts.

> This is the **first published synthetic Indian government document generation pipeline** for fraud detection research.

---

## 🤖 Model Details

| Component | Specification |
|-----------|--------------|
| Backbone | EfficientNet-B4 (ImageNet pre-trained) |
| Total Parameters | 18,467,145 |
| Classification Head | FC(1792→512) → ReLU → FC(512→1) → Sigmoid |
| Dropout | 0.4 (layer 1), 0.3 (layer 2) |
| Optimiser | AdamW (backbone lr=1e-4, head lr=5e-4) |
| Loss | BCEWithLogitsLoss + class weights |
| Schedule | Cosine Annealing with Warm Restarts (T₀=10) |
| Training | 30 epochs, dual NVIDIA Tesla T4, Kaggle Notebooks |
| Best Checkpoint | Epoch 23 (val acc 97.95%) |

**Model weights:** Download `best_truthlens_v4.pth` from [Google Drive](#) *(add your link)*
Place it in a `models/` folder in the project root.

---

## 🔬 Explainability

### Grad-CAM Spatial Attribution
Validated against DocTamper pixel-level ground-truth tampered region masks:
- Mean IoU: **0.61**
- 91.4% of documents achieve IoU > 0.30
- 51.3% achieve IoU > 0.70 (strong alignment)

### Error Level Analysis (ELA)
- FBI forensics standard quality level (q = 95)
- Detects 81.3% of forged documents
- 4-level severity classification: clean / mild / moderate / strong

### Adaptive Three-Class Thresholding
Reduces Indian document false positives from **4.2% → 0.8%**:
- `p < 0.50` → **REAL**
- `0.50 ≤ p < 0.85` → **UNCERTAIN** (route to manual review)
- `p ≥ 0.85` → **FAKE**

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/Shravaniroyal/TruthLens.git
cd TruthLens
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Download the model weights
Download `best_truthlens_v4.pth` from https://drive.google.com/drive/folders/1rYDOQvBhArF0W-awQI6w7DQclIF--Qub?usp=sharing

```
TruthLens/
└── models/
    └── best_truthlens_v4.pth
```

### 4. Run the app
```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser and upload any document image.

---

## 📊 Comparison with State of the Art

| System | Accuracy | AUC | Indian Docs | Interface |
|--------|----------|-----|-------------|-----------|
| Huang et al. (2011) | 87.0% | — | No | Script only |
| Hao et al. (2019) | 89.2% | — | No | None |
| Jain et al. (2021) | 93.7% | 0.961 | No | None |
| Kumar et al. (2022) | 91.2% | — | Yes* | None |
| DocTamper CVPR 2023 | 96.1% | 0.982 | No | None |
| **TruthLens v4 (Ours)** | **98.18%** | **0.9971** | **Yes** | **Web App** |

*Kumar et al. use proprietary data not available for replication.

---

## 🧪 Training

The complete training pipeline is in `TruthLens_Training.ipynb`, designed for **Kaggle Notebooks** (free dual T4 GPU tier).

Training time: ~63 minutes on dual NVIDIA Tesla T4 GPUs.

📓 **Kaggle Notebook:** [TruthLens Training](https://www.kaggle.com/code/shravanirs4/truthlense-v4) 
---

## 📋 Requirements

```
torch>=2.0.0
torchvision>=0.15.0
timm>=0.9.0
streamlit>=1.28.0
Pillow>=9.4.0
numpy>=1.24.0
scikit-learn>=1.2.0
opencv-python>=4.7.0
matplotlib>=3.7.0
```

---

## 📁 Citation

If you use TruthLens in your research, please cite:

```bibtex
@mastersthesis{shravani2026truthlens,
  author  = {Shravani R S},
  title   = {TruthLens: An AI-Powered Multi-Modal Document Fraud Detection System},
  school  = {Indian Institute of Information Technology Dharwad},
  year    = {2026},
  advisor = {Dr. Utkarsh Mahadeo Khaire}
}
```

---

## 👩‍💻 Author

**Shravani R S**
M.Tech Data Science and Artificial Intelligence
Indian Institute of Information Technology Dharwad
Roll No: 25MDA135

*Under the guidance of Dr. Utkarsh Mahadeo Khaire, Assistant Professor, Dept. of CSE, IIIT Dharwad*

---

<div align="center">

⭐ If this project helped you, please give it a star!

</div>