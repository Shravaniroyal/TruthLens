"""
Complete System Test - All 3 Detectors
Tests the fully integrated TruthLens fraud detection system
"""

import sys
sys.path.append('src')

from fraud_detector import IntegratedFraudDetector
import os


def main():
    """
    Complete system demonstration
    """
    print("=" * 80)
    print("TRUTHLENS COMPLETE SYSTEM TEST")
    print("Testing: ELA + Copy-Move + Font Analysis Integration")
    print("=" * 80)
    
    # Initialize integrated detector
    print("\n[INITIALIZATION] Loading all detection modules...")
    detector = IntegratedFraudDetector(
        ela_quality=95,
        copymove_block_size=32,
        copymove_threshold=0.98,
        font_confidence=60
    )
    print("   ✅ ELA Detector loaded (40% weight)")
    print("   ✅ Copy-Move Detector loaded (30% weight)")
    print("   ✅ Font Analyzer loaded (30% weight)")
    print("   ✅ Fusion engine ready")
    
    # Test documents
    test_documents = [
        {
            'name': 'Bank Statement (Authentic)',
            'path': 'data/sample_documents/bank_statement_authentic.jpg',
            'expected': 'AUTHENTIC'
        },
        {
            'name': 'Bank Statement (Fake - Balance Changed)',
            'path': 'data/sample_documents/bank_statement_fake.jpg',
            'expected': 'FRAUDULENT'
        },
        {
            'name': 'Contract (Consistent Font)',
            'path': 'data/sample_documents/contract_consistent_font.jpg',
            'expected': 'AUTHENTIC'
        },
        {
            'name': 'Contract (Mixed Fonts)',
            'path': 'data/sample_documents/contract_mixed_fonts.jpg',
            'expected': 'FRAUDULENT'
        }
    ]
    
    # Track results
    results = []
    
    # Test each document
    for i, doc in enumerate(test_documents, 1):
        if not os.path.exists(doc['path']):
            print(f"\n⚠️  Skipping {doc['name']} - file not found")
            continue
        
        print(f"\n{'='*80}")
        print(f"TEST {i}/{len(test_documents)}: {doc['name']}")
        print(f"Expected: {doc['expected']}")
        print(f"{'='*80}")
        
        # Run detection
        result = detector.detect(doc['path'])
        
        # Store results
        results.append({
            'document': doc['name'],
            'expected': doc['expected'],
            'score': result['combined_fraud_score'],
            'assessment': result['overall_assessment'],
            'confidence': result['confidence_level']
        })
    
    # Print comparative summary
    if results:
        print(f"\n{'='*80}")
        print("COMPARATIVE RESULTS SUMMARY")
        print(f"{'='*80}\n")
        
        print(f"{'Document':<40} {'Score':<10} {'Expected':<15} {'Result':<20}")
        print("-" * 80)
        
        for r in results:
            result_type = "✅ CORRECT" if (
                (r['expected'] == 'AUTHENTIC' and r['score'] < 40) or
                (r['expected'] == 'FRAUDULENT' and r['score'] > 40)
            ) else "❌ INCORRECT"
            
            print(f"{r['document']:<40} {r['score']:<10.1f} {r['expected']:<15} {result_type:<20}")
        
        print("\n" + "="*80)
        print("SYSTEM PERFORMANCE")
        print("="*80)
        
        correct = sum(1 for r in results if (
            (r['expected'] == 'AUTHENTIC' and r['score'] < 40) or
            (r['expected'] == 'FRAUDULENT' and r['score'] > 40)
        ))
        
        accuracy = (correct / len(results)) * 100 if results else 0
        
        print(f"\nDocuments Tested: {len(results)}")
        print(f"Correct Classifications: {correct}/{len(results)}")
        print(f"System Accuracy: {accuracy:.1f}%")
        
        print(f"\n{'='*80}")
        print("✅ COMPLETE SYSTEM TEST FINISHED")
        print(f"{'='*80}\n")


if __name__ == "__main__":
    main()