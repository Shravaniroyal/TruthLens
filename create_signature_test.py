"""
Create test document with duplicated signature
This will clearly demonstrate segmentation benefits:
- Text areas will be excluded (no false positives)
- Duplicated signature will be detected (true positive)
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_document_with_signature_duplication():
    """
    Create a clean document with text and a duplicated signature
    """
    width, height = 800, 600
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 28)
        text_font = ImageFont.truetype("arial.ttf", 18)
        sig_font = ImageFont.truetype("arial.ttf", 14)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        sig_font = ImageFont.load_default()
    
    # Header
    draw.rectangle([(0, 0), (width, 60)], fill='#34495e')
    draw.text((50, 18), "EMPLOYMENT VERIFICATION", fill='white', font=title_font)
    
    # Body text (will be excluded by segmentation)
    y = 100
    draw.text((50, y), "Employee Name: John Doe", fill='black', font=text_font)
    y += 40
    draw.text((50, y), "Employee ID: EMP12345", fill='black', font=text_font)
    y += 40
    draw.text((50, y), "Department: Engineering", fill='black', font=text_font)
    y += 40
    draw.text((50, y), "Join Date: January 1, 2024", fill='black', font=text_font)
    y += 40
    draw.text((50, y), "Salary: $75,000 per annum", fill='black', font=text_font)
    
    # Create UNIQUE signature pattern (not geometric - more realistic)
    def draw_signature(x_offset, y_offset, color='blue'):
        """Draw a signature-like pattern"""
        sig_img = Image.new('RGBA', (180, 60), (255, 255, 255, 0))
        sig_draw = ImageDraw.Draw(sig_img)
        
        # Signature line (handwriting-like curve)
        points = [
            (10, 35), (25, 25), (40, 30), (55, 20), 
            (70, 28), (85, 22), (100, 30), (115, 25),
            (130, 32), (145, 28), (160, 35)
        ]
        sig_draw.line(points, fill=color, width=3)
        
        # Add signature text
        sig_draw.text((45, 40), "J. Doe", fill=color, font=sig_font)
        
        # Add small circle (like a signature dot)
        sig_draw.ellipse([(5, 30), (15, 40)], fill=color)
        
        return sig_img
    
    # Signature 1: Employee signature (left side)
    sig1 = draw_signature(0, 0, 'blue')
    image.paste(sig1, (80, 450), sig1)
    draw.text((80, 520), "Employee Signature", fill='black', font=sig_font)
    
    # Signature 2: Manager signature (right side) 
    # THIS IS THE DUPLICATE (fraud simulation)
    sig2 = draw_signature(0, 0, 'blue')  # Same signature!
    image.paste(sig2, (500, 450), sig2)
    draw.text((500, 520), "Manager Signature", fill='black', font=sig_font)
    
    # Save
    output_dir = 'data/sample_documents'
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, 'signature_duplication_test.jpg')
    image.save(path, 'JPEG', quality=95)
    
    print(f"✅ Created: {path}")
    print("   This document has:")
    print("   - Text content (Employee info)")
    print("   - TWO IDENTICAL signatures (fraud simulation)")
    print("   - Employee signature copied to Manager position!")
    
    return path


if __name__ == "__main__":
    print("Creating signature duplication test document...")
    print("-" * 60)
    create_document_with_signature_duplication()
    print("-" * 60)