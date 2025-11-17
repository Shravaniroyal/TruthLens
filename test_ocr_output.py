"""
Quick test to see what OCR is detecting
"""

import sys
sys.path.append('src')

import pytesseract
from PIL import Image

def check_ocr():
    """
    See what text OCR detects
    """
    print("Checking OCR detection...")
    print("="*60)
    
    # Test on authentic
    print("\nAUTHENTIC DOCUMENT:")
    img = Image.open('data/sample_documents/contract_consistent_font.jpg')
    text = pytesseract.image_to_string(img)
    print(text)
    
    print("\n" + "="*60)
    print("\nFAKE DOCUMENT:")
    img2 = Image.open('data/sample_documents/contract_mixed_fonts.jpg')
    text2 = pytesseract.image_to_string(img2)
    print(text2)
    
    print("\n" + "="*60)
    
    # Get detailed data
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
    
    print("\nDETAILED OCR DATA (first 10 detections):")
    print(f"{'Text':<30} {'Height':<10} {'Confidence':<12}")
    print("-"*60)
    
    count = 0
    for i in range(len(data['text'])):
        if data['text'][i].strip() and int(data['conf'][i]) > 0:
            print(f"{data['text'][i]:<30} {data['height'][i]:<10} {data['conf'][i]:<12}")
            count += 1
            if count >= 10:
                break

if __name__ == "__main__":
    check_ocr()