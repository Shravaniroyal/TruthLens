from PIL import Image, ImageFilter, ImageEnhance, ImageDraw
import os, random, shutil
from pathlib import Path

REAL_BASE = r"C:\Users\Shravani\TruthLens\industry_datasets\real_documents"
FAKE_BASE = r"C:\Users\Shravani\TruthLens\industry_datasets\fake_documents"

categories = [
    "id_cards", "certificates", "bank_statements",
    "invoices", "payslips", "experience_letters", "marksheets"
]

def create_fake(img_path, out_path):
    img = Image.open(img_path).convert("RGB")
    w, h = img.size
    
    # Pick 2-3 random tampering methods
    methods = random.sample([
        "blur_region",
        "brightness_patch",
        "noise",
        "compression",
        "erase_patch",
        "contrast_change"
    ], k=random.randint(2, 3))
    
    for method in methods:
        if method == "blur_region":
            # Blur a random region (simulates edited text)
            x1 = random.randint(0, w//2)
            y1 = random.randint(0, h//2)
            x2 = x1 + random.randint(w//6, w//3)
            y2 = y1 + random.randint(h//8, h//4)
            region = img.crop((x1, y1, x2, y2))
            region = region.filter(ImageFilter.GaussianBlur(radius=3))
            img.paste(region, (x1, y1, x2, y2))
            
        elif method == "brightness_patch":
            # Brighter/darker patch (simulates pasted content)
            x1 = random.randint(0, w//2)
            y1 = random.randint(0, h//2)
            x2 = x1 + random.randint(w//8, w//4)
            y2 = y1 + random.randint(h//8, h//5)
            region = img.crop((x1, y1, x2, y2))
            factor = random.choice([0.6, 0.7, 1.4, 1.5])
            region = ImageEnhance.Brightness(region).enhance(factor)
            img.paste(region, (x1, y1, x2, y2))
            
        elif method == "noise":
            # Save with low quality (compression artifacts)
            temp = r"C:\Users\Shravani\TruthLens\temp_fake.jpg"
            img.save(temp, quality=random.randint(40, 65))
            img = Image.open(temp)
            
        elif method == "compression":
            temp = r"C:\Users\Shravani\TruthLens\temp_fake.jpg"
            img.save(temp, quality=random.randint(30, 55))
            img = Image.open(temp)
            
        elif method == "erase_patch":
            # White/grey rectangle (simulates erased content)
            draw = ImageDraw.Draw(img)
            x1 = random.randint(w//6, w//2)
            y1 = random.randint(h//6, h//2)
            x2 = x1 + random.randint(w//10, w//5)
            y2 = y1 + random.randint(h//15, h//8)
            color = random.randint(200, 255)
            draw.rectangle([x1, y1, x2, y2], fill=(color, color, color))
            
        elif method == "contrast_change":
            x1 = random.randint(0, w//3)
            y1 = random.randint(0, h//3)
            x2 = x1 + random.randint(w//5, w//3)
            y2 = y1 + random.randint(h//6, h//4)
            region = img.crop((x1, y1, x2, y2))
            factor = random.choice([0.5, 0.6, 1.8, 2.0])
            region = ImageEnhance.Contrast(region).enhance(factor)
            img.paste(region, (x1, y1, x2, y2))
    
    img.save(out_path, quality=85)

# Process all categories
total = 0
for category in categories:
    real_folder = os.path.join(REAL_BASE, category)
    fake_folder = os.path.join(FAKE_BASE, category)
    os.makedirs(fake_folder, exist_ok=True)
    
    real_images = [f for f in os.listdir(real_folder) 
                   if f.lower().endswith(('.jpg','.jpeg','.png'))]
    
    print(f"\nProcessing {category}: {len(real_images)} images")
    
    count = 0
    for img_file in real_images:
        src = os.path.join(real_folder, img_file)
        out_name = f"fake_{img_file}"
        dst = os.path.join(fake_folder, out_name)
        try:
            create_fake(src, dst)
            count += 1
        except Exception as e:
            pass
    
    print(f"  Created {count} fake images")
    total += count

# Cleanup
temp = r"C:\Users\Shravani\TruthLens\temp_fake.jpg"
if os.path.exists(temp):
    os.remove(temp)

print(f"\n{'='*50}")
print(f"DONE! Total fake documents created: {total}")
print(f"{'='*50}")
print(f"\nFinal dataset:")
for cat in categories:
    r = len([f for f in os.listdir(os.path.join(REAL_BASE,cat)) if f.lower().endswith(('.jpg','.jpeg','.png'))])
    f = len([f for f in os.listdir(os.path.join(FAKE_BASE,cat)) if f.lower().endswith(('.jpg','.jpeg','.png'))])
    print(f"  {cat}: {r} real | {f} fake")
