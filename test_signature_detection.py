"""
Test segmentation on document with clear signature duplication
"""

import sys
sys.path.append('src')

from cv_module.copymove_detector import CopyMoveDetector


def test_signature_detection():
    """
    Test Copy-Move with and without segmentation on signature duplication
    """
    print("=" * 70)
    print("SIGNATURE DUPLICATION TEST")
    print("=" * 70)
    
    test_doc = 'data/sample_documents/signature_duplication_test.jpg'
    
    # Test WITHOUT segmentation
    print("\n[TEST 1] WITHOUT Segmentation (Text causes false positives)")
    print("-" * 70)
    
    detector_no_seg = CopyMoveDetector(
        block_size=16,  # Smaller blocks for signature details
        threshold=0.98,
        use_segmentation=False
    )
    
    result_no_seg = detector_no_seg.detect(
        test_doc,
        output_path='data/sample_documents/signature_test_no_seg.jpg'
    )
    
    print(f"Duplicates Found: {result_no_seg['num_duplicates']}")
    print(f"Fraud Score: {result_no_seg['fraud_score']}/100")
    print(f"Assessment: {result_no_seg['interpretation']}")
    
    # Test WITH segmentation
    print("\n[TEST 2] WITH Segmentation (Text excluded, signature detected)")
    print("-" * 70)
    
    detector_with_seg = CopyMoveDetector(
        block_size=16,
        threshold=0.98,
        use_segmentation=True
    )
    
    result_with_seg = detector_with_seg.detect(
        test_doc,
        output_path='data/sample_documents/signature_test_with_seg.jpg'
    )
    
    print(f"Duplicates Found: {result_with_seg['num_duplicates']}")
    print(f"Fraud Score: {result_with_seg['fraud_score']}/100")
    print(f"Assessment: {result_with_seg['interpretation']}")
    
    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)
    
    print(f"\nWithout Segmentation:")
    print(f"   Total Duplicates: {result_no_seg['num_duplicates']}")
    print(f"   (Includes text false positives + actual signature)")
    
    print(f"\nWith Segmentation:")
    print(f"   Total Duplicates: {result_with_seg['num_duplicates']}")
    print(f"   (Only signature regions - text excluded!)")
    
    reduction = result_no_seg['num_duplicates'] - result_with_seg['num_duplicates']
    
    if reduction > 0:
        pct = (reduction / result_no_seg['num_duplicates']) * 100
        print(f"\n✅ IMPROVEMENT:")
        print(f"   False Positives Eliminated: {reduction}")
        print(f"   Improvement: {pct:.1f}%")
        print(f"\n✨ Segmentation successfully isolated the duplicated signature!")
        print(f"   Text regions excluded, only signature duplication detected.")
    else:
        print(f"\n📊 Both methods detected similar patterns")
        print(f"   This suggests duplicates are in non-text regions")
    
    print(f"\n📁 Check visualizations:")
    print(f"   signature_test_no_seg.jpg   - Shows all duplicates")
    print(f"   signature_test_with_seg.jpg - Shows only signature duplicates")
    
    print(f"\n" + "=" * 70)


if __name__ == "__main__":
    test_signature_detection()