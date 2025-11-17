"""
Computer Vision Module Initialization
Configures OCR engine path for Windows
"""

import pytesseract
import os

# Set Tesseract path for Windows
# Check common installation locations
possible_paths = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    r'C:\Users\Shravani\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
]

# Find which path exists
tesseract_found = False
for path in possible_paths:
    if os.path.exists(path):
        pytesseract.pytesseract.tesseract_cmd = path
        tesseract_found = True
        print(f"✅ Tesseract found at: {path}")
        break

if not tesseract_found:
    print("⚠️  Tesseract not found in common locations")
    print("Please set path manually in src/cv_module/__init__.py")