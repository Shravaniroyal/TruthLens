# 📘 TruthLens Python API Documentation

**Complete guide for integrating TruthLens into your Python applications**

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Core API: FraudDetector](#core-api-frauddetector)
3. [Understanding Results](#understanding-results)
4. [Advanced Usage](#advanced-usage)
5. [Batch Processing](#batch-processing)
6. [Configuration Options](#configuration-options)
7. [Error Handling](#error-handling)
8. [Performance Optimization](#performance-optimization)
9. [Code Examples](#code-examples)
10. [API Reference](#api-reference)

---

## 🚀 Quick Start

### Basic Usage (3 lines of code)

```python
from src.fraud_detector import FraudDetector

detector = FraudDetector()
result = detector.analyze_document('document.jpg')

print(f"Fraud Detected: {result['fraud_detected']}")
print(f"Confidence: {result['confidence']:.1f}%")
```

**Output:**
```
Fraud Detected: True
Confidence: 87.6%
```

---

## 🔍 Core API: FraudDetector

### Initialization

```python
from src.fraud_detector import FraudDetector

# Basic initialization (recommended settings)
detector = FraudDetector(
    use_segmentation=True,  # Enable semantic segmentation (48% fewer false positives)
    block_size=16,          # Copy-move block size (16x16 pixels)
    ela_quality=95,         # JPEG compression quality for ELA
    duplicate_threshold=5,  # Minimum duplicates to flag fraud
    font_threshold=30       # Font variation threshold (%)
)
```

---

### Main Method: `analyze_document()`

**Signature:**
```python
def analyze_document(
    image_path: str,
    use_cache: bool = True,
    verbose: bool = False
) -> dict
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image_path` | `str` | Required | Path to document image (JPG/PNG) |
| `use_cache` | `bool` | `True` | Use cached results if available |
| `verbose` | `bool` | `False` | Print detailed progress to console |

**Returns:** Dictionary with analysis results (see [Understanding Results](#understanding-results))

---

### Example 1: Basic Analysis

```python
from src.fraud_detector import FraudDetector

# Initialize detector
detector = FraudDetector()

# Analyze document
result = detector.analyze_document('invoice.jpg')

# Check verdict
if result['fraud_detected']:
    print(f"🚨 FRAUD DETECTED!")
    print(f"Confidence: {result['confidence']:.1f}%")
    print(f"Reasoning: {result['reasoning']}")
else:
    print(f"✅ DOCUMENT AUTHENTIC")
    print(f"Confidence: {result['confidence']:.1f}%")
```

**Output:**
```
🚨 FRAUD DETECTED!
Confidence: 87.6%
Reasoning: 2 out of 3 detectors flagged suspicious activity
```

---

### Example 2: Detailed Analysis

```python
from src.fraud_detector import FraudDetector

detector = FraudDetector(use_segmentation=True)
result = detector.analyze_document('document.jpg', verbose=True)

# Access all detection scores
print("\n=== DETECTION DETAILS ===")
print(f"ELA Score: {result['ela_score']:.2f}/100")
print(f"Copy-Move Duplicates: {result['copymove_duplicates']}")
print(f"Font Variation: {result['font_variation']:.1f}%")

# Check which detectors flagged fraud
print("\n=== SUSPICIOUS INDICATORS ===")
print(f"ELA Suspicious: {result['ela_suspicious']}")
print(f"Copy-Move Suspicious: {result['copymove_suspicious']}")
print(f"Font Suspicious: {result['font_suspicious']}")

# Processing time
print(f"\nProcessing Time: {result['processing_time']:.2f} seconds")
```

**Output:**
```
=== DETECTION DETAILS ===
ELA Score: 56.23/100
Copy-Move Duplicates: 5847
Font Variation: 43.8%

=== SUSPICIOUS INDICATORS ===
ELA Suspicious: True
Copy-Move Suspicious: True
Font Suspicious: True

Processing Time: 2.16 seconds
```

---

## 📊 Understanding Results

### Result Dictionary Structure

```python
{
    # Primary Verdict
    'fraud_detected': bool,        # True = Fraud, False = Authentic
    'confidence': float,           # 0-100 (percentage)
    'reasoning': str,              # Human-readable explanation
    
    # ELA Detection
    'ela_score': float,            # 0-100 (higher = more suspicious)
    'ela_suspicious': bool,        # True if score > 50
    
    # Copy-Move Detection
    'copymove_duplicates': int,    # Number of duplicate blocks found
    'copymove_suspicious': bool,   # True if duplicates > threshold
    
    # Font Analysis
    'font_variation': float,       # 0-100 (% variation in font sizes)
    'font_suspicious': bool,       # True if variation > 30%
    
    # Metadata
    'processing_time': float,      # Seconds taken to analyze
    'timestamp': str,              # ISO format timestamp
    'image_path': str,             # Path to analyzed document
    'cache_hit': bool              # True if result was from cache
}
```

---

### Interpreting Scores

#### ELA Score (0-100)

| Range | Interpretation | Meaning |
|-------|---------------|---------|
| 0-20 | ✅ Clean | Likely authentic, uniform compression |
| 21-40 | ⚠️ Minor | Some variation, monitor closely |
| 41-60 | 🚨 Moderate | Suspicious editing detected |
| 61-100 | 🔴 High | Strong evidence of manipulation |

**Threshold:** 50+ = Suspicious

---

#### Copy-Move Duplicates

| Range | Interpretation | Meaning |
|-------|---------------|---------|
| 0-100 | ✅ Normal | Expected patterns/logos |
| 101-500 | ⚠️ Elevated | Check if legitimate repetition |
| 501-2000 | 🚨 High | Likely copied content |
| 2000+ | 🔴 Critical | Definite fraud signature |

**Threshold:** 5+ = Suspicious (with segmentation)

---

#### Font Variation (%)

| Range | Interpretation | Meaning |
|-------|---------------|---------|
| 0-15% | ✅ Consistent | Single font family used |
| 16-30% | ⚠️ Mixed | Multiple sizes (may be normal) |
| 31-50% | 🚨 Inconsistent | Strong tampering indicator |
| 51-100% | 🔴 Chaotic | Definite text manipulation |

**Threshold:** 30%+ = Suspicious

---

### Decision Logic

```python
# TruthLens uses 2/3 voting
suspicious_count = (
    int(ela_suspicious) +
    int(copymove_suspicious) +
    int(font_suspicious)
)

fraud_detected = suspicious_count >= 2  # Need 2 out of 3 agreement
```

**Why 2/3?**
- Reduces false positives (one detector can be wrong)
- Increases confidence in verdict
- Industry standard for multimodal systems

---

## 🔧 Advanced Usage

### Example 3: Disable Segmentation (Faster, Less Accurate)

```python
from src.fraud_detector import FraudDetector

# Without segmentation (1.47s vs 2.16s)
detector = FraudDetector(use_segmentation=False)
result = detector.analyze_document('document.jpg')

print(f"Processing Time: {result['processing_time']:.2f}s")
# Output: Processing Time: 1.47s
```

**Use when:**
- Speed is critical (real-time processing)
- Documents have minimal text
- False positives acceptable

---

### Example 4: Custom Thresholds

```python
from src.fraud_detector import FraudDetector

# More sensitive (catches more fraud, more false positives)
strict_detector = FraudDetector(
    duplicate_threshold=3,   # Lower = more sensitive
    font_threshold=25        # Lower = more sensitive
)

# Less sensitive (fewer false positives, may miss fraud)
lenient_detector = FraudDetector(
    duplicate_threshold=10,  # Higher = less sensitive
    font_threshold=40        # Higher = less sensitive
)
```

---

### Example 5: Without Caching

```python
from src.fraud_detector import FraudDetector

detector = FraudDetector()

# Force fresh analysis (ignore cache)
result = detector.analyze_document(
    'document.jpg',
    use_cache=False  # Always recompute
)
```

**Use when:**
- Document has been modified
- Testing parameter changes
- Cache might be stale

---

## 📦 Batch Processing

### Example 6: Process Multiple Documents

```python
from src.fraud_detector import FraudDetector
import os

detector = FraudDetector()
results = []

# Process all JPGs in folder
folder = 'data/documents/'
for filename in os.listdir(folder):
    if filename.endswith(('.jpg', '.png')):
        filepath = os.path.join(folder, filename)
        result = detector.analyze_document(filepath)
        results.append({
            'filename': filename,
            'fraud_detected': result['fraud_detected'],
            'confidence': result['confidence']
        })

# Print summary
fraud_count = sum(1 for r in results if r['fraud_detected'])
print(f"\nProcessed {len(results)} documents")
print(f"Fraud detected: {fraud_count}")
print(f"Authentic: {len(results) - fraud_count}")
```

---

### Example 7: Using BatchProcessor

```python
from src.batch_processor import BatchProcessor

# Initialize
processor = BatchProcessor(use_segmentation=True)

# Process directory
results = processor.process_directory(
    input_dir='data/documents/',
    output_file='results.json',  # Save results
    use_cache=True
)

# Get statistics
stats = processor.get_statistics()
print(f"Total processed: {stats['total_documents']}")
print(f"Fraud detected: {stats['fraud_detected']}")
print(f"Cache hits: {stats['cache_hits']}")
print(f"Average time: {stats['avg_processing_time']:.2f}s")
```

---

## ⚙️ Configuration Options

### Complete Configuration Example

```python
from src.fraud_detector import FraudDetector

detector = FraudDetector(
    # Segmentation
    use_segmentation=True,      # Enable text exclusion (recommended)
    
    # Copy-Move Detection
    block_size=16,              # Block size (8, 16, 24, or 32)
    duplicate_threshold=5,      # Min duplicates to flag fraud
    
    # ELA Detection
    ela_quality=95,             # JPEG quality (85-98, FBI standard: 95)
    ela_threshold=50,           # Score threshold for suspicious
    
    # Font Analysis
    font_threshold=30,          # Variation % threshold
    
    # Performance
    cache_enabled=True,         # Enable result caching
    cache_dir='data/cache/'     # Cache storage location
)
```

---

### Parameter Optimization Guide

**For Speed (Real-time Processing):**
```python
detector = FraudDetector(
    use_segmentation=False,  # Skip OCR overhead
    block_size=24,           # Larger blocks = fewer comparisons
    cache_enabled=True       # Maximize cache usage
)
# Speed: ~1.5s/document
```

**For Accuracy (Forensic Analysis):**
```python
detector = FraudDetector(
    use_segmentation=True,   # Reduce false positives
    block_size=16,           # Optimal detail level
    duplicate_threshold=5,   # Standard threshold
    ela_quality=95           # FBI standard
)
# Speed: ~2.2s/document
```

**For High Security (Banking/Legal):**
```python
detector = FraudDetector(
    use_segmentation=True,
    block_size=16,
    duplicate_threshold=3,   # More sensitive
    font_threshold=25,       # More sensitive
    ela_threshold=40         # More sensitive
)
# More false positives, catches more fraud
```

---

## 🛡️ Error Handling

### Example 8: Robust Error Handling

```python
from src.fraud_detector import FraudDetector
import os

def analyze_safely(image_path):
    """Analyze document with comprehensive error handling"""
    
    # Check file exists
    if not os.path.exists(image_path):
        return {'error': 'File not found', 'success': False}
    
    # Check file format
    if not image_path.lower().endswith(('.jpg', '.jpeg', '.png')):
        return {'error': 'Unsupported format', 'success': False}
    
    try:
        detector = FraudDetector()
        result = detector.analyze_document(image_path)
        result['success'] = True
        return result
        
    except Exception as e:
        return {
            'error': str(e),
            'success': False,
            'image_path': image_path
        }

# Usage
result = analyze_safely('document.jpg')
if result['success']:
    print(f"Fraud: {result['fraud_detected']}")
else:
    print(f"Error: {result['error']}")
```

---

### Common Errors and Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError` | Image path incorrect | Check path exists |
| `TesseractNotFoundError` | Tesseract not installed | See INSTALL.md |
| `cv2.error` | Corrupted image | Verify image opens in viewer |
| `MemoryError` | Image too large | Resize image before analysis |
| `PermissionError` | Cache folder read-only | Check folder permissions |

---

## ⚡ Performance Optimization

### Example 9: Parallel Processing

```python
from src.fraud_detector import FraudDetector
from concurrent.futures import ThreadPoolExecutor
import os

def analyze_document(filepath):
    detector = FraudDetector()
    return detector.analyze_document(filepath)

# Process 10 documents in parallel
folder = 'data/documents/'
filepaths = [os.path.join(folder, f) for f in os.listdir(folder) 
             if f.endswith(('.jpg', '.png'))]

with ThreadPoolExecutor(max_workers=4) as executor:
    results = list(executor.map(analyze_document, filepaths))

print(f"Processed {len(results)} documents in parallel")
```

**Speedup:** ~3-4x on multi-core systems

---

### Example 10: Cache Management

```python
from src.batch_processor import BatchProcessor

processor = BatchProcessor()

# Get cache statistics
stats = processor.get_cache_info()
print(f"Cached documents: {stats['cached_documents']}")
print(f"Cache size: {stats['cache_size_mb']:.2f} MB")
print(f"Hit rate: {stats['hit_rate']:.1f}%")

# Clear cache if needed
if stats['cache_size_mb'] > 100:  # If cache > 100 MB
    processor.clear_cache()
    print("Cache cleared!")
```

---

## 📚 Code Examples

### Example 11: Generate Report

```python
from src.fraud_detector import FraudDetector
import json
from datetime import datetime

def generate_fraud_report(image_path, output_file='report.json'):
    """Generate detailed fraud analysis report"""
    
    detector = FraudDetector(use_segmentation=True)
    result = detector.analyze_document(image_path, verbose=True)
    
    # Create report
    report = {
        'analysis_date': datetime.now().isoformat(),
        'document': image_path,
        'verdict': 'FRAUD' if result['fraud_detected'] else 'AUTHENTIC',
        'confidence': f"{result['confidence']:.1f}%",
        'details': {
            'ela': {
                'score': result['ela_score'],
                'suspicious': result['ela_suspicious'],
                'threshold': 50
            },
            'copymove': {
                'duplicates': result['copymove_duplicates'],
                'suspicious': result['copymove_suspicious'],
                'threshold': 5
            },
            'font': {
                'variation': result['font_variation'],
                'suspicious': result['font_suspicious'],
                'threshold': 30
            }
        },
        'reasoning': result['reasoning'],
        'processing_time': f"{result['processing_time']:.2f}s"
    }
    
    # Save report
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Report saved to {output_file}")
    return report

# Usage
report = generate_fraud_report('suspicious_invoice.jpg')
```

---

### Example 12: Integration with Flask API

```python
from flask import Flask, request, jsonify
from src.fraud_detector import FraudDetector
import os

app = Flask(__name__)
detector = FraudDetector()

@app.route('/analyze', methods=['POST'])
def analyze():
    """API endpoint for fraud detection"""
    
    # Get uploaded file
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    # Save temporarily
    filepath = f"temp/{file.filename}"
    file.save(filepath)
    
    try:
        # Analyze
        result = detector.analyze_document(filepath)
        
        # Return results
        return jsonify({
            'fraud_detected': result['fraud_detected'],
            'confidence': result['confidence'],
            'reasoning': result['reasoning'],
            'details': {
                'ela_score': result['ela_score'],
                'copymove_duplicates': result['copymove_duplicates'],
                'font_variation': result['font_variation']
            }
        })
    
    finally:
        # Clean up
        os.remove(filepath)

if __name__ == '__main__':
    app.run(debug=True)
```

---

## 📖 API Reference

### FraudDetector Class

#### `__init__(self, **kwargs)`

Initialize fraud detector with configuration.

**Parameters:**
- `use_segmentation` (bool): Enable semantic segmentation (default: True)
- `block_size` (int): Copy-move block size in pixels (default: 16)
- `duplicate_threshold` (int): Min duplicates to flag fraud (default: 5)
- `ela_quality` (int): JPEG quality for ELA (default: 95)
- `ela_threshold` (float): ELA score threshold (default: 50)
- `font_threshold` (float): Font variation threshold % (default: 30)
- `cache_enabled` (bool): Enable caching (default: True)
- `cache_dir` (str): Cache directory path (default: 'data/cache/')

---

#### `analyze_document(image_path, use_cache=True, verbose=False)`

Analyze document for fraud indicators.

**Parameters:**
- `image_path` (str): Path to document image
- `use_cache` (bool): Use cached results if available
- `verbose` (bool): Print detailed progress

**Returns:** dict with keys:
- `fraud_detected` (bool)
- `confidence` (float)
- `reasoning` (str)
- `ela_score` (float)
- `ela_suspicious` (bool)
- `copymove_duplicates` (int)
- `copymove_suspicious` (bool)
- `font_variation` (float)
- `font_suspicious` (bool)
- `processing_time` (float)
- `timestamp` (str)
- `image_path` (str)
- `cache_hit` (bool)

---

### BatchProcessor Class

#### `__init__(self, **kwargs)`

Initialize batch processor (same parameters as FraudDetector).

---

#### `process_directory(input_dir, output_file=None, use_cache=True)`

Process all documents in directory.

**Parameters:**
- `input_dir` (str): Directory containing documents
- `output_file` (str, optional): Save results to JSON file
- `use_cache` (bool): Enable caching

**Returns:** List of result dictionaries

---

#### `get_statistics()`

Get processing statistics.

**Returns:** dict with keys:
- `total_documents` (int)
- `fraud_detected` (int)
- `authentic` (int)
- `cache_hits` (int)
- `avg_processing_time` (float)

---

#### `get_cache_info()`

Get cache statistics.

**Returns:** dict with keys:
- `cached_documents` (int)
- `cache_size_mb` (float)
- `hit_rate` (float)

---

#### `clear_cache()`

Clear all cached results.

---

## 💡 Best Practices

### 1. Always Use Segmentation for Text Documents

```python
# ✅ Good (for documents with text)
detector = FraudDetector(use_segmentation=True)

# ❌ Bad (higher false positives)
detector = FraudDetector(use_segmentation=False)
```

---

### 2. Enable Caching for Repeated Analysis

```python
# ✅ Good (2.4x faster on repeats)
result = detector.analyze_document('doc.jpg', use_cache=True)

# ❌ Bad (always recomputes)
result = detector.analyze_document('doc.jpg', use_cache=False)
```

---

### 3. Handle Errors Gracefully

```python
# ✅ Good
try:
    result = detector.analyze_document('doc.jpg')
except Exception as e:
    print(f"Analysis failed: {e}")

# ❌ Bad (crashes on error)
result = detector.analyze_document('doc.jpg')
```

---

### 4. Use Batch Processing for Multiple Documents

```python
# ✅ Good (optimized, shows progress)
from src.batch_processor import BatchProcessor
processor = BatchProcessor()
results = processor.process_directory('documents/')

# ❌ Bad (no optimization, no progress)
for file in files:
    result = detector.analyze_document(file)
```

---

### 5. Adjust Thresholds Based on Use Case

```python
# Banking/Legal (high security)
detector = FraudDetector(duplicate_threshold=3, font_threshold=25)

# General purpose (balanced)
detector = FraudDetector(duplicate_threshold=5, font_threshold=30)

# Low-stakes (fewer false alarms)
detector = FraudDetector(duplicate_threshold=10, font_threshold=40)
```

---

## 🎓 Further Reading

- **[README.md](README.md)** - Project overview and quick start
- **[INSTALL.md](INSTALL.md)** - Installation guide
- **[docs/daily_logs/](docs/daily_logs/)** - Technical deep dives
- **CLI Usage:** `python truthlens_cli.py --help`

---

## 📞 Support

For questions or issues:
- Check [Troubleshooting](#error-handling) section
- Review [examples](#code-examples)
- Refer to source code comments
- Open issue on GitHub (when available)

---

**🎉 Happy Coding with TruthLens!**

*Last updated: Day 8 of development*