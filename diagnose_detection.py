"""
Diagnostic tool to visualize what Copy-Move is detecting
"""

import sys
sys.path.append('src')

import cv2
import numpy as np
from cv_module.copymove_detector import CopyMoveDetector
from utils.document_segmenter import DocumentSegmenter


def diagnose_detection():
    """
    Show detailed information about what's being detected
    """
    print("=" * 70)
    print("DIAGNOSTIC: What is Copy-Move Detecting?")
    print("=" * 70)
    
    test_doc = 'data/sample_documents/signature_duplication_test.jpg'
    
    # Load original image
    image = cv2.imread(test_doc)
    
    # Get segmentation mask
    segmenter = DocumentSegmenter()
    seg_result = segmenter.segment(test_doc)
    
    print(f"\n📊 Segmentation Info:")
    print(f"   Text regions found: {seg_result['num_text_regions']}")
    print(f"   Text region examples:")
    for i, region in enumerate(seg_result['text_regions'][:5]):
        print(f"      {i+1}. '{region['text']}' at {region['bbox']}")
    
    # Create visualization showing mask
    print(f"\n🎨 Creating mask visualization...")
    
    # Show text mask (white = text, black = image)
    cv2.imwrite('data/sample_documents/debug_text_mask.jpg', 
                seg_result['text_mask'])
    
    # Show image mask (white = analyze, black = skip)
    cv2.imwrite('data/sample_documents/debug_image_mask.jpg', 
                seg_result['image_mask'])
    
    # Show overlay
    overlay = image.copy()
    # Green tint on text areas
    green_tint = np.zeros_like(image)
    green_tint[:, :, 1] = seg_result['text_mask']
    overlay = cv2.addWeighted(overlay, 0.7, green_tint, 0.3, 0)
    cv2.imwrite('data/sample_documents/debug_overlay.jpg', overlay)
    
    print(f"✅ Mask visualizations saved:")
    print(f"   debug_text_mask.jpg   - White = text areas")
    print(f"   debug_image_mask.jpg  - White = areas to analyze")
    print(f"   debug_overlay.jpg     - Green = text (excluded)")
    
    # Now run Copy-Move with detailed block info
    print(f"\n🔍 Running Copy-Move detection...")
    
    detector = CopyMoveDetector(
        block_size=16,
        threshold=0.98,
        use_segmentation=True
    )
    
    result = detector.detect(test_doc)
    
    print(f"\n📊 Detection Results:")
    print(f"   Total duplicates found: {result['num_duplicates']}")
    
    if result['num_duplicates'] > 0:
        print(f"\n   Duplicate locations (first 5):")
        for i, (pos1, pos2) in enumerate(result['duplicate_pairs'][:5]):
            print(f"      {i+1}. Block at {pos1} matches block at {pos2}")
            distance = np.sqrt((pos1[0]-pos2[0])**2 + (pos1[1]-pos2[1])**2)
            print(f"         Distance: {distance:.0f} pixels")
    
    print(f"\n" + "=" * 70)
    print("DIAGNOSIS COMPLETE")
    print("=" * 70)
    print(f"\n💡 Next steps:")
    print(f"   1. Open debug_overlay.jpg - Check if green covers text")
    print(f"   2. Open signature_test_with_seg.jpg - See what's detected")
    print(f"   3. If duplicates are in white background, that's the issue")


if __name__ == "__main__":
    diagnose_detection()