"""
Font Analysis Module
Detects font inconsistencies in documents using OCR
"""

import cv2
import pytesseract
from collections import Counter


class FontAnalyzer:
    """Analyzes font consistency in documents"""
    
    def __init__(self):
        """Initialize font analyzer"""
        # Tesseract path configured in __init__.py
        pass
    
    def analyze(self, image_path):
        """
        Analyze font consistency in a document
        
        Args:
            image_path (str): Path to document image
            
        Returns:
            dict: Analysis results
        """
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                return self._empty_result()
            
            # Convert to RGB for Tesseract
            rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Get detailed OCR data
            data = pytesseract.image_to_data(rgb, output_type=pytesseract.Output.DICT)
            
            # Extract font sizes
            font_sizes = []
            for i, conf in enumerate(data['conf']):
                if int(conf) > 30:  # Only confident detections
                    height = data['height'][i]
                    if height > 0:
                        font_sizes.append(height)
            
            if not font_sizes:
                return self._empty_result()
            
            # Count unique font sizes
            font_counter = Counter(font_sizes)
            unique_fonts = len(font_counter)
            
            # Calculate variation (coefficient of variation)
            import numpy as np
            mean_size = np.mean(font_sizes)
            std_size = np.std(font_sizes)
            variation = (std_size / mean_size * 100) if mean_size > 0 else 0
            
            # Determine if suspicious
            # Multiple fonts OR high variation = suspicious
            is_suspicious = unique_fonts > 5 or variation > 30
            
            return {
                'unique_fonts': unique_fonts,
                'variation': variation,
                'is_suspicious': is_suspicious,
                'font_sizes': list(font_counter.keys())
            }
            
        except Exception as e:
            print(f"⚠️  Font analysis failed: {e}")
            return self._empty_result()
    
    def _empty_result(self):
        """Return empty result on error"""
        return {
            'unique_fonts': 0,
            'variation': 0.0,
            'is_suspicious': False,
            'font_sizes': []
        }


# Test function
def test_font_analyzer():
    """Test font analyzer"""
    import os
    
    analyzer = FontAnalyzer()
    
    test_images = [
        'data/sample_documents/authentic_doc.jpg',
        'data/sample_documents/font_mixed_doc.jpg'
    ]
    
    print("\n" + "="*70)
    print("🧪 TESTING FONT ANALYZER")
    print("="*70)
    
    for img_path in test_images:
        if os.path.exists(img_path):
            result = analyzer.analyze(img_path)
            print(f"\n📄 {os.path.basename(img_path)}")
            print(f"   Unique fonts: {result['unique_fonts']}")
            print(f"   Variation: {result['variation']:.1f}%")
            print(f"   Status: {'🚨 SUSPICIOUS' if result['is_suspicious'] else '✅ CLEAN'}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    test_font_analyzer()