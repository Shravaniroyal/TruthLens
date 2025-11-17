"""
Simplified test with OBVIOUS copy-move forgery
"""

import sys
sys.path.append('src')

from cv_module.copymove_detector import CopyMoveDetector
from PIL import Image, ImageDraw
import os


def create_simple_test():
    """
    Create super simple test: white image with one shape
    """
    # Authentic: One circle
    img_auth = Image.new('RGB', (600, 400), 'white')
    draw = ImageDraw.Draw(img_auth)
    draw.ellipse([(100, 150), (200, 250)], fill='red', outline='black', width=3)
    
    auth_path = 'data/sample_documents/simple_authentic.jpg'
    img_auth.save(auth_path, 'JPEG', quality=95)
    print(f"✅ Created authentic (1 circle): {auth_path}")
    
    # Fake: TWO identical circles (one copied)
    img_fake = Image.new('RGB', (600, 400), 'white')
    draw = ImageDraw.Draw(img_fake)
    draw.ellipse([(100, 150), (200, 250)], fill='red', outline='black', width=3)
    draw.ellipse([(400, 150), (500, 250)], fill='red', outline='black', width=3)  # COPIED!
    
    fake_path = 'data/sample_documents/simple_fake.jpg'
    img_fake.save(fake_path, 'JPEG', quality=95)
    print(f"✅ Created fake (2 identical circles): {fake_path}")
    
    return auth_path, fake_path


def test_simple():
    """
    Test on simple, obvious case
    """
    print("="*60)
    print("SIMPLE COPY-MOVE TEST")
    print("="*60)
    
    auth_path, fake_path = create_simple_test()
    
    detector = CopyMoveDetector(block_size=16, threshold=0.98)
    
    print("\n[TEST 1] Authentic (1 circle):")
    result_auth = detector.detect(auth_path, 'data/sample_documents/simple_auth_result.jpg')
    print(f"   Duplicates: {result_auth['num_duplicates']}")
    print(f"   Score: {result_auth['fraud_score']}")
    
    print("\n[TEST 2] Fake (2 identical circles):")
    result_fake = detector.detect(fake_path, 'data/sample_documents/simple_fake_result.jpg')
    print(f"   Duplicates: {result_fake['num_duplicates']}")
    print(f"   Score: {result_fake['fraud_score']}")
    
    print("\n" + "="*60)
    if result_fake['num_duplicates'] > result_auth['num_duplicates']:
        print("✅ SUCCESS: Copy-Move detector working correctly!")
        print(f"   Fake has {result_fake['num_duplicates'] - result_auth['num_duplicates']} more duplicates")
    else:
        print("⚠️  Algorithm needs more tuning for text documents")
    print("="*60)


if __name__ == "__main__":
    test_simple()