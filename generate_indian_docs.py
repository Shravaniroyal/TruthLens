"""
TruthLens — Realistic Indian Document Generator v2
=====================================================
Generates visually accurate synthetic docs matching real Indian government documents:
  • Aadhaar Card  — UIDAI layout, orange header, green stripe, QR code
  • PAN Card      — Income Tax Dept, blue gradient, Ashoka emblem
  • Driving Licence — State-wise Indian Union DL layout

Run:
    .\\venv\\Scripts\\pip.exe install faker pillow numpy
    .\\venv\\Scripts\\python.exe generate_indian_docs.py

Output:
    C:\\Users\\Shravani\\TruthLens\\indian_dataset\\real\\   ← 1200 images
    C:\\Users\\Shravani\\TruthLens\\indian_dataset\\fake\\   ← 1200 images

Tamper types embedded in fake docs (for EfficientNet to learn):
    name / dob / number / marks — each alters a specific field
    The tampered region will have slightly different JPEG artifacts
    (matching what forensic_explainer.py later detects)
"""

import os, io, math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

try:
    from faker import Faker
    fake = Faker('en_IN')
except ImportError:
    raise SystemExit("Run:  .\\venv\\Scripts\\pip.exe install faker")

# ─────────────────────────────────────────────────────────────────────────────
# OUTPUT PATHS
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = r"C:\Users\Shravani\TruthLens\indian_dataset"
REAL_DIR = os.path.join(BASE_DIR, "real")
FAKE_DIR = os.path.join(BASE_DIR, "fake")
os.makedirs(REAL_DIR, exist_ok=True)
os.makedirs(FAKE_DIR, exist_ok=True)

# Card dimensions (landscape, like real physical cards)
CARD_W, CARD_H = 856, 540

# ─────────────────────────────────────────────────────────────────────────────
# COLOUR CONSTANTS  (taken from real doc colour-picks)
# ─────────────────────────────────────────────────────────────────────────────
# Aadhaar
AAD_ORANGE   = (241, 90,  34)
AAD_ORANGE2  = (255, 140, 60)
AAD_GREEN    = (0,   128, 60)
AAD_BLUE     = (0,   80,  160)
AAD_WHITE    = (255, 255, 255)
AAD_CREAM    = (255, 252, 245)

# PAN
PAN_LTBLUE   = (180, 215, 235)
PAN_MIDBLUE  = (100, 165, 210)
PAN_DKBLUE   = (0,   80,  150)
PAN_MAROON   = (140, 0,   20)
PAN_GOLD     = (180, 140, 0)
PAN_BG       = (225, 238, 248)

# DL (Indian Union)
DL_MAROON    = (140, 0,   20)
DL_LTGREEN   = (200, 230, 200)
DL_OLIVE     = (100, 110, 50)
DL_CREAM     = (255, 252, 240)

# ─────────────────────────────────────────────────────────────────────────────
# FONT LOADER
# ─────────────────────────────────────────────────────────────────────────────
def F(size, bold=False):
    for name in (["arialbd.ttf","Arial Bold.ttf","DejaVuSans-Bold.ttf"] if bold
                 else ["arial.ttf","Arial.ttf","DejaVuSans.ttf"]):
        try:
            return ImageFont.truetype(name, size)
        except Exception:
            pass
    return ImageFont.load_default()

