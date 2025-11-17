"""
Create test images with copy-move forgery
Generates documents with duplicated signatures for testing.
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os


def create_document_with_signature():
    """
    Create a simple document with a signature
    """
    # Create white canvas
    width, height = 800, 600
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("arial.ttf", 24)
        title_font = ImageFont.truetype("arial.ttf", 32)
    except:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    
    # Draw document content
    draw.text((50, 50), "EMPLOYMENT CONTRACT", fill='black', font=title_font)
    draw.text((50, 120), "This agreement is made between:", fill='black', font=font)
    draw.text((50, 160), "Party A: ABC Corporation", fill='black', font=font)
    draw.text((50, 200), "Party B: John Doe", fill='black', font=font)
    
    # Create a simple "signature" (scribble pattern)
    signature_box = Image.new('RGB', (200, 80), 'white')
    sig_draw = ImageDraw.Draw(signature_box)
    
    # Draw signature-like scribble
    sig_draw.line([(20, 40), (50, 20), (80, 50), (110, 25), (140, 45), (170, 30)], 
                  fill='blue', width=3)
    sig_draw.text((50, 55), "John Doe", fill='blue', font=font)
    
    # Paste signature at bottom
    image.paste(signature_box, (100, 450))
    
    # Save authentic version
    output_dir = 'data/sample_documents'
    os.makedirs(output_dir, exist_ok=True)
    authentic_path = os.path.join(output_dir, 'contract_authentic.jpg')
    image.save(authentic_path, 'JPEG', quality=95)
    
    print(f"✅ Created authentic contract: {authentic_path}")
    
    return authentic_path, signature_box


def create_forged_document(authentic_path, signature_box):
    """
    Create forged version with duplicated signature
    """
    # Load authentic document
    image = Image.open(authentic_path)
    
    # PASTE THE SAME SIGNATURE AGAIN (FORGERY!)
    # This simulates someone copying signature to another section
    image.paste(signature_box, (450, 450))  # Second location
    
    # Save forged version
    forged_path = 'data/sample_documents/contract_forged_copymove.jpg'
    image.save(forged_path, 'JPEG', quality=95)
    
    print(f"✅ Created forged contract (duplicated signature): {forged_path}")
    print("   → Same signature appears at TWO locations!")
    
    return forged_path


def generate_copymove_samples():
    """
    Generate test samples for copy-move detection
    """
    print("Generating copy-move test documents...")
    print("-" * 60)
    
    # Create authentic document with signature
    authentic_path, signature_box = create_document_with_signature()
    
    # Create forged version with duplicated signature
    forged_path = create_forged_document(authentic_path, signature_box)
    
    print("-" * 60)
    print("✅ Copy-move test samples created!")
    print(f"📁 Location: data/sample_documents/")
    print(f"   - contract_authentic.jpg (REAL - 1 signature)")
    print(f"   - contract_forged_copymove.jpg (FAKE - duplicated signature)")


if __name__ == "__main__":
    generate_copymove_samples()