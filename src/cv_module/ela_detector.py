"""
Error Level Analysis (ELA) Detector
Detects image manipulation by analyzing JPEG compression artifacts
"""

import cv2
import numpy as np
from PIL import Image
import os


class ELADetector:
    """Detects image manipulation using Error Level Analysis"""
    
    def __init__(self, quality=95):
        """
        Initialize ELA detector
        
        Args:
            quality (int): JPEG compression quality for ELA (0-100)
        """
        self.quality = quality
    
    def detect(self, image_path):
        """
        Perform ELA detection on an image
        
        Args:
            image_path (str): Path to the image file
            
        Returns:
            float: ELA score (0-100, higher = more suspicious)
        """
        try:
            # Load original image
            original = Image.open(image_path).convert('RGB')
            
            # Save as JPEG with specified quality
            temp_path = 'temp_ela.jpg'
            original.save(temp_path, 'JPEG', quality=self.quality)
            
            # Load recompressed image
            compressed = Image.open(temp_path).convert('RGB')
            
            # Convert to numpy arrays
            original_arr = np.array(original)
            compressed_arr = np.array(compressed)
            
            # Calculate pixel-wise difference
            diff = cv2.absdiff(original_arr, compressed_arr)
            
            # Convert to grayscale
            diff_gray = cv2.cvtColor(diff, cv2.COLOR_RGB2GRAY)
            
            # Calculate ELA score (normalized standard deviation)
            ela_score = np.std(diff_gray) / 255.0 * 100
            
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return ela_score
            
        except Exception as e:
            print(f"⚠️  ELA detection failed: {e}")
            return 0.0


# Test function
def test_ela():
    """Test ELA detector"""
    import os
    
    detector = ELADetector()
    
    test_images = [
        'data/sample_documents/authentic_doc.jpg',
        'data/sample_documents/fake_doc_copymove.jpg'
    ]
    
    print("\n" + "="*70)
    print("🧪 TESTING ELA DETECTOR")
    print("="*70)
    
    for img_path in test_images:
        if os.path.exists(img_path):
            score = detector.detect(img_path)
            print(f"\n📄 {os.path.basename(img_path)}")
            print(f"   ELA Score: {score:.2f}/100")
            print(f"   Status: {'🚨 SUSPICIOUS' if score > 50 else '✅ CLEAN'}")
    
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    test_ela()