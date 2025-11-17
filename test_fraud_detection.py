"""
Day 1 Demo: First Fraud Detection Test
Tests ELA detector on authentic vs manipulated bank statements
"""

import sys
import os

# Add src to path
sys.path.append('src')

from cv_module.ela_detector import ELADetector
from utils.sample_generator import generate_test_samples
import matplotlib.pyplot as plt
from PIL import Image


def run_day1_demo():
    """
    Complete Day 1 demonstration
    """
    print("=" * 60)
    print("TruthLens - Day 1 Fraud Detection Demo")
    print("=" * 60)
    
    # Step 1: Generate sample documents
    print("\n[STEP 1] Generating sample documents...")
    generate_test_samples()
    
    # Step 2: Initialize ELA Detector
    print("\n[STEP 2] Initializing ELA Detector...")
    detector = ELADetector(quality=95)
    print("✅ Detector ready!")
    
    # Step 3: Test on authentic document
    print("\n[STEP 3] Analyzing AUTHENTIC bank statement...")
    authentic_path = 'data/sample_documents/bank_statement_authentic.jpg'
    result_authentic = detector.detect(
        authentic_path,
        output_path='data/sample_documents/ela_authentic.jpg'
    )
    
    print(f"   Fraud Score: {result_authentic['fraud_score']}/100")
    print(f"   Mean ELA: {result_authentic['mean_ela']}")
    print(f"   Assessment: {result_authentic['interpretation']}")
    
    # Step 4: Test on manipulated document
    print("\n[STEP 4] Analyzing MANIPULATED bank statement...")
    fake_path = 'data/sample_documents/bank_statement_fake.jpg'
    result_fake = detector.detect(
        fake_path,
        output_path='data/sample_documents/ela_fake.jpg'
    )
    
    print(f"   Fraud Score: {result_fake['fraud_score']}/100")
    print(f"   Mean ELA: {result_fake['mean_ela']}")
    print(f"   Assessment: {result_fake['interpretation']}")
    
    # Step 5: Visual comparison
    print("\n[STEP 5] Generating visual comparison...")
    visualize_results(authentic_path, fake_path, result_authentic, result_fake)
    
    print("\n" + "=" * 60)
    print("✅ DAY 1 DEMO COMPLETE!")
    print("=" * 60)
    print(f"\nResults:")
    print(f"  Authentic document: {result_authentic['fraud_score']}/100")
    print(f"  Manipulated document: {result_fake['fraud_score']}/100")
    print(f"\n📊 Visualization saved: fraud_detection_results.png")


def visualize_results(authentic_path, fake_path, result_auth, result_fake):
    """
    Create side-by-side comparison visualization
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # Load images
    img_auth = Image.open(authentic_path)
    img_fake = Image.open(fake_path)
    
    # Row 1: Authentic document
    axes[0, 0].imshow(img_auth)
    axes[0, 0].set_title('Original: AUTHENTIC', fontsize=14, fontweight='bold')
    axes[0, 0].axis('off')
    
    axes[0, 1].imshow(result_auth['ela_image'])
    axes[0, 1].set_title(f"ELA Analysis\nScore: {result_auth['fraud_score']}/100", fontsize=12)
    axes[0, 1].axis('off')
    
    axes[0, 2].text(0.5, 0.5, f"{result_auth['interpretation']}\n\nMean ELA: {result_auth['mean_ela']}\nMax ELA: {result_auth['max_ela']}", 
                    ha='center', va='center', fontsize=11, wrap=True)
    axes[0, 2].axis('off')
    
    # Row 2: Manipulated document
    axes[1, 0].imshow(img_fake)
    axes[1, 0].set_title('Original: MANIPULATED', fontsize=14, fontweight='bold', color='red')
    axes[1, 0].axis('off')
    
    axes[1, 1].imshow(result_fake['ela_image'])
    axes[1, 1].set_title(f"ELA Analysis\nScore: {result_fake['fraud_score']}/100", fontsize=12, color='red')
    axes[1, 1].axis('off')
    
    axes[1, 2].text(0.5, 0.5, f"{result_fake['interpretation']}\n\nMean ELA: {result_fake['mean_ela']}\nMax ELA: {result_fake['max_ela']}", 
                    ha='center', va='center', fontsize=11, color='red', wrap=True)
    axes[1, 2].axis('off')
    
    plt.tight_layout()
    plt.savefig('fraud_detection_results.png', dpi=150, bbox_inches='tight')
    print("✅ Visualization saved: fraud_detection_results.png")


if __name__ == "__main__":
    run_day1_demo()