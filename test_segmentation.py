"""
Test Semantic Segmentation Impact
Compares Copy-Move detection with and without segmentation
"""

import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

# Now import from src
from cv_module.copymove_detector import CopyMoveDetector
from utils.document_segmenter import DocumentSegmenter


def main():
    """
    Compare Copy-Move with and without segmentation
    """
    print("=" * 70)
    print("SEMANTIC SEGMENTATION TEST")
    print("Checking imports...")
    
    # Verify imports worked
    print(f"✅ CopyMoveDetector imported: {CopyMoveDetector}")
    print(f"✅ DocumentSegmenter imported: {DocumentSegmenter}")
    print("=" * 70)
    
    # Test document
    test_doc = 'data/sample_documents/bank_statement_authentic.jpg'
    
    # Check if file exists
    if not os.path.exists(test_doc):
        print(f"\n⚠️  Test document not found: {test_doc}")
        print("\nLooking for available documents...")
        if os.path.exists('data/sample_documents'):
            docs = [f for f in os.listdir('data/sample_documents') if f.endswith('.jpg')]
            if docs:
                print("Available documents:")
                for f in docs:
                    print(f"   - {f}")
                # Use first available document
                test_doc = os.path.join('data/sample_documents', docs[0])
                print(f"\nUsing: {test_doc}")
            else:
                print("No documents found!")
                return
        else:
            print("data/sample_documents directory not found!")
            return
    
    print(f"\nTesting on: {test_doc}")
    
    # Test 1: WITHOUT segmentation (baseline)
    print("\n" + "="*70)
    print("TEST 1: Copy-Move WITHOUT Segmentation (Baseline)")
    print("="*70)
    
    try:
        detector_baseline = CopyMoveDetector(use_segmentation=False)
        result_baseline = detector_baseline.detect(
            test_doc,
            output_path='data/sample_documents/copymove_no_seg.jpg'
        )
        
        print(f"\n📊 Results:")
        print(f"   Duplicates Found: {result_baseline['num_duplicates']}")
        print(f"   Fraud Score: {result_baseline['fraud_score']}/100")
        print(f"   Assessment: {result_baseline['interpretation']}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Test 2: WITH segmentation (improved)
    print("\n" + "="*70)
    print("TEST 2: Copy-Move WITH Segmentation (Improved)")
    print("="*70)
    
    try:
        detector_improved = CopyMoveDetector(use_segmentation=True)
        result_improved = detector_improved.detect(
            test_doc,
            output_path='data/sample_documents/copymove_with_seg.jpg'
        )
        
        print(f"\n📊 Results:")
        print(f"   Duplicates Found: {result_improved['num_duplicates']}")
        print(f"   Fraud Score: {result_improved['fraud_score']}/100")
        print(f"   Assessment: {result_improved['interpretation']}")
    except Exception as e:
        print(f"❌ Error: {e}")
        return
    
    # Comparison
    print("\n" + "="*70)
    print("COMPARISON")
    print("="*70)
    
    baseline_dups = result_baseline['num_duplicates']
    improved_dups = result_improved['num_duplicates']
    improvement = baseline_dups - improved_dups
    
    print(f"\nDuplicates Detected:")
    print(f"   Without Segmentation: {baseline_dups}")
    print(f"   With Segmentation:    {improved_dups}")
    
    if baseline_dups > 0:
        reduction_pct = (improvement / baseline_dups) * 100
        print(f"   Reduction:            {improvement} ({reduction_pct:.1f}%)")
    
    if improvement > 0:
        print(f"\n✅ SUCCESS: Segmentation reduced false positives by {improvement}!")
    elif improvement < 0:
        print(f"\n⚠️  Segmentation detected MORE duplicates")
    else:
        print(f"\n➖ No change")
    
    print(f"\n📁 Visualizations saved in: data/sample_documents/")
    
    print(f"\n{'='*70}")
    print("TEST COMPLETE")
    print("="*70)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()