# Test Setup Script
import sys
print(f"Python version: {sys.version}")

import numpy as np
print(f"✅ NumPy {np.__version__} installed")

import cv2
print(f"✅ OpenCV {cv2.__version__} installed")

from PIL import Image
print(f"✅ Pillow installed")

import matplotlib
print(f"✅ Matplotlib {matplotlib.__version__} installed")

import pandas as pd
print(f"✅ Pandas {pd.__version__} installed")

print("\n🎉 ALL PACKAGES WORKING! Environment is ready.")