"""
TruthLens - Synthetic Document Generator
Generates realistic fake documents for training fraud detection model

Creates:
- CVs/Resumes (real and fake versions)
- Certificates (real and fake versions)
- Invoices (real and fake versions)
- ID Cards (real and fake versions)
- Applications (real and fake versions)

Output: 2,000 images (1,000 real-looking, 1,000 fake-looking)
"""

import os
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import sys

# Configuration
OUTPUT_DIR = "industry_datasets/synthetic_data"
TOTAL_DOCUMENTS = 2000
IMAGE_SIZE = (800, 1100)  # A4-like ratio

# Sample data
NAMES = [
    "Rajesh Kumar", "Priya Sharma", "Amit Patel", "Sneha Reddy", "Vikram Singh",
    "Ananya Iyer", "Rahul Verma", "Pooja Gupta", "Karthik Nair", "Divya Menon",
    "Arjun Das", "Kavya Krishnan", "Sanjay Mehta", "Aisha Khan", "Rohan Joshi",
    "Meera Bhat", "Nikhil Rao", "Swati Desai", "Varun Pillai", "Riya Agarwal"
]

COMPANIES = [
    "Infosys", "TCS", "Wipro", "Tech Mahindra", "HCL Technologies",
    "Cognizant", "Amazon India", "Google India", "Microsoft India", "Flipkart",
    "Paytm", "PhonePe", "CRED", "Zomato", "Swiggy", "Ola", "Uber India"
]

SKILLS = [
    "Python", "Java", "Machine Learning", "Data Science", "SQL", "React",
    "Node.js", "AWS", "Docker", "Kubernetes", "TensorFlow", "PyTorch",
    "MongoDB", "PostgreSQL", "Git", "CI/CD", "Agile", "Scrum"
]

UNIVERSITIES = [
    "IIT Bombay", "IIT Delhi", "IIT Madras", "IIIT Bangalore", "IIIT Hyderabad",
    "NIT Trichy", "BITS Pilani", "VIT Vellore", "Manipal Institute", "SRM University"
]

CERTIFICATE_TYPES = [
    "AWS Certified Solutions Architect", "Google Cloud Professional",
    "Microsoft Azure Administrator", "CompTIA Security+", "CISSP",
    "PMP Certification", "Scrum Master Certification", "Data Science Certificate"
]

def create_directories():
    """Create output directories"""
    os.makedirs(f"{OUTPUT_DIR}/real", exist_ok=True)
    os.makedirs(f"{OUTPUT_DIR}/fake", exist_ok=True)
    print(f"✅ Created directories in {OUTPUT_DIR}")

def get_font(size=20):
    """Get font (tries multiple options)"""
    font_options = [
        "arial.ttf",
        "Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:\\Windows\\Fonts\\arial.ttf",
        "C:\\Windows\\Fonts\\calibri.ttf"
    ]
    
    for font_path in font_options:
        try:
            return ImageFont.truetype(font_path, size)
        except:
            continue
    
    return ImageFont.load_default()

def add_noise(image, is_fake=False):
    """Add realistic document noise"""
    if random.random() < 0.3:
        # Add slight blur
        image = image.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5)))
    
    if is_fake and random.random() < 0.5:
        # Add more noise to fake documents
        image = image.filter(ImageFilter.GaussianBlur(radius=random.uniform(2, 4)))
    
    return image

