"""
Day 2 Test: Copy-Move Forgery Detection
"""

import sys
sys.path.append('src')

from cv_module.copymove_detector import CopyMoveDetector
from utils.create_copymove_samples import generate_copymove_samples
import cv2


def test_copymove_detection():
    """
    Test copy-move detector on authentic vs forged documents
    """
    print("=" * 60)
    print("TruthLens - Day 2: Copy-Move Detection Test")
    print("=" * 60)
    
    # Step 1: Generate test documents
    print("\n[STEP 1] Generating test documents with signatures...")
    generate_copymove_samples()
    
    # Step 2: Initialize detector
    print("\n[STEP 2] Initializing Copy-Move Detector...")
    detector = CopyMoveDetector(block_size=16, threshold=0.95)
    print("✅ Detector ready!")
    
    # Step 3: Test on authentic document
    print("\n[STEP 3] Analyzing AUTHENTIC contract (1 signature)...")
    authentic_path = 'data/sample_documents/contract_authentic.jpg'
    result_auth = detector.detect(
        authentic_path,
        output_path='data/sample_documents/copymove_authentic.jpg'
    )
    
    print(f"   Fraud Score: {result_auth['fraud_score']}/100")
    print(f"   Duplicates Found: {result_auth['num_duplicates']}")
    print(f"   Assessment: {result_auth['interpretation']}")
    
    # Step 4: Test on forged document
    print("\n[STEP 4] Analyzing FORGED contract (duplicated signature)...")
    forged_path = 'data/sample_documents/contract_forged_copymove.jpg'
    result_forged = detector.detect(
        forged_path,
        output_path='data/sample_documents/copymove_forged.jpg'
    )
    
    print(f"   Fraud Score: {result_forged['fraud_score']}/100")
    print(f"   Duplicates Found: {result_forged['num_duplicates']}")
    print(f"   Assessment: {result_forged['interpretation']}")
    
    # Step 5: Summary
    print("\n" + "=" * 60)
    print("✅ COPY-MOVE DETECTION TEST COMPLETE!")
    print("=" * 60)
    print(f"\nResults:")
    print(f"  Authentic (1 signature): {result_auth['num_duplicates']} duplicates")
    print(f"  Forged (copied signature): {result_forged['num_duplicates']} duplicates")
    print(f"\n📊 Visualizations saved:")
    print(f"  - copymove_authentic.jpg (should show NO duplicates)")
    print(f"  - copymove_forged.jpg (should show RED/BLUE boxes on duplicates)")
    
    # Compare results
    if result_forged['num_duplicates'] > result_auth['num_duplicates']:
        print(f"\n✅ SUCCESS: Detector correctly identified more duplicates in forged document!")
    else:
        print(f"\n⚠️  Note: Results may vary. Check visualizations manually.")


if __name__ == "__main__":
    test_copymove_detection()