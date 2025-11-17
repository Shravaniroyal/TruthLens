"""
Quick segmentation test - just first 3 documents
"""

from src.fraud_detector import FraudDetector
import os

def quick_test():
    """Test segmentation on first 3 documents only"""
    
    doc_folder = 'data/sample_documents'
    all_docs = []
    
    if os.path.exists(doc_folder):
        for file in os.listdir(doc_folder):
            if file.endswith(('.jpg', '.png')):
                all_docs.append(os.path.join(doc_folder, file))
    
    # Only test first 3
    test_docs = all_docs[:3]
    
    print("\n" + "="*70)
    print("🧪 QUICK SEGMENTATION TEST (3 documents)")
    print("="*70)
    
    detector = FraudDetector(use_segmentation=True)
    
    for doc_path in test_docs:
        print(f"\n📄 Testing: {os.path.basename(doc_path)}")
        comparison = detector.compare_with_without_segmentation(doc_path)
        
        print(f"\n✅ Result:")
        print(f"   Reduction: {comparison['improvement']} duplicates")
        print(f"   Text regions: {comparison['with_segmentation']['text_regions_excluded']}")

if __name__ == "__main__":
    quick_test()