def generate_cv(doc_id, is_fake=False):
    """Generate a CV/Resume"""
    img = Image.new('RGB', IMAGE_SIZE, color='white')
    draw = ImageDraw.Draw(img)
    
    # Fonts
    font_title = get_font(36)
    font_heading = get_font(24)
    font_normal = get_font(18)
    font_small = get_font(14)
    
    y_pos = 50
    name = random.choice(NAMES)
    
    # Header
    draw.text((50, y_pos), name, fill='black', font=font_title)
    y_pos += 60
    
    # Contact info
    email = f"{name.lower().replace(' ', '.')}@email.com"
    phone = f"+91 {''.join([str(random.randint(0,9)) for _ in range(10)])}"
    
    if is_fake:
        # Introduce errors in fake CVs
        if random.random() < 0.5:
            email = email.replace('@', '@@')  # Double @
        if random.random() < 0.5:
            phone = phone[:5] + "XXXX" + phone[9:]  # Suspicious phone
    
    draw.text((50, y_pos), f"Email: {email}", fill='navy', font=font_small)
    y_pos += 25
    draw.text((50, y_pos), f"Phone: {phone}", fill='navy', font=font_small)
    y_pos += 50
    
    # Experience
    draw.text((50, y_pos), "WORK EXPERIENCE", fill='darkblue', font=font_heading)
    y_pos += 40
    
    company = random.choice(COMPANIES)
    role = random.choice(["Software Engineer", "Data Scientist", "ML Engineer", "Full Stack Developer"])
    years = random.randint(1, 5)
    
    if is_fake and random.random() < 0.3:
        # Fake experience - unrealistic years
        years = random.randint(10, 20)  # Too much experience
    
    draw.text((50, y_pos), f"{role} at {company}", fill='black', font=font_normal)
    y_pos += 30
    draw.text((50, y_pos), f"{years} years experience", fill='gray', font=font_small)
    y_pos += 50
    
    # Education
    draw.text((50, y_pos), "EDUCATION", fill='darkblue', font=font_heading)
    y_pos += 40
    
    university = random.choice(UNIVERSITIES)
    degree = "B.Tech in Computer Science"
    year = random.randint(2015, 2023)
    
    if is_fake and random.random() < 0.3:
        # Fake university name
        university = "International " + university + " Online"
        if random.random() < 0.5:
            year = 2030  # Future date
    
    draw.text((50, y_pos), f"{degree}", fill='black', font=font_normal)
    y_pos += 30
    draw.text((50, y_pos), f"{university} ({year})", fill='gray', font=font_small)
    y_pos += 50
    
    # Skills
    draw.text((50, y_pos), "SKILLS", fill='darkblue', font=font_heading)
    y_pos += 40
    
    skills = random.sample(SKILLS, random.randint(5, 8))
    skills_text = ", ".join(skills)
    
    if is_fake and random.random() < 0.3:
        # Add suspicious skills
        skills_text += ", Expert in Everything, 20+ Programming Languages"
    
    draw.text((50, y_pos), skills_text, fill='black', font=font_small)
    
    # Add watermark if fake
    if is_fake and random.random() < 0.3:
        draw.text((IMAGE_SIZE[0] - 200, IMAGE_SIZE[1] - 50), 
                 "DRAFT - NOT VERIFIED", fill='red', font=font_small)
    
    return add_noise(img, is_fake)

