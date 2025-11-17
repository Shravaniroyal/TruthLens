"""
Create sample test documents for fraud detection testing
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_fake_bank_statement():
    """Create a simple fake bank statement for testing"""
    
    # Create blank white image (A4 aspect ratio)
    width, height = 800, 1000
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Add header
    draw.rectangle([0, 0, width, 100], fill='#0066cc')
    draw.text((20, 30), "STATE BANK OF EXAMPLE", fill='white', 
              font=ImageFont.load_default())
    
    # Add account details
    y_position = 150
    details = [
        "Account Statement",
        "Account Number: 1234567890",
        "Account Holder: John Doe",
        "Period: Jan 2024 - Mar 2024",
        "",
        "Opening Balance: ₹50,000.00",
        "",
        "TRANSACTIONS:",
        "01-Jan-2024  Salary Credit      ₹75,000.00",
        "05-Jan-2024  ATM Withdrawal     ₹5,000.00",
        "15-Jan-2024  Online Transfer    ₹10,000.00",
        "",
        "Closing Balance: ₹110,000.00"
    ]
    
    for line in details:
        draw.text((50, y_position), line, fill='black', 
                  font=ImageFont.load_default())
        y_position += 40
    
    # Save as JPEG
    output_path = "data/sample_documents/authentic_bank_statement.jpg"
    img.save(output_path, 'JPEG', quality=90)
    print(f"✅ Created: {output_path}")
    
    return output_path


def create_fake_degree():
    """Create a simple fake degree certificate"""
    
    width, height = 1000, 700
    img = Image.new('RGB', (width, height), color='#fffef0')
    draw = ImageDraw.Draw(img)
    
    # Border
    draw.rectangle([20, 20, width-20, height-20], outline='#8B4513', width=5)
    
    # Header
    draw.text((width//2 - 150, 80), "UNIVERSITY OF EXAMPLE", 
              fill='#8B4513', font=ImageFont.load_default())
    
    # Certificate text
    y_pos = 200
    lines = [
        "BACHELOR OF TECHNOLOGY",
        "",
        "This is to certify that",
        "",
        "JOHN DOE",
        "",
        "has successfully completed the degree of",
        "Bachelor of Technology in Computer Science",
        "",
        "with First Class Honors",
        "",
        "Date: 15th May 2024",
        "Registration No: 2020/CSE/001"
    ]
    
    for line in lines:
        draw.text((width//2 - 200, y_pos), line, fill='black',
                  font=ImageFont.load_default())
        y_pos += 35
    
    output_path = "data/sample_documents/authentic_degree.jpg"
    img.save(output_path, 'JPEG', quality=90)
    print(f"✅ Created: {output_path}")
    
    return output_path


def create_manipulated_document(original_path):
    """
    Create a manipulated version by editing and re-saving
    (simulates Photoshop editing)
    """
    
    img = Image.open(original_path)
    draw = ImageDraw.Draw(img)
    
    # Simulate editing: change some numbers (like someone changing salary amount)
    # This creates compression artifacts that ELA will detect
    draw.rectangle([400, 450, 600, 490], fill='white')
    draw.text((410, 460), "₹150,000.00", fill='black',
              font=ImageFont.load_default())
    
    # Save with different quality (this creates detectable artifacts)
    filename = os.path.basename(original_path)
    name, ext = os.path.splitext(filename)
    output_path = f"data/sample_documents/manipulated_{name}.jpg"
    
    img.save(output_path, 'JPEG', quality=85)
    print(f"✅ Created: {output_path}")
    
    return output_path


if __name__ == "__main__":
    print("Creating test documents...\n")
    
    # Create authentic documents
    bank_statement = create_fake_bank_statement()
    degree = create_fake_degree()
    
    print("\nCreating manipulated versions...\n")
    
    # Create manipulated versions
    manipulated_bank = create_manipulated_document(bank_statement)
    manipulated_degree = create_manipulated_document(degree)
    
    print("\n🎉 All test documents created!")
    print("\nYou now have:")
    print("  - 2 authentic documents")
    print("  - 2 manipulated documents")
    print("\nReady for fraud detection testing!")