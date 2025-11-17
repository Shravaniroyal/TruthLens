"""
Sample Document Generator
Creates authentic and manipulated sample documents for testing.
"""

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os


class SampleDocumentGenerator:
    """
    Generates sample financial documents (bank statements, invoices, etc.)
    for testing fraud detection algorithms.
    """
    
    def __init__(self, output_dir='data/sample_documents'):
        """
        Initialize generator
        
        Args:
            output_dir (str): Directory to save generated documents
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    
    def create_simple_bank_statement(self, filename='bank_statement_authentic.jpg'):
        """
        Creates a simple bank statement image for testing
        
        Args:
            filename (str): Output filename
        
        Returns:
            str: Path to created file
        """
        # Create blank white image (A4 size at 150 DPI)
        width, height = 1240, 1754
        image = Image.new('RGB', (width, height), 'white')
        draw = ImageDraw.Draw(image)
        
        # Try to use a system font, fallback to default
        try:
            title_font = ImageFont.truetype("arial.ttf", 40)
            header_font = ImageFont.truetype("arial.ttf", 30)
            text_font = ImageFont.truetype("arial.ttf", 24)
        except:
            # Fallback to default font if Arial not found
            title_font = ImageFont.load_default()
            header_font = ImageFont.load_default()
            text_font = ImageFont.load_default()
        
        # Draw bank header
        draw.rectangle([(0, 0), (width, 100)], fill='#1a5490')
        draw.text((50, 30), "STATE BANK OF INDIA", fill='white', font=title_font)
        
        # Account details
        y_position = 150
        draw.text((50, y_position), "Account Statement", fill='black', font=header_font)
        
        y_position += 80
        draw.text((50, y_position), "Account Number: 1234567890", fill='black', font=text_font)
        y_position += 40
        draw.text((50, y_position), "Account Holder: JOHN DOE", fill='black', font=text_font)
        y_position += 40
        draw.text((50, y_position), "Period: Jan 01, 2024 - Jan 31, 2024", fill='black', font=text_font)
        
        # Transaction table header
        y_position += 80
        draw.rectangle([(50, y_position), (width-50, y_position+50)], fill='#e0e0e0')
        draw.text((70, y_position+10), "Date", fill='black', font=text_font)
        draw.text((300, y_position+10), "Description", fill='black', font=text_font)
        draw.text((800, y_position+10), "Debit", fill='black', font=text_font)
        draw.text((1000, y_position+10), "Credit", fill='black', font=text_font)
        
        # Sample transactions
        transactions = [
            ("Jan 05", "Salary Credit", "", "50,000.00"),
            ("Jan 07", "ATM Withdrawal", "5,000.00", ""),
            ("Jan 12", "Online Purchase", "2,500.00", ""),
            ("Jan 15", "Electricity Bill", "1,200.00", ""),
            ("Jan 20", "Grocery Store", "3,500.00", ""),
        ]
        
        y_position += 60
        for date, desc, debit, credit in transactions:
            draw.text((70, y_position), date, fill='black', font=text_font)
            draw.text((300, y_position), desc, fill='black', font=text_font)
            draw.text((800, y_position), debit, fill='black', font=text_font)
            draw.text((1000, y_position), credit, fill='black', font=text_font)
            y_position += 50
        
        # Balance
        y_position += 30
        draw.rectangle([(50, y_position), (width-50, y_position+50)], fill='#f0f0f0')
        draw.text((70, y_position+10), "Closing Balance: Rs 37,800.00", fill='black', font=header_font)
        
        # Save
        output_path = os.path.join(self.output_dir, filename)
        image.save(output_path, 'JPEG', quality=95)
        
        print(f"✅ Created: {output_path}")
        return output_path
    
    
    def create_manipulated_version(self, authentic_path, output_filename='bank_statement_fake.jpg'):
        """
        Creates a manipulated version of a document
        (simulates Photoshop editing by changing text)
        
        Args:
            authentic_path (str): Path to authentic document
            output_filename (str): Output filename for fake version
        
        Returns:
            str: Path to manipulated file
        """
        # Load authentic image
        image = Image.open(authentic_path)
        draw = ImageDraw.Draw(image)
        
        try:
            text_font = ImageFont.truetype("arial.ttf", 24)
        except:
            text_font = ImageFont.load_default()
        
        # Simulate manipulation: Change closing balance
        # Cover original balance with white rectangle
        draw.rectangle([(950, 950), (1150, 1000)], fill='white')
        
        # Write fake amount (different font to simulate copy-paste)
        try:
            fake_font = ImageFont.truetype("times.ttf", 24)  # Different font!
        except:
            fake_font = text_font
        
        draw.text((950, 960), "Rs 87,800.00", fill='black', font=fake_font)
        
        # Save with different compression (typical of edited images)
        output_path = os.path.join(self.output_dir, output_filename)
        image.save(output_path, 'JPEG', quality=90)  # Slightly different quality
        
        print(f"✅ Created manipulated version: {output_path}")
        return output_path


def generate_test_samples():
    """
    Generate test samples for Day 1 demo
    """
    generator = SampleDocumentGenerator()
    
    print("Generating sample documents...")
    
    # Create authentic document
    authentic = generator.create_simple_bank_statement('bank_statement_authentic.jpg')
    
    # Create manipulated version
    fake = generator.create_manipulated_version(authentic, 'bank_statement_fake.jpg')
    
    print("\n✅ Sample documents generated successfully!")
    print(f"📁 Location: data/sample_documents/")
    print(f"   - bank_statement_authentic.jpg (REAL)")
    print(f"   - bank_statement_fake.jpg (MANIPULATED - balance changed)")


if __name__ == "__main__":
    generate_test_samples()