def generate_certificate(doc_id, is_fake=False):
    """Generate a certificate"""
    img = Image.new('RGB', IMAGE_SIZE, color='#FFF8DC')  # Cream color
    draw = ImageDraw.Draw(img)
    
    # Border
    draw.rectangle([30, 30, IMAGE_SIZE[0]-30, IMAGE_SIZE[1]-30], 
                   outline='gold', width=5)
    draw.rectangle([40, 40, IMAGE_SIZE[0]-40, IMAGE_SIZE[1]-40], 
                   outline='darkgoldenrod', width=2)
    
    font_title = get_font(48)
    font_name = get_font(36)
    font_normal = get_font(20)
    
    y_pos = 150
    
    # Title
    title = "CERTIFICATE OF ACHIEVEMENT"
    if is_fake and random.random() < 0.3:
        title = "CERTIFICATE OF ACHEIVEMENT"  # Typo
    
    draw.text((IMAGE_SIZE[0]//2 - 200, y_pos), title, fill='darkblue', font=font_title)
    y_pos += 100
    
    # This certifies that
    draw.text((IMAGE_SIZE[0]//2 - 100, y_pos), "This is to certify that", 
             fill='black', font=font_normal)
    y_pos += 60
    
    # Name
    name = random.choice(NAMES)
    draw.text((IMAGE_SIZE[0]//2 - 100, y_pos), name, fill='darkred', font=font_name)
    y_pos += 80
    
    # Certificate type
    cert_type = random.choice(CERTIFICATE_TYPES)
    draw.text((IMAGE_SIZE[0]//2 - 200, y_pos), f"has successfully completed", 
             fill='black', font=font_normal)
    y_pos += 40
    draw.text((IMAGE_SIZE[0]//2 - 150, y_pos), cert_type, 
             fill='black', font=font_normal)
    y_pos += 80
    
    # Date
    date = f"{random.randint(1,28)}/{random.randint(1,12)}/{random.randint(2020,2025)}"
    if is_fake and random.random() < 0.3:
        date = f"{random.randint(1,28)}/{random.randint(1,12)}/2030"  # Future date
    
    draw.text((100, IMAGE_SIZE[1] - 150), f"Date: {date}", fill='black', font=font_normal)
    
    # Signature (fake line)
    if not is_fake or random.random() < 0.7:
        draw.line([(IMAGE_SIZE[0] - 300, IMAGE_SIZE[1] - 150), 
                  (IMAGE_SIZE[0] - 100, IMAGE_SIZE[1] - 150)], 
                 fill='black', width=2)
        draw.text((IMAGE_SIZE[0] - 280, IMAGE_SIZE[1] - 130), 
                 "Authorized Signature", fill='gray', font=get_font(12))
    
    if is_fake and random.random() < 0.3:
        # Add watermark
        draw.text((IMAGE_SIZE[0]//2 - 100, IMAGE_SIZE[1]//2), 
                 "COPY", fill=(255, 0, 0, 50), font=get_font(100))
    
    return add_noise(img, is_fake)

def generate_invoice(doc_id, is_fake=False):
    """Generate an invoice"""
    img = Image.new('RGB', IMAGE_SIZE, color='white')
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(32)
    font_normal = get_font(18)
    font_small = get_font(14)
    
    y_pos = 50
    
    # Header
    company = random.choice(COMPANIES)
    draw.rectangle([0, 0, IMAGE_SIZE[0], 100], fill='darkblue')
    draw.text((50, 30), f"{company} Invoice", fill='white', font=font_title)
    y_pos = 150
    
    # Invoice details
    invoice_num = f"INV-{random.randint(1000, 9999)}"
    date = f"{random.randint(1,28)}/{random.randint(1,12)}/{random.randint(2023,2025)}"
    
    if is_fake and random.random() < 0.3:
        invoice_num = f"INV-{random.randint(1, 99)}"  # Suspiciously low number
    
    draw.text((50, y_pos), f"Invoice #: {invoice_num}", fill='black', font=font_normal)
    y_pos += 30
    draw.text((50, y_pos), f"Date: {date}", fill='black', font=font_normal)
    y_pos += 60
    
    # Bill to
    draw.text((50, y_pos), "Bill To:", fill='darkblue', font=font_normal)
    y_pos += 35
    draw.text((50, y_pos), random.choice(NAMES), fill='black', font=font_small)
    y_pos += 25
    draw.text((50, y_pos), f"{random.randint(1, 999)} MG Road, Bangalore", 
             fill='black', font=font_small)
    y_pos += 60
    
    # Items
    draw.rectangle([50, y_pos, IMAGE_SIZE[0]-50, y_pos+30], fill='lightgray')
    draw.text((60, y_pos+5), "Item", fill='black', font=font_normal)
    draw.text((400, y_pos+5), "Quantity", fill='black', font=font_normal)
    draw.text((550, y_pos+5), "Price", fill='black', font=font_normal)
    y_pos += 40
    
    # Items
    total = 0
    for i in range(random.randint(2, 4)):
        item = f"Service Item {i+1}"
        qty = random.randint(1, 10)
        price = random.randint(1000, 5000)
        
        if is_fake and random.random() < 0.3 and i == 0:
            price = random.randint(100000, 500000)  # Unrealistically high
        
        draw.text((60, y_pos), item, fill='black', font=font_small)
        draw.text((400, y_pos), str(qty), fill='black', font=font_small)
        draw.text((550, y_pos), f"₹{price}", fill='black', font=font_small)
        total += qty * price
        y_pos += 30
    
    # Total
    y_pos += 30
    draw.rectangle([400, y_pos, IMAGE_SIZE[0]-50, y_pos+40], fill='lightblue')
    draw.text((420, y_pos+10), f"Total: ₹{total}", fill='darkblue', font=font_normal)
    
    if is_fake and random.random() < 0.3:
        # Add suspicious text
        draw.text((50, IMAGE_SIZE[1] - 80), 
                 "PAYMENT NOT VERIFIED", fill='red', font=font_small)
    
    return add_noise(img, is_fake)

def generate_id_card(doc_id, is_fake=False):
    """Generate an ID card"""
    img = Image.new('RGB', (IMAGE_SIZE[1], IMAGE_SIZE[0]), color='white')  # Landscape
    draw = ImageDraw.Draw(img)
    
    # Border
    draw.rectangle([20, 20, img.size[0]-20, img.size[1]-20], 
                   outline='blue', width=3)
    
    font_title = get_font(28)
    font_normal = get_font(20)
    font_small = get_font(16)
    
    # Header
    company = random.choice(COMPANIES)
    draw.rectangle([0, 0, img.size[0], 80], fill='darkblue')
    draw.text((50, 25), f"{company} Employee ID", fill='white', font=font_title)
    
    y_pos = 120
    
    # Photo placeholder
    draw.rectangle([50, y_pos, 200, y_pos+150], fill='lightgray', outline='black')
    draw.text((90, y_pos+60), "PHOTO", fill='black', font=font_normal)
    
    # Details
    x_pos = 230
    name = random.choice(NAMES)
    emp_id = f"EMP{random.randint(1000, 9999)}"
    dept = random.choice(["Engineering", "Marketing", "Sales", "HR", "Finance"])
    
    if is_fake and random.random() < 0.3:
        emp_id = f"EMP00{random.randint(1, 9)}"  # Suspiciously low ID
    
    draw.text((x_pos, y_pos), "Name:", fill='darkblue', font=font_normal)
    draw.text((x_pos+100, y_pos), name, fill='black', font=font_normal)
    y_pos += 40
    
    draw.text((x_pos, y_pos), "ID:", fill='darkblue', font=font_normal)
    draw.text((x_pos+100, y_pos), emp_id, fill='black', font=font_normal)
    y_pos += 40
    
    draw.text((x_pos, y_pos), "Department:", fill='darkblue', font=font_normal)
    draw.text((x_pos+150, y_pos), dept, fill='black', font=font_normal)
    y_pos += 40
    
    # Valid until
    year = random.randint(2024, 2026)
    if is_fake and random.random() < 0.3:
        year = 2020  # Expired
    
    draw.text((x_pos, y_pos), f"Valid Until: 31/12/{year}", fill='gray', font=font_small)
    
    if is_fake and random.random() < 0.3:
        draw.text((img.size[0] - 200, img.size[1] - 50), 
                 "DUPLICATE", fill='red', font=font_normal)
    
    return add_noise(img, is_fake)

def generate_application(doc_id, is_fake=False):
    """Generate an application form"""
    img = Image.new('RGB', IMAGE_SIZE, color='white')
    draw = ImageDraw.Draw(img)
    
    font_title = get_font(32)
    font_normal = get_font(18)
    font_small = get_font(14)
    
    y_pos = 50
    
    # Title
    draw.text((IMAGE_SIZE[0]//2 - 150, y_pos), "APPLICATION FORM", 
             fill='darkblue', font=font_title)
    y_pos += 80
    
    # Form fields
    name = random.choice(NAMES)
    email = f"{name.lower().replace(' ', '.')}@email.com"
    phone = f"+91 {''.join([str(random.randint(0,9)) for _ in range(10)])}"
    
    if is_fake:
        if random.random() < 0.3:
            email = "invalid.email"  # Missing @
        if random.random() < 0.3:
            phone = "+91 123"  # Incomplete phone
    
    draw.text((50, y_pos), "Full Name:", fill='black', font=font_normal)
    draw.rectangle([200, y_pos, IMAGE_SIZE[0]-50, y_pos+30], outline='black')
    draw.text((210, y_pos+5), name, fill='black', font=font_small)
    y_pos += 50
    
    draw.text((50, y_pos), "Email:", fill='black', font=font_normal)
    draw.rectangle([200, y_pos, IMAGE_SIZE[0]-50, y_pos+30], outline='black')
    draw.text((210, y_pos+5), email, fill='black', font=font_small)
    y_pos += 50
    
    draw.text((50, y_pos), "Phone:", fill='black', font=font_normal)
    draw.rectangle([200, y_pos, IMAGE_SIZE[0]-50, y_pos+30], outline='black')
    draw.text((210, y_pos+5), phone, fill='black', font=font_small)
    y_pos += 50
    
    draw.text((50, y_pos), "Address:", fill='black', font=font_normal)
    draw.rectangle([200, y_pos, IMAGE_SIZE[0]-50, y_pos+80], outline='black')
    address = f"{random.randint(1, 999)} MG Road, Bangalore, Karnataka"
    draw.text((210, y_pos+5), address, fill='black', font=font_small)
    y_pos += 100
    
    # Signature
    draw.text((50, y_pos), "Signature:", fill='black', font=font_normal)
    draw.line([(200, y_pos+20), (450, y_pos+20)], fill='black', width=2)
    y_pos += 50
    
    # Date
    date = f"{random.randint(1,28)}/{random.randint(1,12)}/{random.randint(2023,2025)}"
    if is_fake and random.random() < 0.3:
        date = "32/13/2025"  # Invalid date
    
    draw.text((50, y_pos), f"Date: {date}", fill='black', font=font_normal)
    
    if is_fake and random.random() < 0.3:
        draw.text((IMAGE_SIZE[0] - 250, IMAGE_SIZE[1] - 50), 
                 "INCOMPLETE SUBMISSION", fill='red', font=font_small)
    
    return add_noise(img, is_fake)

def generate_documents():
    """Main generation function"""
    print("\n" + "="*80)
    print("STARTING SYNTHETIC DOCUMENT GENERATION")
    print("="*80)
    
    create_directories()
    
    doc_types = ['cv', 'certificate', 'invoice', 'id_card', 'application']
    docs_per_type = TOTAL_DOCUMENTS // len(doc_types)
    
    generators = {
        'cv': generate_cv,
        'certificate': generate_certificate,
        'invoice': generate_invoice,
        'id_card': generate_id_card,
        'application': generate_application
    }
    
    doc_id = 1
    
    for doc_type in doc_types:
        print(f"\n📄 Generating {doc_type.upper()} documents...")
        
        # Half real, half fake
        real_count = docs_per_type // 2
        fake_count = docs_per_type - real_count
        
        # Generate real documents
        for i in range(real_count):
            try:
                img = generators[doc_type](doc_id, is_fake=False)
                filename = f"{OUTPUT_DIR}/real/{doc_type}_{doc_id:04d}.jpg"
                img.save(filename)
                
                if (i + 1) % 50 == 0:
                    print(f"   ✅ Real {doc_type}: {i+1}/{real_count}")
                
                doc_id += 1
            except Exception as e:
                print(f"   ⚠️ Error generating real {doc_type} {doc_id}: {e}")
        
        # Generate fake documents
        for i in range(fake_count):
            try:
                img = generators[doc_type](doc_id, is_fake=True)
                filename = f"{OUTPUT_DIR}/fake/{doc_type}_{doc_id:04d}.jpg"
                img.save(filename)
                
                if (i + 1) % 50 == 0:
                    print(f"   ✅ Fake {doc_type}: {i+1}/{fake_count}")
                
                doc_id += 1
            except Exception as e:
                print(f"   ⚠️ Error generating fake {doc_type} {doc_id}: {e}")
        
        print(f"   ✅ Completed {doc_type}: {docs_per_type} documents")
    
    print("\n" + "="*80)
    print("GENERATION COMPLETE!")
    print("="*80)
    
    # Count files
    real_count = len([f for f in os.listdir(f"{OUTPUT_DIR}/real") if f.endswith('.jpg')])
    fake_count = len([f for f in os.listdir(f"{OUTPUT_DIR}/fake") if f.endswith('.jpg')])
    
    print(f"\n📊 Summary:")
    print(f"   Real documents: {real_count}")
    print(f"   Fake documents: {fake_count}")
    print(f"   Total: {real_count + fake_count}")
    print(f"\n📁 Saved to: {OUTPUT_DIR}")
    
    return real_count + fake_count

def main():
    """Main entry point"""
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║         TruthLens - Synthetic Document Generator               ║
    ║         Creates 2,000 realistic document images                ║
    ╚════════════════════════════════════════════════════════════════╝
    
    This will generate:
    - 400 CVs (200 real-looking, 200 fake-looking)
    - 400 Certificates (200 real, 200 fake)
    - 400 Invoices (200 real, 200 fake)
    - 400 ID Cards (200 real, 200 fake)
    - 400 Applications (200 real, 200 fake)
    
    Total: 2,000 documents
    Time: 15-30 minutes (depending on your computer)
    
    Output directory: industry_datasets/synthetic_data/
    """)
    
    confirm = input("Start generation? (y/n): ").lower()
    
    if confirm != 'y':
        print("Cancelled.")
        return
    
    print("\n⏳ Starting generation...")
    print("   (This will take 15-30 minutes - be patient!)\n")
    
    try:
        total = generate_documents()
        
        print("\n" + "="*80)
        print("✅ SUCCESS!")
        print("="*80)
        print(f"\nGenerated {total} synthetic documents!")
        print(f"\nCombined with your 669 MIDV-2020 images:")
        print(f"TOTAL: {669 + total} images ✅")
        print("\n🎉 YOU'RE READY TO START TRAINING!")
        
        print("\n" + "="*80)
        print("NEXT STEPS:")
        print("="*80)
        print("""
        1. Run: python verify_datasets.py
           (Check that all images are there)
        
        2. Organize data into train/val/test splits
           (We'll do this next)
        
        3. Start fine-tuning in Google Colab
           (I'll create the notebook for you)
        """)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Generation interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        print("   Try running again or check for missing dependencies")

if __name__ == "__main__":
    main()