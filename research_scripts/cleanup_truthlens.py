"""
TruthLens SAFE Cleanup Script
==============================
This script ONLY deletes files that are 100% safe to remove.
It will NEVER touch:
  - app.py
  - forensic_explainer.py
  - gradcam_truthlens.py
  - generate_indian_docs.py
  - generate_synthetic_documents.py
  - build_indian_dataset.py
  - create_fakes.py
  - TruthLens_Training.ipynb
  - requirements.txt
  - .gitignore
  - README.md
  - models/best_truthlens_v4.pth   <- YOUR TRAINED MODEL
  - prepared_data/                  <- YOUR DATASET (stays on laptop)
  - venv/                           <- your virtual environment

Run from inside your TruthLens folder:
    python cleanup_truthlens.py
"""

import os
import shutil

# =====================================================================
#  SAFETY LIST - these will NEVER be touched no matter what
# =====================================================================
NEVER_DELETE = {
    "app.py",
    "forensic_explainer.py",
    "gradcam_truthlens.py",
    "generate_indian_docs.py",
    "generate_synthetic_documents.py",
    "build_indian_dataset.py",
    "create_fakes.py",
    "TruthLens_Training.ipynb",
    "requirements.txt",
    ".gitignore",
    "README.md",
    "cleanup_truthlens.py",
    "scan_project.py",
}

NEVER_DELETE_FOLDERS = {
    "venv", ".venv", "prepared_data", "models", "__pycache__", ".git",
}

# =====================================================================
#  CATEGORY 1 - Duplicate app files
# =====================================================================
CAT1 = [
    "streamlit_app.py",
    "train_locally.py",
    "TruthLens_Website.html",
]

# =====================================================================
#  CATEGORY 2 - Giant zip files (already on Kaggle, safe to delete)
# =====================================================================
CAT2 = [
    "final_dataset_v4_kaggle.zip",
    "training_data_v2.zip",
    "training_data_v3.zip",
]

# =====================================================================
#  CATEGORY 3 - Old dataset build scripts
# =====================================================================
CAT3 = [
    "build_dataset.py",
    "build_dataset_v2.py",
    "build_dataset_v3.py",
    "build_dataset_v3_fixed.py",
    "organize_folders.py",
    "organize_training.py",
    "reorganize_v2.py",
    "reorganize_v3.py",
    "dataset_status.py",
    "zip_dataset.py",
    "verify_datasets.py",
    "verify_datasets_updated.py",
]

# =====================================================================
#  CATEGORY 4 - Download scripts (one-time use, not needed)
# =====================================================================
CAT4 = [
    "download_idcards.py",
    "download_industry_datasets.py",
    "download_midv.py",
    "download_real_datasets.py",
    "download_real_documents.py",
    "python download_real_documents.py",
    "multi_source_downloader.py",
    "get_real_documents.py",
    "collect_custom_docs.py",
    "convert_pdfs.py",
    "convert_personal.py",
    "extract_doctamper.py",
]

# =====================================================================
#  CATEGORY 5 - Fix/patch scripts (one-time fixes, done)
# =====================================================================
CAT5 = [
    "fix_and_convert.py",
    "fix_downloads.py",
    "fix_fake_idcards.py",
    "fix_idcards.py",
    "fix_idcards2.py",
    "rebuild_fake_idcards.py",
    "clean_idcards.py",
    "cleanup_project.py",
]

# =====================================================================
#  CATEGORY 6 - Test/debug scripts
# =====================================================================
CAT6 = [
    "test_day38.py",
    "test_system.py",
    "create_test_docs.py",
    "create_training_docs.py",
    "public_sources.txt",
    "QUICK_START.md",
]

# =====================================================================
#  CATEGORY 7 - Old folders (NOT your v4 model folder)
# =====================================================================
CAT7_FOLDERS = [
    "02_models",
    "src",
    "data",
    "docs",
    "01_production_code",
]

# ---------------------------------------------------------------------

def get_size_str(path):
    try:
        if os.path.isfile(path):
            size = os.path.getsize(path)
        else:
            size = sum(
                os.path.getsize(os.path.join(r, f))
                for r, _, files in os.walk(path)
                for f in files
            )
        if size < 1024:       return f"{size} B"
        elif size < 1024**2:  return f"{size/1024:.1f} KB"
        elif size < 1024**3:  return f"{size/1024**2:.1f} MB"
        else:                 return f"{size/1024**3:.2f} GB"
    except:
        return "?"

def collect(items, is_folder=False):
    found = []
    for item in items:
        if is_folder:
            if os.path.isdir(item) and item not in NEVER_DELETE_FOLDERS:
                found.append(item)
        else:
            if os.path.isfile(item) and os.path.basename(item) not in NEVER_DELETE:
                found.append(item)
    return found

