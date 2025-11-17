"""
TruthLens - Integrated Fraud Detection System
Combines ELA, Copy-Move (with segmentation), and Font Analysis
"""

import cv2
import numpy as np
from src.cv_module.ela_detector import ELADetector
from src.cv_module.copymove_detector import CopyMoveDetector
from src.cv_module.font_analyzer import FontAnalyzer
from src.utils.document_segmenter import DocumentSegmenter


class FraudDetector:
    """
    Integrated fraud detection system combining multiple detection methods
    """
    
    def __init__(self, use_segmentation=True):
        """
        Initialize all detection modules
        
        Args:
            use_segmentation (bool): Whether to use semantic segmentation for Copy-Move
        """
        self.ela_detector = ELADetector()
        self.copymove_detector = CopyMoveDetector()
        self.font_analyzer = FontAnalyzer()
        self.segmenter = DocumentSegmenter() if use_segmentation else None
        self.use_segmentation = use_segmentation
        
        print("🚀 FraudDetector initialized")
        print(f"   📊 Segmentation: {'ENABLED' if use_segmentation else 'DISABLED'}")
    
    def analyze_document(self, image_path, verbose=True):
        """
        Run complete fraud analysis on a document
        
        Args:
            image_path (str): Path to document image
            verbose (bool): Print detailed results
            
        Returns:
            dict: Complete analysis results
        """
        if verbose:
            print("\n" + "="*70)
            print("🔍 TRUTHLENS FRAUD ANALYSIS")
            print("="*70)
            print(f"📄 Document: {image_path}")
            print("-"*70)
        
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            return {
                'error': 'Could not load image',
                'fraud_detected': False
            }
        
        # Get text regions if segmentation enabled
        text_regions = None
        if self.use_segmentation and self.segmenter:
            text_regions = self.segmenter.get_text_regions(image_path)
            if verbose and text_regions:
                print(f"   ℹ️  Segmentation: {len(text_regions)} text regions excluded")
        
        # 1. ELA Detection
        if verbose:
            print("\n1️⃣  ERROR LEVEL ANALYSIS (ELA)")
        
        ela_score = self.ela_detector.detect(image_path)
        ela_suspicious = ela_score > 50  # Threshold: 50/100
        
        if verbose:
            print(f"   Score: {ela_score:.2f}/100")
            print(f"   Status: {'🚨 SUSPICIOUS' if ela_suspicious else '✅ CLEAN'}")
        
        # 2. Copy-Move Detection (with segmentation)
        if verbose:
            print("\n2️⃣  COPY-MOVE FORGERY DETECTION")
        
        copymove_result = self.copymove_detector.detect(
            image_path, 
            text_regions=text_regions
        )
        copymove_suspicious = copymove_result['num_duplicates'] > 5
        
        if verbose:
            print(f"   Duplicates found: {copymove_result['num_duplicates']}")
            print(f"   Status: {'🚨 SUSPICIOUS' if copymove_suspicious else '✅ CLEAN'}")
        
        # 3. Font Analysis
        if verbose:
            print("\n3️⃣  FONT CONSISTENCY ANALYSIS")
        
        font_result = self.font_analyzer.analyze(image_path)
        font_suspicious = font_result['is_suspicious']
        
        if verbose:
            print(f"   Unique fonts: {font_result['unique_fonts']}")
            print(f"   Variation: {font_result['variation']:.1f}%")
            print(f"   Status: {'🚨 SUSPICIOUS' if font_suspicious else '✅ CLEAN'}")
        
        # 4. Combined Decision
        suspicious_count = sum([ela_suspicious, copymove_suspicious, font_suspicious])
        fraud_detected = suspicious_count >= 2  # At least 2 detectors agree
        
        # Calculate overall confidence
        confidence = (
            (ela_score if ela_suspicious else (100 - ela_score)) +
            (min(copymove_result['num_duplicates'] * 5, 100) if copymove_suspicious else 0) +
            (font_result['variation'] if font_suspicious else 0)
        ) / 3
        confidence = min(confidence, 100)
        
        if verbose:
            print("\n" + "="*70)
            print("📊 FINAL VERDICT")
            print("="*70)
            print(f"   Suspicious detectors: {suspicious_count}/3")
            print(f"   Overall confidence: {confidence:.1f}%")
            print(f"   Decision: {'🚨 FRAUD DETECTED' if fraud_detected else '✅ AUTHENTIC'}")
            print("="*70 + "\n")
        
        return {
            'fraud_detected': bool(fraud_detected),
            'confidence': float(confidence),
            'ela_score': float(ela_score),
            'ela_suspicious': bool(ela_suspicious),
            'copymove_duplicates': int(copymove_result['num_duplicates']),
            'copymove_suspicious': bool(copymove_suspicious),
            'font_variation': float(font_result['variation']),
            'font_suspicious': bool(font_suspicious),
            'suspicious_count': int(suspicious_count),
            'segmentation_used': bool(self.use_segmentation),
            'text_regions_excluded': int(len(text_regions) if text_regions else 0)
        }
    
    def batch_analyze(self, image_paths, verbose=False):
        """
        Analyze multiple documents
        
        Args:
            image_paths (list): List of image paths
            verbose (bool): Print results for each document
            
        Returns:
            list: Results for each document
        """
        results = []
        
        print("\n" + "="*70)
        print("📦 BATCH ANALYSIS")
        print("="*70)
        print(f"   Total documents: {len(image_paths)}")
        print(f"   Segmentation: {'ENABLED' if self.use_segmentation else 'DISABLED'}")
        print("="*70)
        
        for i, path in enumerate(image_paths, 1):
            print(f"\n[{i}/{len(image_paths)}] Analyzing: {path}")
            result = self.analyze_document(path, verbose=verbose)
            result['image_path'] = path
            results.append(result)
        
        # Summary
        fraud_count = sum(1 for r in results if r.get('fraud_detected', False))
        print("\n" + "="*70)
        print("📊 BATCH SUMMARY")
        print("="*70)
        print(f"   Total analyzed: {len(results)}")
        print(f"   Fraud detected: {fraud_count}")
        print(f"   Authentic: {len(results) - fraud_count}")
        print(f"   Fraud rate: {(fraud_count/len(results)*100):.1f}%")
        print("="*70 + "\n")
        
        return results
    
    def compare_with_without_segmentation(self, image_path):
        """
        Compare results with and without segmentation
        
        Args:
            image_path (str): Path to document image
            
        Returns:
            dict: Comparison results
        """
        print("\n" + "="*70)
        print("🔬 SEGMENTATION COMPARISON TEST")
        print("="*70)
        print(f"📄 Document: {image_path}")
        print("="*70)
        
        # Test WITHOUT segmentation
        print("\n🔹 TEST 1: WITHOUT SEGMENTATION")
        print("-"*70)
        self.use_segmentation = False
        self.segmenter = None
        result_without = self.analyze_document(image_path, verbose=True)
        
        # Test WITH segmentation
        print("\n🔹 TEST 2: WITH SEGMENTATION")
        print("-"*70)
        self.use_segmentation = True
        self.segmenter = DocumentSegmenter()
        result_with = self.analyze_document(image_path, verbose=True)
        
        # Comparison
        print("\n" + "="*70)
        print("📊 COMPARISON RESULTS")
        print("="*70)
        print(f"   Copy-Move Duplicates:")
        print(f"      Without segmentation: {result_without['copymove_duplicates']}")
        print(f"      With segmentation:    {result_with['copymove_duplicates']}")
        
        improvement = result_without['copymove_duplicates'] - result_with['copymove_duplicates']
        print(f"      Reduction: {improvement}")
        print(f"\n   Text regions excluded: {result_with['text_regions_excluded']}")
        print(f"\n   Final verdict:")
        print(f"      Without segmentation: {'🚨 FRAUD' if result_without['fraud_detected'] else '✅ AUTHENTIC'}")
        print(f"      With segmentation:    {'🚨 FRAUD' if result_with['fraud_detected'] else '✅ AUTHENTIC'}")
        print("="*70 + "\n")
        
        return {
            'without_segmentation': result_without,
            'with_segmentation': result_with,
            'improvement': improvement
        }


# Testing function
def test_integrated_system():
    """Test the complete integrated system"""
    import os
    
    # Initialize detector
    detector = FraudDetector(use_segmentation=True)
    
    # Test documents
    test_docs = [
        'data/sample_documents/authentic_doc.jpg',
        'data/sample_documents/fake_doc_copymove.jpg',
        'data/sample_documents/font_mixed_doc.jpg',
        'data/sample_documents/advanced_fake_doc.jpg'
    ]
    
    # Filter existing documents
    existing_docs = [doc for doc in test_docs if os.path.exists(doc)]
    
    if not existing_docs:
        print("❌ No test documents found. Please run sample generators first.")
        return
    
    # Batch analysis
    results = detector.batch_analyze(existing_docs, verbose=False)
    
    # Test segmentation comparison on first document
    if existing_docs:
        print("\n" + "="*70)
        print("🔬 TESTING SEGMENTATION IMPACT")
        print("="*70)
        detector.compare_with_without_segmentation(existing_docs[0])


if __name__ == "__main__":
    test_integrated_system()