# ─────────────────────────────────────────────────────────────────────────────
# DRAWING UTILITIES
# ─────────────────────────────────────────────────────────────────────────────
def draw_qr(draw, x, y, size=90, seed=None):
    """Draw a realistic-looking QR code placeholder."""
    rng = random.Random(seed or random.randint(0, 99999))
    cell = max(4, size // 21)
    cols = size // cell

    # White background
    draw.rectangle([(x, y), (x+size, y+size)], fill='white')

    # Random data cells
    for r in range(cols):
        for c in range(cols):
            if rng.random() > 0.55:
                draw.rectangle(
                    [(x+c*cell, y+r*cell), (x+(c+1)*cell-1, y+(r+1)*cell-1)],
                    fill='black')

    # Three finder-pattern corners  (top-left, top-right, bottom-left)
    for (fx, fy) in [(x, y), (x+size-7*cell, y), (x, y+size-7*cell)]:
        draw.rectangle([(fx,       fy),       (fx+7*cell, fy+7*cell)], fill='black')
        draw.rectangle([(fx+cell,  fy+cell),  (fx+6*cell, fy+6*cell)], fill='white')
        draw.rectangle([(fx+2*cell,fy+2*cell),(fx+5*cell, fy+5*cell)], fill='black')

    # Black border
    draw.rectangle([(x,y),(x+size, y+size)], outline='black', width=2)


def draw_photo_box(draw, x1, y1, x2, y2, label="PHOTO"):
    """Placeholder photo box."""
    draw.rectangle([(x1, y1), (x2, y2)], fill=(195, 195, 195),
                   outline=(120, 120, 120), width=2)
    # Stick-figure silhouette
    cx, cy = (x1+x2)//2, (y1+y2)//2
    r = (x2-x1)//6
    draw.ellipse([(cx-r, y1+10), (cx+r, y1+10+2*r)], fill=(150,150,150))
    draw.ellipse([(cx-r*2, cy), (cx+r*2, y2-5)], fill=(150,150,150))
    draw.text((cx - len(label)*3, y2 - 18), label, fill=(80,80,80), font=F(10))


def draw_ashoka(draw, cx, cy, radius=28):
    """Simplified Ashoka Stambh emblem (circular)."""
    draw.ellipse([(cx-radius, cy-radius), (cx+radius, cy+radius)],
                 fill=(255,215,0), outline=(100,70,0), width=2)
    # 24 spokes
    for deg in range(0, 360, 15):
        rad = math.radians(deg)
        x1 = cx + int((radius*0.3)*math.cos(rad))
        y1 = cy + int((radius*0.3)*math.sin(rad))
        x2 = cx + int((radius*0.85)*math.cos(rad))
        y2 = cy + int((radius*0.85)*math.sin(rad))
        draw.line([(x1,y1),(x2,y2)], fill=(100,70,0), width=1)
    draw.ellipse([(cx-radius*0.28, cy-radius*0.28),
                  (cx+radius*0.28, cy+radius*0.28)], fill=(100,70,0))
    draw.ellipse([(cx-radius*0.12, cy-radius*0.12),
                  (cx+radius*0.12, cy+radius*0.12)], fill=(255,215,0))


def draw_fingerprint_logo(draw, cx, cy, radius=22):
    """UIDAI fingerprint icon approximation."""
    for i in range(5, 0, -1):
        r = radius - (5-i)*3
        col = (255, 255-i*20, 255-i*30)
        draw.arc([(cx-r, cy-r//2), (cx+r, cy+r//2)],
                 start=200, end=340, fill=AAD_ORANGE, width=2)
    draw.ellipse([(cx-4, cy-4), (cx+4, cy+4)], fill=AAD_ORANGE)


def draw_horizontal_tricolor(draw, x, y, w, h):
    """Mini Indian flag tricolor stripe."""
    th = h // 3
    draw.rectangle([(x, y),        (x+w, y+th)],    fill=(255, 153, 51))   # saffron
    draw.rectangle([(x, y+th),     (x+w, y+2*th)],  fill=(255, 255, 255))  # white
    draw.rectangle([(x, y+2*th),   (x+w, y+h)],     fill=(19,  136, 8))    # green


def aadhaar_num():
    return f"{random.randint(2000,9999)} {random.randint(1000,9999)} {random.randint(1000,9999)}"

def pan_num():
    a = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    return ''.join(random.choices(a,k=5)) + str(random.randint(1000,9999)) + random.choice(a)

def dl_num(state_code):
    return f"{state_code}-{random.randint(10,99)}-{random.randint(1990,2025)}-{random.randint(1000000,9999999)}"

def rnd_dob(lo=1960, hi=2003):
    return f"{random.randint(1,28):02d}/{random.randint(1,12):02d}/{random.randint(lo,hi)}"

def add_noise(img, sigma=5):
    arr = np.array(img.convert('RGB'), np.int16)
    arr = np.clip(arr + np.random.normal(0, sigma, arr.shape), 0, 255).astype(np.uint8)
    return Image.fromarray(arr)

def jpeg(img, q):
    buf = io.BytesIO()
    img.convert('RGB').save(buf, 'JPEG', quality=q)
    buf.seek(0)
    return Image.open(buf).copy()

def save(img, path, is_fake):
    img = add_noise(img, sigma=4 if is_fake else 3)
    img = jpeg(img, 87)
    if is_fake:
        img = jpeg(img, 74)   # double-save artifact = tampered region signature
    img.save(path, 'JPEG', quality=84)


# ─────────────────────────────────────────────────────────────────────────────
#  AADHAAR CARD
#  Layout matches UIDAI e-Aadhaar PDF / physical card:
#    • Orange header band  with UIDAI logo + "भारत सरकार"
#    • Green stripe        with "mera aadhaar meri pehchaan"
#    • Photo (left)  /  Fields (centre)  /  QR (right)
#    • Orange footer band  with 12-digit UID + barcode
# ─────────────────────────────────────────────────────────────────────────────
def draw_aadhaar(name, dob, gender, uid, address,
                 is_fake=False, tamper='none'):
    W, H = CARD_W, CARD_H
    img  = Image.new('RGB', (W, H), AAD_CREAM)
    draw = ImageDraw.Draw(img)

    # ── Orange header band ──────────────────────────────────────────────────
    draw.rectangle([(0, 0), (W, 72)], fill=AAD_ORANGE)

    # Fingerprint icon
    draw_fingerprint_logo(draw, 44, 36, radius=26)

    draw.text((80, 6),  "भारत सरकार",                       fill='white', font=F(11, bold=True))
    draw.text((80, 22), "Government of India",               fill='white', font=F(11))
    draw.text((80, 38), "Unique Identification Authority of India", fill=(255,230,200), font=F(9))

    # "AADHAAR" right side of header
    draw.text((W-190, 10), "आधार",   fill='white', font=F(26, bold=True))
    draw.text((W-105, 16), "AADHAAR",fill='white', font=F(20, bold=True))

    # ── Green stripe ────────────────────────────────────────────────────────
    draw.rectangle([(0, 72), (W, 98)], fill=AAD_GREEN)
    draw.text((W//2 - 140, 78),
              "मेरा आधार, मेरी पहचान   |   Mera Aadhaar, Meri Pehchaan",
              fill='white', font=F(12, bold=True))

    # ── Photo box ───────────────────────────────────────────────────────────
    draw_photo_box(draw, 18, 110, 195, 340)

    # ── Main content fields ─────────────────────────────────────────────────
    fx, fy = 215, 112

    display_name = fake.name() if (is_fake and tamper == 'name') else name
    draw.text((fx, fy),    "नाम / Name",             fill=(100,100,100), font=F(10))
    draw.text((fx, fy+15), display_name,             fill=(0,0,0),       font=F(17, bold=True))

    fy += 58
    display_dob = rnd_dob() if (is_fake and tamper == 'dob') else dob
    draw.text((fx, fy),    "जन्म तिथि / Date of Birth", fill=(100,100,100), font=F(10))
    draw.text((fx, fy+15), display_dob,              fill=(0,0,0), font=F(15, bold=True))

    fy += 52
    draw.text((fx, fy),    "लिंग / Gender",          fill=(100,100,100), font=F(10))
    draw.text((fx, fy+15), gender,                   fill=(0,0,0), font=F(15, bold=True))

    fy += 52
    draw.text((fx, fy),    "पता / Address",           fill=(100,100,100), font=F(10))
    lines = [address[i:i+52] for i in range(0, min(len(address),155), 52)]
    for i, ln in enumerate(lines[:3]):
        draw.text((fx, fy+14+i*14), ln, fill=(30,30,30), font=F(10))

    # ── QR Code ─────────────────────────────────────────────────────────────
    qr_seed = int(uid.replace(' ','')) % 99999
    draw_qr(draw, W - 175, 110, size=155, seed=qr_seed)

    # ── Orange footer with UID ───────────────────────────────────────────────
    draw.rectangle([(0, H-115), (W, H)], fill=AAD_ORANGE)
    draw.line([(0, H-115), (W, H-115)], fill='white', width=2)

    display_uid = uid
    if is_fake and tamper == 'number':
        parts = uid.split(' ')
        parts[random.randint(0,2)] = str(random.randint(1000,9999))
        display_uid = ' '.join(parts)

    # Big UID number
    draw.text((W//2 - 135, H-98), display_uid, fill='white', font=F(34, bold=True))

    # Barcode simulation (short vertical lines)
    bx, by = W//2 - 135, H - 52
    for j in range(90):
        w = random.choice([1,1,1,2])
        gap = random.choice([1,2,3])
        col = 'white' if random.random() > 0.45 else AAD_ORANGE
        draw.rectangle([(bx, by), (bx+w, by+28)], fill=col)
        bx += w + gap

    draw.text((18, H-50),
              "आधार - आम आदमी का पहचान  |  uidai.gov.in  |  1947",
              fill=(255,220,180), font=F(10))

    # Border
    draw.rectangle([(0,0),(W-1,H-1)], outline=AAD_ORANGE, width=4)

    return img.resize((640, 400), Image.LANCZOS)


# ─────────────────────────────────────────────────────────────────────────────
#  PAN CARD
#  Layout matches IT Dept physical card:
#    • Blue gradient background (light to mid)
#    • Maroon header:  "आयकर विभाग / INCOME TAX DEPARTMENT / GOVT. OF INDIA"
#    • Ashoka emblem   top-right
#    • PAN number      large, black, below header
#    • Photo           left side
#    • Fields          centre (Name, Father, DOB, Signature)
# ─────────────────────────────────────────────────────────────────────────────
def draw_pan(name, father_name, dob, pan,
             is_fake=False, tamper='none'):
    W, H = CARD_W, CARD_H
    img  = Image.new('RGB', (W, H), PAN_BG)
    draw = ImageDraw.Draw(img)

    # Blue gradient overlay (left→right)
    for x in range(W):
        t = x / W
        r = int(PAN_BG[0] * (1-t) + PAN_LTBLUE[0] * t)
        g = int(PAN_BG[1] * (1-t) + PAN_LTBLUE[1] * t)
        b = int(PAN_BG[2] * (1-t) + PAN_LTBLUE[2] * t)
        draw.line([(x, 0), (x, H)], fill=(r, g, b))

    # Subtle watermark text
    wm_font = F(55, bold=True)
    draw.text((W//2 - 140, H//2 - 38), "INDIA", fill=(200,218,235), font=wm_font)

    # ── Maroon header band ──────────────────────────────────────────────────
    draw.rectangle([(0, 0), (W, 80)], fill=PAN_MAROON)
    draw.text((14, 6),  "आयकर विभाग",                      fill='white', font=F(16, bold=True))
    draw.text((14, 28), "INCOME TAX DEPARTMENT",           fill=(255,200,200), font=F(14, bold=True))
    draw.text((14, 50), "GOVT. OF INDIA",                  fill=(255,230,230), font=F(12))

    # ── Ashoka emblem top-right ─────────────────────────────────────────────
    draw_ashoka(draw, W-68, 40, radius=35)

    # ── "Permanent Account Number Card" label ───────────────────────────────
    draw.rectangle([(0, 80), (W, 106)], fill=(160, 200, 225))
    draw.text((14, 84), "Permanent Account Number Card / स्थायी खाता संख्या कार्ड",
              fill=PAN_DKBLUE, font=F(12, bold=True))

    # ── PAN number ──────────────────────────────────────────────────────────
    display_pan = pan
    if is_fake and tamper == 'number':
        lst = list(pan)
        lst[random.randint(5,8)] = str(random.randint(0,9))
        display_pan = ''.join(lst)

    draw.text((14, 112), display_pan, fill=(10,10,10), font=F(32, bold=True))

    # ── Photo box ───────────────────────────────────────────────────────────
    draw_photo_box(draw, 14, 160, 190, 370)

    # ── Fields ──────────────────────────────────────────────────────────────
    fx, fy = 210, 160

    display_name = fake.name().upper() if (is_fake and tamper=='name') else name.upper()
    draw.text((fx, fy),    "नाम / Name",              fill=(60,60,60), font=F(10))
    draw.text((fx, fy+16), display_name,              fill=(0,0,0),   font=F(17, bold=True))

    fy += 62
    draw.text((fx, fy),    "पिता का नाम / Father's Name", fill=(60,60,60), font=F(10))
    draw.text((fx, fy+16), father_name.upper(),        fill=(0,0,0),   font=F(15, bold=True))

    fy += 58
    display_dob = rnd_dob(1950,2000) if (is_fake and tamper=='dob') else dob
    draw.text((fx, fy),    "जन्म की तारीख / Date of Birth", fill=(60,60,60), font=F(10))
    draw.text((fx, fy+16), display_dob,               fill=(0,0,0),   font=F(15, bold=True))

    fy += 58
    draw.text((fx, fy),    "हस्ताक्षर / Signature",  fill=(60,60,60), font=F(10))
    draw.line([(fx, fy+40), (fx+200, fy+40)], fill=(0,0,0), width=1)

    # ── Footer ──────────────────────────────────────────────────────────────
    draw.rectangle([(0, H-52), (W, H)], fill=(160,200,225))
    draw.text((14, H-40), "incometaxindia.gov.in",   fill=PAN_DKBLUE, font=F(10))
    draw.text((W-220, H-40), "INCOME TAX DEPARTMENT", fill=PAN_MAROON, font=F(10, bold=True))

    # QR code (PAN cards have one)
    draw_qr(draw, W-165, 155, size=140, seed=hash(pan) % 99999)

    draw.rectangle([(0,0),(W-1,H-1)], outline=PAN_DKBLUE, width=4)

    return img.resize((640, 400), Image.LANCZOS)


# ─────────────────────────────────────────────────────────────────────────────
#  DRIVING LICENCE
#  Indian Union Driving Licence  —  state-wise variation
#    • Header:   "THE UNION OF INDIA" + state name
#    • Tricolor stripe
#    • Photo (left)
#    • DL Number, validity, vehicle classes
#    • Ashoka emblem + state emblem placeholder
# ─────────────────────────────────────────────────────────────────────────────
STATES = [
    ("Maharashtra",   "MH", (140,0,20)),
    ("Karnataka",     "KA", (200,60,0)),
    ("Delhi",         "DL", (0,70,140)),
    ("Tamil Nadu",    "TN", (0,100,60)),
    ("Andhra Pradesh","AP", (0,80,130)),
    ("Gujarat",       "GJ", (180,100,0)),
    ("Rajasthan",     "RJ", (160,80,0)),
    ("Kerala",        "KL", (0,120,80)),
    ("West Bengal",   "WB", (100,0,100)),
    ("Punjab",        "PB", (80,0,140)),
]

VEHICLE_CLASSES = ["LMV", "MCWG", "TRANS", "HMV", "LMV-NT", "MCWOG"]


def draw_driving_licence(name, dob, dl_no, state_info, blood_group,
                          valid_from, valid_till,
                          is_fake=False, tamper='none'):
    state_name, state_code, state_col = state_info
    W, H = CARD_W, CARD_H
    img  = Image.new('RGB', (W, H), DL_CREAM)
    draw = ImageDraw.Draw(img)

    # Subtle light-cream background texture lines
    for yy in range(0, H, 18):
        draw.line([(0, yy), (W, yy)], fill=(245, 240, 225), width=1)

    # ── Top header ─────────────────────────────────────────────────────────
    draw.rectangle([(0, 0), (W, 78)], fill=state_col)

    # Tricolor stripe under header
    draw_horizontal_tricolor(draw, 0, 78, W, 18)

    draw.text((18, 5),  "THE UNION OF INDIA",    fill='white', font=F(13, bold=True))
    draw.text((18, 24), "INDIAN UNION DRIVING LICENCE", fill=(255,230,200), font=F(11, bold=True))
    draw.text((18, 44), f"{state_name.upper()} STATE MOTOR DRIVING LICENCE",
              fill='white', font=F(10))

    # Ashoka emblem header right
    draw_ashoka(draw, W - 70, 39, radius=34)

    # ── Form number badge ───────────────────────────────────────────────────
    draw.rectangle([(W-175, 5), (W-110, 26)], fill='white')
    draw.text((W-172, 8), f"FORM J / 7", fill=state_col, font=F(9, bold=True))

    # ── Photo box ───────────────────────────────────────────────────────────
    draw_photo_box(draw, 14, 106, 196, 350)

    # ── DL Number (prominent) ───────────────────────────────────────────────
    display_dl = dl_no
    if is_fake and tamper == 'number':
        parts = dl_no.split('-')
        parts[-1] = str(random.randint(1000000, 9999999))
        display_dl = '-'.join(parts)

    draw.rectangle([(210, 106), (W-14, 154)], fill=(240,240,255), outline=state_col, width=1)
    draw.text((218, 110), "DL Number / ड्राइविंग लाइसेंस नंबर",
              fill=(80,80,80), font=F(10))
    draw.text((218, 126), display_dl, fill=state_col, font=F(18, bold=True))

    # ── Fields ──────────────────────────────────────────────────────────────
    fx, fy = 218, 162

    display_name = fake.name() if (is_fake and tamper=='name') else name
    draw.text((fx, fy),    "Name / नाम",            fill=(80,80,80), font=F(10))
    draw.text((fx, fy+14), display_name,            fill=(0,0,0),   font=F(15, bold=True))

    fy += 50
    draw.text((fx, fy),    "S/o D/o W/o",           fill=(80,80,80), font=F(10))
    draw.text((fx, fy+14), fake.last_name(),         fill=(0,0,0),   font=F(13))

    fy += 46
    display_dob = rnd_dob() if (is_fake and tamper=='dob') else dob
    draw.text((fx, fy),    "DOB",                   fill=(80,80,80), font=F(10))
    draw.text((fx, fy+14), display_dob,             fill=(0,0,0),   font=F(13))

    draw.text((fx+180, fy),    "Blood Group",       fill=(80,80,80), font=F(10))
    draw.text((fx+180, fy+14), blood_group,         fill=(180,0,0), font=F(14, bold=True))

    fy += 46
    draw.text((fx, fy),    "Date of Issue",         fill=(80,80,80), font=F(10))
    draw.text((fx, fy+14), valid_from,              fill=(0,0,0),   font=F(12))

    draw.text((fx+180, fy),    "Valid Till",        fill=(80,80,80), font=F(10))
    draw.text((fx+180, fy+14), valid_till,          fill=(0,100,0), font=F(12, bold=True))

    # ── Vehicle classes ──────────────────────────────────────────────────────
    fy += 46
    draw.text((fx, fy), "Authorised to Drive:", fill=(80,80,80), font=F(10))
    fy += 14
    n_classes = random.randint(2, 4)
    classes = random.sample(VEHICLE_CLASSES, n_classes)
    cx_off = fx
    for cls in classes:
        draw.rectangle([(cx_off, fy), (cx_off+58, fy+22)],
                       fill=state_col, outline='white', width=1)
        draw.text((cx_off+4, fy+4), cls, fill='white', font=F(10, bold=True))
        cx_off += 64

    # ── QR code + fingerprint ───────────────────────────────────────────────
    draw_qr(draw, W - 165, 220, size=130, seed=hash(dl_no) % 99999)

    # Fingerprint placeholder (small)
    draw_fingerprint_logo(draw, W-192, 290, radius=16)

    # ── Footer ──────────────────────────────────────────────────────────────
    draw.rectangle([(0, H-52), (W, H)], fill=state_col)
    draw.text((18, H-40), f"{state_name} Motor Vehicles Dept",
              fill='white', font=F(10))
    draw.text((W-220, H-40), "sarathi.parivahan.gov.in",
              fill=(255,230,200), font=F(10))

    draw.rectangle([(0,0),(W-1,H-1)], outline=state_col, width=4)

    return img.resize((640, 400), Image.LANCZOS)


# ─────────────────────────────────────────────────────────────────────────────
# BATCH GENERATION
# ─────────────────────────────────────────────────────────────────────────────
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]

def generate_all(n_per_type: int = 400):
    """
    Generates n_per_type real + n_per_type fake  for each of 3 doc types.
    Default: 400 × 3 = 1200 real + 1200 fake = 2400 total images.
    """
    real_count = fake_count = 0
    aad_tampers = ['name', 'dob', 'number']
    pan_tampers = ['name', 'dob', 'number']
    dl_tampers  = ['name', 'dob', 'number']

    print(f"[TruthLens v2] Generating {n_per_type*3} real + {n_per_type*3} fake "
          f"Indian documents (realistic layout) ...")

    for i in range(n_per_type):

        # ── AADHAAR ──────────────────────────────────────────────────────────
        name    = fake.name()
        dob     = rnd_dob()
        gender  = random.choice(['Male / पुरुष', 'Female / महिला'])
        uid     = aadhaar_num()
        address = fake.address().replace('\n', ', ')[:140]

        path = os.path.join(REAL_DIR, f"aadhaar_real_{i:04d}.jpg")
        save(draw_aadhaar(name,dob,gender,uid,address), path, is_fake=False)
        real_count += 1

        tamper = random.choice(aad_tampers)
        path = os.path.join(FAKE_DIR, f"aadhaar_fake_{i:04d}.jpg")
        save(draw_aadhaar(name,dob,gender,uid,address,
                          is_fake=True, tamper=tamper), path, is_fake=True)
        fake_count += 1

        # ── PAN CARD ─────────────────────────────────────────────────────────
        name        = fake.name()
        father_name = fake.name()
        dob         = rnd_dob(1950, 2000)
        pan         = pan_num()

        path = os.path.join(REAL_DIR, f"pan_real_{i:04d}.jpg")
        save(draw_pan(name,father_name,dob,pan), path, is_fake=False)
        real_count += 1

        tamper = random.choice(pan_tampers)
        path = os.path.join(FAKE_DIR, f"pan_fake_{i:04d}.jpg")
        save(draw_pan(name,father_name,dob,pan,
                      is_fake=True, tamper=tamper), path, is_fake=True)
        fake_count += 1

        # ── DRIVING LICENCE ───────────────────────────────────────────────────
        state_info  = random.choice(STATES)
        state_code  = state_info[1]
        name        = fake.name()
        dob         = rnd_dob(1960, 2003)
        dl_no       = dl_num(state_code)
        blood       = random.choice(BLOOD_GROUPS)
        vy          = random.randint(2010, 2023)
        vm, vd      = random.randint(1,12), random.randint(1,28)
        valid_from  = f"{vd:02d}-{vm:02d}-{vy}"
        valid_till  = f"{vd:02d}-{vm:02d}-{vy+20}"  # DL valid 20 yrs

        path = os.path.join(REAL_DIR, f"dl_real_{i:04d}.jpg")
        save(draw_driving_licence(name,dob,dl_no,state_info,blood,
                                  valid_from,valid_till), path, is_fake=False)
        real_count += 1

        tamper = random.choice(dl_tampers)
        path = os.path.join(FAKE_DIR, f"dl_fake_{i:04d}.jpg")
        save(draw_driving_licence(name,dob,dl_no,state_info,blood,
                                  valid_from,valid_till,
                                  is_fake=True, tamper=tamper), path, is_fake=True)
        fake_count += 1

        if (i + 1) % 100 == 0:
            print(f"  ✓ {i+1}/{n_per_type} sets  |  real: {real_count}  fake: {fake_count}")

    print(f"\n✅ Done!   Real: {real_count}   Fake: {fake_count}")
    print(f"   Real → {REAL_DIR}")
    print(f"   Fake → {FAKE_DIR}")
    print("\nNEXT: run build_indian_dataset.py to merge with v3 and create v4")
    return real_count, fake_count


if __name__ == "__main__":
    generate_all(n_per_type=400)