def show(label, items, is_folder=False):
    print(f"\n  {label}")
    print(f"  {'-'*55}")
    found = []
    for item in items:
        exists = (os.path.isdir(item) if is_folder else os.path.isfile(item))
        if exists:
            safe = (item not in NEVER_DELETE_FOLDERS if is_folder
                    else os.path.basename(item) not in NEVER_DELETE)
            if safe:
                print(f"    DELETE  {item}  ({get_size_str(item)})")
                found.append(item)
            else:
                print(f"    SAFE    {item}  (protected - will NOT delete)")
        else:
            print(f"    SKIP    {item}  (not found)")
    return found

# ---------------------------------------------------------------------

print()
print("=" * 60)
print("  TruthLens SAFE Cleanup - PREVIEW (nothing deleted yet)")
print("=" * 60)

print("\n  PROTECTED - will NEVER be touched:")
print(f"  {'-'*55}")
protected_show = [
    "app.py", "forensic_explainer.py", "gradcam_truthlens.py",
    "generate_indian_docs.py", "generate_synthetic_documents.py",
    "build_indian_dataset.py", "create_fakes.py",
    "TruthLens_Training.ipynb", "requirements.txt",
    ".gitignore", "README.md",
    "models/best_truthlens_v4.pth  <- YOUR V4 MODEL",
    "prepared_data/                <- YOUR FULL DATASET",
    "venv/                         <- virtual environment",
]
for f in protected_show:
    print(f"    SAFE  {f}")

# Collect everything to delete
to_del_files   = []
to_del_folders = []

to_del_files   += show("CATEGORY 1 - Duplicate app files",        CAT1)
to_del_files   += show("CATEGORY 2 - Giant zip files",            CAT2)
to_del_files   += show("CATEGORY 3 - Old dataset build scripts",  CAT3)
to_del_files   += show("CATEGORY 4 - Download scripts",           CAT4)
to_del_files   += show("CATEGORY 5 - Fix/patch scripts",          CAT5)
to_del_files   += show("CATEGORY 6 - Test/debug scripts",         CAT6)
to_del_folders += show("CATEGORY 7 - Old folders", CAT7_FOLDERS, is_folder=True)

# Calculate space
total_bytes = 0
for f in to_del_files:
    try: total_bytes += os.path.getsize(f)
    except: pass
for folder in to_del_folders:
    for r, _, files in os.walk(folder):
        for f in files:
            try: total_bytes += os.path.getsize(os.path.join(r, f))
            except: pass

print()
print("=" * 60)
print(f"  Files to delete   : {len(to_del_files)}")
print(f"  Folders to delete : {len(to_del_folders)}")
print(f"  Space to free     : {get_size_str(total_bytes)}")
print(f"  Model v4.pth      : SAFE (not touched)")
print(f"  prepared_data/    : SAFE (not touched)")
print(f"  app.py            : SAFE (not touched)")
print("=" * 60)
print()

confirm = input("  Type  YES  to delete, or anything else to cancel: ")
print()

if confirm.strip().upper() != "YES":
    print("  Cancelled. Nothing was deleted. Your files are safe.")
    print()
else:
    deleted = 0
    failed  = 0

    print("  Deleting files...")
    for f in to_del_files:
        if os.path.basename(f) in NEVER_DELETE:
            print(f"    SKIPPED (protected): {f}")
            continue
        try:
            os.remove(f)
            print(f"    Deleted: {f}")
            deleted += 1
        except Exception as e:
            print(f"    FAILED:  {f} => {e}")
            failed += 1

    print()
    print("  Deleting old folders...")
    for folder in to_del_folders:
        if folder in NEVER_DELETE_FOLDERS:
            print(f"    SKIPPED (protected): {folder}/")
            continue
        try:
            shutil.rmtree(folder)
            print(f"    Deleted: {folder}/")
        except Exception as e:
            print(f"    FAILED:  {folder}/ => {e}")

    print()
    print("=" * 60)
    print(f"  DONE! Deleted {deleted} files ({failed} failed)")
    print("=" * 60)
    print()
    print("  Files remaining in your project root:")
    print()
    for item in sorted(os.listdir(".")):
        if item in {"venv", ".venv", ".git", "__pycache__"}:
            continue
        if os.path.isfile(item):
            print(f"    FILE    {item}  ({get_size_str(item)})")
        elif os.path.isdir(item):
            print(f"    FOLDER  {item}/  ({get_size_str(item)})")
    print()
    print("  Step 1: Verify your app still works:")
    print("          streamlit run app.py")
    print()
    print("  Step 2: Paste the file list above in the chat")
    print("          and I will create your new README + push to GitHub")
    print()