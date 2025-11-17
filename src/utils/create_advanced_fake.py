"""
Create advanced fake document with multiple fraud types
Combines: Text manipulation (ELA) + Signature duplication (Copy-Move)
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_advanced_fake_bank_statement():
    """
    Create bank statement with BOTH types of fraud:
    1. Changed balance (will trigger ELA)
    2. Duplicated signature (will trigger Copy-Move)
    """
    # Create canvas
    width, height = 1000, 800
    image = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(image)
    
    try:
        title_font = ImageFont.truetype("arial.ttf", 36)
        text_font = ImageFont.truetype("arial.ttf", 24)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # Bank header
    draw.rectangle([(0, 0), (width, 80)], fill='#1a5490')
    draw.text((50, 20), "GLOBAL BANK", fill='white', font=title_font)
    
    # Account info
    y = 120
    draw.text((50, y), "Account Statement", fill='black', font=title_font)
    y += 60
    draw.text((50, y), "Account: 9876543210", fill='black', font=text_font)
    y += 40
    draw.text((50, y), "Name: JANE SMITH", fill='black', font=text_font)
    y += 40
    draw.text((50, y), "Period: Jan 2024", fill='black', font=text_font)
    
    # Transactions
    y += 60
    draw.text((50, y), "TRANSACTIONS:", fill='black', font=text_font)
    y += 40
    draw.text((70, y), "Jan 01 - Salary Credit: $8,000", fill='black', font=text_font)
    y += 35
    draw.text((70, y), "Jan 05 - Rent Payment: $1,500", fill='black', font=text_font)
    y += 35
    draw.text((70, y), "Jan 10 - Groceries: $300", fill='black', font=text_font)
    
    # Original balance (we'll manipulate this)
    y += 60
    draw.rectangle([(50, y), (width-50, y+50)], fill='#f0f0f0')
    draw.text((70, y+10), "Closing Balance: $6,200", fill='black', font=title_font)
    
    # Create signature
    sig_img = Image.new('RGB', (200, 60), 'white')
    sig_draw = ImageDraw.Draw(sig_img)
    sig_draw.line([(10, 30), (40, 15), (70, 35), (100, 20), (130, 30), (160, 25)],
                  fill='blue', width=2)
    sig_draw.text((60, 40), "J. Smith", fill='blue', font=text_font)
    
    # Paste signature ONCE (authentic location)
    image.paste(sig_img, (100, 680))
    
    # Save authentic version
    output_dir = 'data/sample_documents'
    os.makedirs(output_dir, exist_ok=True)
    authentic_path = os.path.join(output_dir, 'advanced_bank_authentic.jpg')
    image.save(authentic_path, 'JPEG', quality=95)
    print(f"✅ Created authentic: {authentic_path}")
    
    # NOW CREATE FAKE VERSION WITH BOTH FRAUD TYPES
    
    # FRAUD TYPE 1: Change balance (ELA will catch this)
    draw.rectangle([(50, 372), (width-50, 422)], fill='#f0f0f0')  # Cover old balance
    
    # Use different font to simulate copy-paste (stronger ELA signal)
    try:
        fake_font = ImageFont.truetype("times.ttf", 36)
    except:
        fake_font = title_font
    
    draw.text((70, 382), "Closing Balance: $26,200", fill='black', font=fake_font)
    # Changed from $6,200 to $26,200 (added $20,000!)
    
    # FRAUD TYPE 2: Duplicate signature (Copy-Move will catch this)
    image.paste(sig_img, (500, 680))  # Location 2 (middle)
    image.paste(sig_img, (700, 250))  # Paste signature AGAIN at different location
    
    # Save fake version
    fake_path = os.path.join(output_dir, 'advanced_bank_fake.jpg')
    image.save(fake_path, 'JPEG', quality=90)  # Slightly different quality (realistic)
    print(f"✅ Created FAKE with BOTH fraud types: {fake_path}")
    print(f"   → Balance changed: $6,200 → $26,200 (will trigger ELA)")
    print(f"   → Signature duplicated (will trigger Copy-Move)")
    
    return authentic_path, fake_path


if __name__ == "__main__":
    print("Generating advanced fraud test case...")
    print("-" * 60)
    create_advanced_fake_bank_statement()
    print("-" * 60)
    print("✅ Done!")