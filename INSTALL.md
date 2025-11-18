# 🔧 TruthLens Installation Guide

**Complete setup guide for Windows, macOS, and Linux**

Estimated time: **15-20 minutes**

---

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Step 1: Install Python](#step-1-install-python)
3. [Step 2: Install Tesseract OCR](#step-2-install-tesseract-ocr)
4. [Step 3: Download TruthLens](#step-3-download-truthlens)
5. [Step 4: Set Up Virtual Environment](#step-4-set-up-virtual-environment)
6. [Step 5: Install Dependencies](#step-5-install-dependencies)
7. [Step 6: Verify Installation](#step-6-verify-installation)
8. [Troubleshooting](#troubleshooting)
9. [Next Steps](#next-steps)

---

## 💻 System Requirements

### Minimum Requirements
- **OS:** Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **RAM:** 4 GB (8 GB recommended)
- **Storage:** 2 GB free space
- **Python:** 3.8 or higher
- **Internet:** Required for initial setup

### Recommended Specifications
- **RAM:** 8 GB or more
- **CPU:** Multi-core processor
- **Storage:** SSD for faster processing

---

## 🐍 Step 1: Install Python

### Check if Python is Already Installed

Open terminal/command prompt and run:

```bash
python --version
```

**If you see `Python 3.8` or higher:** ✅ Skip to Step 2

**If you see error or version < 3.8:** Continue below

---

### Windows Installation

1. **Download Python:**
   - Go to: https://www.python.org/downloads/
   - Click "Download Python 3.11" (or latest version)

2. **Run Installer:**
   - ⚠️ **IMPORTANT:** Check ☑️ "Add Python to PATH"
   - Click "Install Now"
   - Wait for installation to complete

3. **Verify Installation:**
   ```bash
   python --version
   # Should show: Python 3.11.x
   ```

---

### macOS Installation

**Option 1: Using Homebrew (Recommended)**

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Verify
python3 --version
```

**Option 2: Download from Python.org**
- Go to: https://www.python.org/downloads/macos/
- Download macOS installer
- Run the .pkg file
- Follow installation wizard

---

### Linux Installation (Ubuntu/Debian)

```bash
# Update package list
sudo apt update

# Install Python 3.11
sudo apt install python3.11 python3.11-venv python3-pip

# Verify
python3.11 --version
```

---

## 🔤 Step 2: Install Tesseract OCR

Tesseract is required for font analysis. **This is critical!**

---

### Windows Installation

1. **Download Tesseract:**
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download: `tesseract-ocr-w64-setup-5.3.x.exe` (latest version)

2. **Run Installer:**
   - Install to default location: `C:\Program Files\Tesseract-OCR`
   - ✅ Select "Additional script data" during installation
   - Click "Install"

3. **Add to PATH (CRITICAL):**
   
   **Method 1: Automatic (during installation)**
   - Installer asks "Add Tesseract to PATH?" → Check YES
   
   **Method 2: Manual (if you missed it)**
   - Press `Win + X` → System → Advanced system settings
   - Click "Environment Variables"
   - Under "System variables" → Select "Path" → Click "Edit"
   - Click "New" → Add: `C:\Program Files\Tesseract-OCR`
   - Click OK on all windows
   - **Restart your terminal/command prompt**

4. **Verify Installation:**
   ```bash
   tesseract --version
   # Should show: tesseract 5.3.x
   ```

   **If you get error:** See [Troubleshooting](#tesseract-not-found-windows)

---

### macOS Installation

```bash
# Using Homebrew
brew install tesseract

# Verify
tesseract --version
```

---

### Linux Installation (Ubuntu/Debian)

```bash
# Install Tesseract
sudo apt install tesseract-ocr

# Verify
tesseract --version
```

---

## 📦 Step 3: Download TruthLens

### Option 1: Download as ZIP (Easiest)

1. Contact the project owner for the source code
2. Extract ZIP to desired location (e.g., `C:\Users\Shravani\TruthLens`)

### Option 2: Clone from GitHub (When Available)

```bash
# Navigate to desired location
cd C:\Users\Shravani

# Clone repository
git clone https://github.com/Shravaniroyal/TruthLens.git

# Enter directory
cd TruthLens
```

---

## 🌐 Step 4: Set Up Virtual Environment

**Why?** Keeps TruthLens dependencies separate from other Python projects.

### Windows

```bash
# Navigate to TruthLens folder
cd C:\Users\Shravani\TruthLens

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# You should see (venv) before your prompt
# Example: (venv) C:\Users\Shravani\TruthLens>
```

---

### macOS / Linux

```bash
# Navigate to TruthLens folder
cd /path/to/TruthLens

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# You should see (venv) before your prompt
# Example: (venv) user@computer:~/TruthLens$
```

---

## 📚 Step 5: Install Dependencies

**Make sure virtual environment is activated** (you should see `(venv)` in your prompt)

```bash
# Upgrade pip (package manager)
python -m pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

**This will install:**
- opencv-python (Computer Vision)
- numpy (Numerical Computing)
- pillow (Image Processing)
- pytesseract (OCR Interface)
- gradio (Web Interface)
- click (CLI Tool)

**Installation time:** 2-5 minutes depending on internet speed

---

## ✅ Step 6: Verify Installation

### Test 1: Import Required Libraries

```bash
# Still in your TruthLens folder with venv activated
python -c "import cv2, numpy, PIL, pytesseract, gradio, click; print('✅ All libraries imported successfully!')"
```

**Expected output:**
```
✅ All libraries imported successfully!
```

**If you see error:** See [Troubleshooting](#import-errors)

---

### Test 2: Test Tesseract OCR

```bash
python -c "import pytesseract; print(pytesseract.get_tesseract_version()); print('✅ Tesseract is working!')"
```

**Expected output:**
```
tesseract 5.3.x
✅ Tesseract is working!
```

**If you see error:** See [Troubleshooting](#tesseract-not-found)

---

### Test 3: Run TruthLens Web Interface

```bash
python truthlens_web.py
```

**Expected output:**
```
Running on local URL:  http://127.0.0.1:7860

To create a public link, set `share=True` in `launch()`.
```

**Open browser and go to:** http://localhost:7860

**You should see:** TruthLens web interface! 🎉

**Press `Ctrl+C` in terminal to stop the server**

---

### Test 4: Run CLI Tool

```bash
python truthlens_cli.py --help
```

**Expected output:**
```
Usage: truthlens_cli.py [OPTIONS] COMMAND [ARGS]...

  TruthLens - Document Fraud Detection CLI

Commands:
  analyze     Analyze a single document
  batch       Process multiple documents
  cache-info  Show cache statistics
  clear-cache Clear all cached results
```

✅ **If you see this, installation is complete!**

---

## 🐛 Troubleshooting

### Tesseract Not Found (Windows)

**Error:**
```
pytesseract.pytesseract.TesseractNotFoundError: tesseract is not installed or it's not in your PATH
```

**Solution 1: Set Tesseract path in code**

Create a file `src/tesseract_config.py`:
```python
import pytesseract

# Set Tesseract path explicitly
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

Then in `src/cv_module/font_analyzer.py`, add at the top:
```python
from src.tesseract_config import *
```

**Solution 2: Verify Tesseract location**
```bash
# Check if Tesseract is installed
dir "C:\Program Files\Tesseract-OCR\tesseract.exe"
```

If not found, reinstall Tesseract and note the installation path.

---

### Import Errors

**Error:**
```
ModuleNotFoundError: No module named 'cv2'
```

**Solution:**
```bash
# Make sure venv is activated (you see (venv) in prompt)
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

---

### Virtual Environment Not Activating (Windows)

**Error:**
```
venv\Scripts\activate : File cannot be loaded because running scripts is disabled
```

**Solution:**
```bash
# Run PowerShell as Administrator
# Then run:
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# Now try activating again:
venv\Scripts\activate
```

---

### OpenCV Import Error

**Error:**
```
ImportError: DLL load failed while importing cv2
```

**Solution:**
```bash
# Uninstall and reinstall opencv
pip uninstall opencv-python
pip install opencv-python
```

---

### Gradio Not Starting

**Error:**
```
Address already in use
```

**Solution:**
```bash
# Kill process on port 7860
# Windows:
netstat -ano | findstr :7860
taskkill /PID <PID_NUMBER> /F

# macOS/Linux:
lsof -i :7860
kill -9 <PID_NUMBER>

# Or use different port:
python truthlens_web.py  # Gradio will auto-select another port
```

---

### Permission Denied Errors (Linux/macOS)

**Error:**
```
Permission denied
```

**Solution:**
```bash
# Don't use sudo with pip in venv
# Instead, make sure venv is activated:
source venv/bin/activate

# Then install normally:
pip install -r requirements.txt
```

---

### Out of Memory Errors

**Error:**
```
MemoryError or system freezing
```

**Solution:**
- Close other applications
- Process smaller batches (not 100s at once)
- Use CLI instead of Web interface for large batches
- Increase system RAM if possible

---

## 🚀 Next Steps

Now that TruthLens is installed:

### 1. Try the Examples

```bash
# Start web interface
python truthlens_web.py

# In the web interface:
# - Click "Examples" tab
# - Try example documents
# - See how fraud detection works
```

---

### 2. Analyze Your Own Documents

```bash
# Using Web Interface (easiest):
python truthlens_web.py
# Then upload your document

# Using CLI:
python truthlens_cli.py analyze your_document.jpg --verbose
```

---

### 3. Read the Documentation

- **[README.md](README.md)** - Project overview
- **[API_USAGE.md](API_USAGE.md)** - Python API guide (coming soon)
- **[docs/](docs/)** - Technical documentation

---

### 4. Explore the Code

```
TruthLens/
├── src/
│   ├── fraud_detector.py      ⭐ Main detector (start here)
│   ├── cv_module/             # Detection algorithms
│   │   ├── ela_detector.py
│   │   ├── copymove_detector.py
│   │   └── font_analyzer.py
│   └── utils/                 # Helper functions
│
├── truthlens_web.py          ⭐ Web interface
└── truthlens_cli.py          ⭐ Command-line tool
```

---

## 🎓 Learning Resources

### Understanding the Technology

- **ELA Detection:** https://fotoforensics.com/tutorial.php
- **Copy-Move Detection:** Research paper links in `docs/`
- **Font Analysis:** Tesseract OCR documentation

### Python Resources

- **OpenCV Tutorial:** https://docs.opencv.org/4.x/d6/d00/tutorial_py_root.html
- **NumPy Guide:** https://numpy.org/doc/stable/user/quickstart.html
- **Gradio Docs:** https://www.gradio.app/docs/

---

## 💡 Tips for Best Results

1. **Use High-Quality Scans**
   - Resolution: 300+ DPI
   - Format: JPG or PNG
   - Avoid overly compressed images

2. **Start with Web Interface**
   - Easier to visualize results
   - Interactive learning
   - Good for single documents

3. **Use CLI for Batch Processing**
   - Faster for many documents
   - Can automate with scripts
   - Outputs JSON for analysis

4. **Enable Caching**
   - Automatically enabled
   - Speeds up repeated analysis by 2.4x
   - Clear cache if results seem outdated: `python truthlens_cli.py clear-cache`

---

## 🤝 Getting Help

**If you encounter issues:**

1. **Check Troubleshooting section** above
2. **Review error messages carefully**
3. **Verify all steps were followed**
4. **Check Python and Tesseract versions**

**For persistent issues:**
- Open an issue on GitHub (when repository is public)
- Include: Error message, OS version, Python version, steps to reproduce

---

## ✅ Installation Complete!

You're now ready to use TruthLens! 🎉

**Quick test:**
```bash
# Activate venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Start TruthLens
python truthlens_web.py

# Open browser: http://localhost:7860
```

**Happy fraud detecting!** 🔍

---

*For questions or support, refer to README.md or contact the project maintainer.*