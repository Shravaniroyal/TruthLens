"""
TruthLens -- Build Dataset v4  (FIXED: .tif extension + correct real count)
============================================================================
Root cause of v3 real = 177:
  RVL-CDIP images use .tif extension (NOT .tiff)
  Old script only checked: .jpg .jpeg .png .bmp .tiff .webp
  Fix: added .tif to IMAGE_EXTS

Expected result after fix:
  v3 real: 5896   v3 fake: 5896
  Indian real: 1200   Indian fake: 1200
  v4 TOTAL: ~14192 images balanced

Run:
    .\\venv\\Scripts\\python.exe build_indian_dataset.py
"""

import os, shutil, random
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
ROOT = Path(r"C:\Users\Shravani\TruthLens")

V3 = ROOT / "final_dataset_v3_fixed"
V3_SPLITS = {
    "train": {"real": V3/"train"/"real", "fake": V3/"train"/"fake"},
    "val":   {"real": V3/"val"  /"real", "fake": V3/"val"  /"fake"},
    "test":  {"real": V3/"test" /"real", "fake": V3/"test" /"fake"},
}

IND_REAL = ROOT / "indian_dataset" / "real"
IND_FAKE = ROOT / "indian_dataset" / "fake"
V4_BASE  = ROOT / "final_dataset_v4"

TRAIN_RATIO = 0.70
VAL_RATIO   = 0.15
SEED        = 42
random.seed(SEED)

# KEY FIX: .tif (RVL-CDIP format) was missing from this list
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.webp'}


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def list_images(folder: Path):
    """Find all images in folder (flat — v3 real/fake are not nested)."""
    if not folder.exists():
        print(f"  WARNING: Not found: {folder}")
        return []
    imgs = [p for p in folder.iterdir() if p.suffix.lower() in IMAGE_EXTS]
    imgs.sort()
    return imgs


def shuffle_split(imgs, train_r, val_r, seed):
    rng = random.Random(seed)
    lst = list(imgs)
    rng.shuffle(lst)
    n    = len(lst)
    n_tr = int(n * train_r)
    n_v  = int(n * val_r)
    return lst[:n_tr], lst[n_tr:n_tr+n_v], lst[n_tr+n_v:]


def copy_files(src_list, dest: Path, prefix: str):
    dest.mkdir(parents=True, exist_ok=True)
    for idx, src in enumerate(src_list):
        dst = dest / f"{prefix}_{idx:05d}.jpg"   # save all as jpg
        # Convert .tif → .jpg on the fly using Pillow
        try:
            from PIL import Image
            img = Image.open(src).convert('RGB')
            img.save(dst, 'JPEG', quality=87)
        except Exception:
            shutil.copy2(src, dest / f"{prefix}_{idx:05d}{src.suffix.lower()}")
    return len(src_list)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def build_v4():
    print("=" * 62)
    print("  TruthLens -- Building Dataset v4 (Western + Indian docs)")
    print("  Fix: .tif extension now included")
    print("=" * 62)

    # -- Read v3 -------------------------------------------------------------
    print("\n[1/4] Reading v3 dataset ...")
    v3_real, v3_fake = [], []
    for sp, paths in V3_SPLITS.items():
        r = list_images(paths["real"])
        f = list_images(paths["fake"])
        print(f"       v3 {sp:5s}  real: {len(r):5d}   fake: {len(f):5d}")
        v3_real.extend(r)
        v3_fake.extend(f)
    print(f"\n       v3 TOTAL  real: {len(v3_real):5d}   fake: {len(v3_fake):5d}")

    # -- Read Indian docs ----------------------------------------------------
    print("\n[2/4] Reading Indian dataset ...")
    ind_real = list_images(IND_REAL)
    ind_fake = list_images(IND_FAKE)
    print(f"       Indian   real: {len(ind_real):5d}   fake: {len(ind_fake):5d}")

    if not ind_real:
        print("  ERROR: Indian dataset empty — run generate_indian_docs.py first")
        return

    # -- Merge & balance -----------------------------------------------------
    print("\n[3/4] Merging and balancing ...")
    all_real = v3_real + ind_real
    all_fake = v3_fake + ind_fake
    min_n    = min(len(all_real), len(all_fake))
    rng      = random.Random(SEED)
    rng.shuffle(all_real)
    rng.shuffle(all_fake)
    all_real = all_real[:min_n]
    all_fake = all_fake[:min_n]
    print(f"       Balanced: {min_n} real + {min_n} fake = {min_n*2} total")

    # -- Split & write -------------------------------------------------------
    print("\n[4/4] Writing v4 splits (converting .tif -> .jpg) ...")
    if V4_BASE.exists():
        shutil.rmtree(V4_BASE)

    tr_r, val_r, te_r = shuffle_split(all_real, TRAIN_RATIO, VAL_RATIO, SEED)
    tr_f, val_f, te_f = shuffle_split(all_fake, TRAIN_RATIO, VAL_RATIO, SEED+1)

    counts = {}
    for sp, rl, fk in [("train", tr_r, tr_f),
                        ("val",   val_r, val_f),
                        ("test",  te_r,  te_f)]:
        print(f"       Writing {sp}/ ...", end='', flush=True)
        n_r = copy_files(rl, V4_BASE / sp / "real", "real")
        n_f = copy_files(fk, V4_BASE / sp / "fake", "fake")
        counts[sp] = (n_r, n_f)
        print(f"  real: {n_r:5d}   fake: {n_f:5d}   total: {n_r+n_f:5d}")

    # -- Summary -------------------------------------------------------------
    tot_r = sum(v[0] for v in counts.values())
    tot_f = sum(v[1] for v in counts.values())

    print(f"\n{'='*62}")
    print(f"  Dataset v4 built!")
    print(f"  {'Split':7}  {'Real':>6}  {'Fake':>6}  {'Total':>7}")
    print(f"  {'-'*35}")
    for sp, (r, f) in counts.items():
        print(f"  {sp:7}  {r:6d}  {f:6d}  {r+f:7d}")
    print(f"  {'-'*35}")
    print(f"  {'TOTAL':7}  {tot_r:6d}  {tot_f:6d}  {tot_r+tot_f:7d}")
    print(f"{'='*62}")
    print(f"\n  Output: {V4_BASE}")
    print(f"""
NEXT STEPS
==========

STEP 1 -- Zip the dataset in PowerShell:

  Compress-Archive -Path "C:\\Users\\Shravani\\TruthLens\\final_dataset_v4" `
    -DestinationPath "C:\\Users\\Shravani\\TruthLens\\final_dataset_v4.zip"

STEP 2 -- Upload to Kaggle:
  kaggle.com -> Datasets -> New Dataset
  Name: truthlens-v4
  Upload: final_dataset_v4.zip

STEP 3 -- Open Kaggle Notebook "TRUTHLENS v33"
  Change:  DATA_DIR = '/kaggle/input/datasets/shravanirs4/truthlens-v4'
  Keep same: EfficientNet-B4, lr=5e-5, 30 epochs, label_smoothing=0.1
  Save Version -> Save and Run All  (~2 hrs on T4 x2)

STEP 4 -- Download & deploy:
  Notebook Output tab -> download best_truthlens_v4.pth
  Copy to: C:\\Users\\Shravani\\TruthLens\\models\\best_truthlens_v4.pth
  Update app.py:  MODEL_PATH = "models/best_truthlens_v4.pth"
""")


if __name__ == "__main__":
    build_v4()