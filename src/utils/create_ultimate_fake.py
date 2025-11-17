"""
Create ultimate fake document with ALL fraud types
Triggers: ELA + Copy-Move + Font inconsistencies
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_ultimate_fake():
    """
    Create document with all three fraud types
    """
    width, height = 1000, 800
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    try:
        font_title = ImageFont.truetype("arial.ttf", 36)
        font_normal = ImageFont.truetype("arial.ttf", 22)
        font_fake = ImageFont.truetype("times.ttf", 24)  # Different font for fake parts
    except:
        font_title = ImageFont.load_default()
        font_normal = ImageFont.load_default()
        font_fake = ImageFont.load_default()
    
    # Header
    draw.rectangle([(0, 0), (width, 80)], fill='#2c3e50')
    draw.text((50, 20), "FINANCIAL STATEMENT", fill='white', font=font_title)
    
    y = 120
    draw.text((50, y), "Account: 1234567890", fill='black', font=font_normal)
    y += 40
    draw.text((50, y), "Name: JOHN DOE", fill='black', font=font_normal)
    y += 60
    
    # Transactions (normal font)
    draw.text((50, y), "Date           Description                Amount", fill='black', font=font_normal)
    y += 40
    draw.text((50, y), "Jan 01        Opening Balance            $5,000", fill='black', font=font_normal)
    y += 35
    draw.text((50, y), "Jan 05        Salary Credit              $8,000", fill='black', font=font_normal)
    y += 35
    
    # FRAUD TYPE 1: Changed amount with different font (triggers ELA + Font)
    draw.text((50, y), "Jan 10        Bonus Payment              $25,000", fill='black', font=font_fake)
    y += 35
    
    draw.text((50, y), "Jan 15        Rent Payment               -$1,500", fill='black', font=font_normal)
    y += 60
    
    # FRAUD TYPE 2: Changed balance (triggers ELA)
    draw.rectangle([(50, y), (width-50, y+50)], fill='#ecf0f1')
    
    # Cover and change balance
    draw.rectangle([(600, y+5), (900, y+45)], fill='white')  # White out original
    draw.text((620, y+10), "$86,500", fill='black', font=font_fake)  # Fake amount
    draw.text((70, y+10), "Closing Balance:", fill='black', font=font_normal)
    
    # Create signature
    sig = Image.new('RGB', (150, 50), 'white')
    sig_draw = ImageDraw.Draw(sig)
    sig_draw.line([(10, 25), (35, 15), (60, 30), (90, 20), (120, 28)], fill='blue', width=2)
    sig_draw.text((40, 32), "J. Doe", fill='blue', font=font_normal)
    
    # FRAUD TYPE 3: Duplicate signature (triggers Copy-Move)
    image.paste(sig, (100, 680))  # First signature
    image.paste(sig, (600, 680))  # DUPLICATE signature
    
    # Save
    output_dir = 'data/sample_documents'
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, 'ultimate_fake_all_fraud_types.jpg')
    image.save(path, 'JPEG', quality=90)
    
    print(f"✅ Created ULTIMATE FAKE document: {path}")
    print("   Contains ALL THREE fraud types:")
    print("   1. Compression artifacts (edited balance)")
    print("   2. Duplicated signature (copy-move)")
    print("   3. Mixed fonts (copy-pasted bonus line)")
    
    return path


if __name__ == "__main__":
    print("Creating ultimate fake document...")
    print("-" * 60)
    create_ultimate_fake()
    print("-" * 60)