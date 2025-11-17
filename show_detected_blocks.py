"""
Show exactly which blocks are being flagged as duplicates
"""

import sys
sys.path.append('src')

import cv2
import numpy as np
from cv_module.copymove_detector import CopyMoveDetector


def show_detected_blocks():
    """
    Extract and save the actual blocks being detected as duplicates
    """
    print("=" * 70)
    print("SHOWING ACTUAL DETECTED BLOCKS")
    print("=" * 70)
    
    test_doc = 'data/sample_documents/signature_duplication_test.jpg'
    image = cv2.imread(test_doc)
    
    # Detect with segmentation
    detector = CopyMoveDetector(block_size=16, use_segmentation=True)
    result = detector.detect(test_doc)
    
    print(f"\nTotal duplicates: {result['num_duplicates']}")
    
    if result['num_duplicates'] > 0:
        num_to_show = min(10, len(result['duplicate_pairs']))
        print(f"\nShowing first {num_to_show} duplicate pairs...")
        
        # Create a canvas - each pair needs 2 blocks side by side
        canvas_height = 100
        canvas_width = num_to_show * 40  # 16 + 16 + gap
        canvas = np.ones((canvas_height, canvas_width, 3), dtype=np.uint8) * 255
        
        for idx, (pos1, pos2) in enumerate(result['duplicate_pairs'][:num_to_show]):
            x1, y1 = pos1
            x2, y2 = pos2
            
            # Extract blocks
            try:
                block1 = image[y1:y1+16, x1:x1+16]
                block2 = image[y2:y2+16, x2:x2+16]
                
                # Place on canvas
                if block1.shape[:2] == (16, 16):
                    canvas[20:36, idx*40:idx*40+16] = block1
                    cv2.rectangle(canvas, (idx*40, 20), (idx*40+15, 35), (255, 0, 0), 1)
                    
                if block2.shape[:2] == (16, 16):
                    canvas[20:36, idx*40+20:idx*40+36] = block2
                    cv2.rectangle(canvas, (idx*40+20, 20), (idx*40+35, 35), (0, 0, 255), 1)
                
                # Add labels below
                cv2.putText(canvas, f"#{idx+1}", (idx*40+5, 55), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 1)
                           
            except Exception as e:
                print(f"   Skipped pair {idx+1}: {e}")
                continue
        
        output_path = 'data/sample_documents/detected_blocks.jpg'
        cv2.imwrite(output_path, canvas)
        print(f"\n✅ Saved: {output_path}")
        print(f"\n💡 Open this image to see the ACTUAL blocks being detected")
        print(f"   Red box = First block")
        print(f"   Blue box = Matching block")
        print(f"\n   What are they?")
        print(f"   - Signature parts? → Correct detection ✅")
        print(f"   - Header/background? → False positive ❌")
        print(f"   - White/empty? → Need more filtering ⚠️")
    
    print(f"\n" + "=" * 70)


if __name__ == "__main__":
    show_detected_blocks()