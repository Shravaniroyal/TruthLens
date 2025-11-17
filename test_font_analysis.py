"""
Font Analysis Test
Tests font consistency detection on documents
"""

import sys
sys.path.append('src')

from cv_module.font_analyzer import FontAnalyzer
from utils.create_font_test import generate_font_test_samples


def main():
    """
    Test font analyzer
    """
    print("=" * 70)
    print("FONT CONSISTENCY ANALYSIS TEST")
    print("=" * 70)
    
    # Generate test documents
    print("\n[STEP 1] Creating test documents...")
    generate_font_test_samples()
    
    # Initialize analyzer
    print("\n[STEP 2] Initializing Font Analyzer...")
    analyzer = FontAnalyzer(min_confidence=60)
    print("✅ Analyzer ready!")
    
    # Test authentic document
    print("\n" + "="*70)
    print("TEST 1: AUTHENTIC CONTRACT (Consistent Font)")
    print("="*70)
    
    authentic_path = 'data/sample_documents/contract_consistent_font.jpg'
    result_auth = analyzer.detect(
        authentic_path,
        output_path='data/sample_documents/font_analysis_authentic.jpg'
    )
    
    print(f"\n📊 RESULTS:")
    print(f"   Fraud Score: {result_auth['fraud_score']}/100")
    print(f"   Font Variations: {result_auth['font_variations']}")
    print(f"   Suspicious Regions: {result_auth['num_suspicious']}")
    print(f"   Assessment: {result_auth['interpretation']}")
    
    # Test fake document
    print("\n" + "="*70)
    print("TEST 2: FAKE CONTRACT (Mixed Fonts - Copy/Paste)")
    print("="*70)
    
    fake_path = 'data/sample_documents/contract_mixed_fonts.jpg'
    result_fake = analyzer.detect(
        fake_path,
        output_path='data/sample_documents/font_analysis_fake.jpg'
    )
    
    print(f"\n📊 RESULTS:")
    print(f"   Fraud Score: {result_fake['fraud_score']}/100")
    print(f"   Font Variations: {result_fake['font_variations']}")
    print(f"   Suspicious Regions: {result_fake['num_suspicious']}")
    print(f"   Assessment: {result_fake['interpretation']}")
    
    # Summary
    print("\n" + "="*70)
    print("COMPARISON SUMMARY")
    print("="*70)
    print(f"\n{'Metric':<30} {'Authentic':<15} {'Fake':<15}")
    print("-" * 70)
    print(f"{'Fraud Score':<30} {result_auth['fraud_score']:<15} {result_fake['fraud_score']:<15}")
    print(f"{'Font Variations':<30} {result_auth['font_variations']:<15} {result_fake['font_variations']:<15}")
    print(f"{'Suspicious Regions':<30} {result_auth['num_suspicious']:<15} {result_fake['num_suspicious']:<15}")
    
    print(f"\n📁 Visualizations saved in: data/sample_documents/")
    print(f"\n{'='*70}")
    print("FONT ANALYSIS TEST COMPLETE!")
    print("="*70)


if __name__ == "__main__":
    main()