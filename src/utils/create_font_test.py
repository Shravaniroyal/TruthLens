"""
Create test documents with font inconsistencies
Simulates copy-paste fraud where text from different sources is mixed.
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_consistent_font_document():
    """
    Create document with single consistent font (authentic)
    """
    width, height = 800, 600
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Use single font throughout
    try:
        font_title = ImageFont.truetype("arial.ttf", 32)
        font_body = ImageFont.truetype("arial.ttf", 20)
    except:
        font_title = ImageFont.load_default()
        font_body = ImageFont.load_default()
    
    # Draw content with consistent font
    y = 50
    draw.text((50, y), "EMPLOYMENT AGREEMENT", fill='black', font=font_title)
    
    y += 80
    draw.text((50, y), "This agreement is made on January 1, 2024", fill='black', font=font_body)
    y += 40
    draw.text((50, y), "Between: ABC Corporation", fill='black', font=font_body)
    y += 40
    draw.text((50, y), "And: John Doe", fill='black', font=font_body)
    y += 60
    draw.text((50, y), "Position: Software Engineer", fill='black', font=font_body)
    y += 40
    draw.text((50, y), "Salary: $80,000 per annum", fill='black', font=font_body)
    y += 40
    draw.text((50, y), "Start Date: February 1, 2024", fill='black', font=font_body)
    
    # Save
    output_dir = 'data/sample_documents'
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, 'contract_consistent_font.jpg')
    image.save(path, 'JPEG', quality=95)
    
    print(f"✅ Created authentic (consistent font): {path}")
    return path


def create_mixed_font_document():
    """
    Create document with MIXED fonts (fraudulent copy-paste)
    """
    width, height = 800, 600
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    # Use DIFFERENT fonts (simulating copy-paste from multiple sources)
    try:
        font_title = ImageFont.truetype("arial.ttf", 32)
        font_body1 = ImageFont.truetype("arial.ttf", 20)
        font_body2 = ImageFont.truetype("times.ttf", 22)  # DIFFERENT FONT!
        font_body3 = ImageFont.truetype("arial.ttf", 18)  # DIFFERENT SIZE!
    except:
        font_title = ImageFont.load_default()
        font_body1 = ImageFont.load_default()
        font_body2 = ImageFont.load_default()
        font_body3 = ImageFont.load_default()
    
    # Draw content with MIXED fonts
    y = 50
    draw.text((50, y), "EMPLOYMENT AGREEMENT", fill='black', font=font_title)
    
    y += 80
    draw.text((50, y), "This agreement is made on January 1, 2024", fill='black', font=font_body1)
    y += 40
    draw.text((50, y), "Between: ABC Corporation", fill='black', font=font_body1)
    y += 40
    draw.text((50, y), "And: John Doe", fill='black', font=font_body1)
    y += 60
    
    # FRAUD: Copied salary from another document (different font!)
    draw.text((50, y), "Position: Software Engineer", fill='black', font=font_body2)
    y += 40
    draw.text((50, y), "Salary: $180,000 per annum", fill='black', font=font_body2)
    y += 40
    
    # Back to original font
    draw.text((50, y), "Start Date: February 1, 2024", fill='black', font=font_body3)
    
    # Save
    path = os.path.join('data/sample_documents', 'contract_mixed_fonts.jpg')
    image.save(path, 'JPEG', quality=95)
    
    print(f"✅ Created FAKE (mixed fonts): {path}")
    print(f"   → Lines 5-6 use Times New Roman (copied from another doc!)")
    print(f"   → Salary changed from $80k to $180k")
    return path


def generate_font_test_samples():
    """
    Generate test samples for font analysis
    """
    print("Generating font consistency test documents...")
    print("-" * 60)
    
    authentic = create_consistent_font_document()
    fake = create_mixed_font_document()
    
    print("-" * 60)
    print("✅ Font test samples created!")
    print(f"📁 Location: data/sample_documents/")
    print(f"   - contract_consistent_font.jpg (AUTHENTIC)")
    print(f"   - contract_mixed_fonts.jpg (FAKE - mixed fonts)")


if __name__ == "__main__":
    generate_font_test_samples()