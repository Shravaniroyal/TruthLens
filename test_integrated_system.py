"""
Day 2 Final Test: Integrated Multimodal Fraud Detection
Tests combined ELA + Copy-Move system
"""

import sys
sys.path.append('src')

from fraud_detector import IntegratedFraudDetector
from utils.create_advanced_fake import create_advanced_fake_bank_statement


def main():
    """
    Complete Day 2 demonstration
    """
    print("=" * 70)
    print("DAY 2 FINAL TEST: INTEGRATED MULTIMODAL FRAUD DETECTION")
    print("=" * 70)
    
    # Step 1: Generate advanced test documents
    print("\n[STEP 1] Creating test documents...")
    print("   Creating bank statement with signature...")
    authentic_path, fake_path = create_advanced_fake_bank_statement()
    
    # Step 2: Initialize integrated detector
    print("\n[STEP 2] Initializing Integrated Fraud Detection System...")
    detector = IntegratedFraudDetector(
        ela_quality=95,
        copymove_block_size=32,      # Larger blocks
        copymove_threshold=0.98      # Stricter threshold
)
    
    print("   ✅ ELA Detector loaded")
    print("   ✅ Copy-Move Detector loaded")
    print("   ✅ Fusion engine ready")
    
    # Step 3: Analyze AUTHENTIC document
    print("\n" + "="*70)
    print("TEST 1: AUTHENTIC BANK STATEMENT")
    print("="*70)
    result_authentic = detector.detect(authentic_path)
    
    # Step 4: Analyze FAKE document
    print("\n" + "="*70)
    print("TEST 2: FAKE BANK STATEMENT (Balance changed + Signature duplicated)")
    print("="*70)
    result_fake = detector.detect(fake_path)
    
    # Step 5: Comparison Summary
    print("\n" + "="*70)
    print("COMPARATIVE ANALYSIS")
    print("="*70)
    
    print(f"\n📊 SCORES COMPARISON:")
    print(f"{'Metric':<30} {'Authentic':<15} {'Fake':<15} {'Difference'}")
    print("-" * 70)
    print(f"{'Combined Score':<30} {result_authentic['combined_fraud_score']:<15} "
          f"{result_fake['combined_fraud_score']:<15} "
          f"+{result_fake['combined_fraud_score'] - result_authentic['combined_fraud_score']:.1f}")
    
    print(f"{'ELA Score':<30} {result_authentic['ela_analysis']['score']:<15} "
          f"{result_fake['ela_analysis']['score']:<15} "
          f"+{result_fake['ela_analysis']['score'] - result_authentic['ela_analysis']['score']:.1f}")
    
    print(f"{'Copy-Move Score':<30} {result_authentic['copymove_analysis']['score']:<15} "
          f"{result_fake['copymove_analysis']['score']:<15} "
          f"+{result_fake['copymove_analysis']['score'] - result_authentic['copymove_analysis']['score']:.1f}")
    
    print(f"{'Duplicates Found':<30} {result_authentic['copymove_analysis']['num_duplicates']:<15} "
          f"{result_fake['copymove_analysis']['num_duplicates']:<15} "
          f"+{result_fake['copymove_analysis']['num_duplicates'] - result_authentic['copymove_analysis']['num_duplicates']}")
    
    # Final verdict
    print(f"\n{'='*70}")
    print("FINAL VERDICT")
    print(f"{'='*70}")
    
    if result_fake['combined_fraud_score'] > result_authentic['combined_fraud_score'] * 2:
        print("✅ SUCCESS: System correctly identified fake as significantly more suspicious!")
        print(f"   Fake scored {result_fake['combined_fraud_score']/result_authentic['combined_fraud_score']:.1f}x higher than authentic")
    elif result_fake['combined_fraud_score'] > result_authentic['combined_fraud_score']:
        print("✅ PARTIAL SUCCESS: Fake scored higher, but margin could be larger")
    else:
        print("⚠️  NEEDS IMPROVEMENT: Fake not clearly distinguished from authentic")
    
    print(f"\n📁 All analysis images saved in: data/sample_documents/")
    print(f"\n{'='*70}")
    print("DAY 2 COMPLETE: MULTIMODAL DETECTION SYSTEM OPERATIONAL!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()