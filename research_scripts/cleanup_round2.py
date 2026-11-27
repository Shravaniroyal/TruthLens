"""
TruthLens Round 2 Cleanup — FINAL SAFE VERSION
================================================
Cross-checked carefully. Only deletes old versions
and raw downloads. Keeps everything that took time to build.

NEVER touches:
  - All code files (app.py, etc.)
  - models/              <- your trained v4 model
  - prepared_data/       <- final training splits
  - indian_dataset/      <- your generated Indian docs (4.2 hrs to make)
  - final_dataset_v4/    <- your v4 training dataset
  - test_documents/
  - real_test_documents/
  - 03_documentation/
  - venv/

Only deletes:
  - raw downloads (on Kaggle, re-downloadable)
  - old dataset versions (v1, v2, v3 — replaced by v4)
  - old code archive

Run from your TruthLens folder:
    python cleanup_round2.py
"""

import os
import shutil

# ====================================================================
#  ABSOLUTE PROTECTION — never deleted under any circumstances
# ====================================================================
NEVER_DELETE_FOLDERS = {
    "venv", ".venv",
    "models",               # has best_truthlens_v4.pth
    "prepared_data",        # final training splits
    "indian_dataset",       # generated Indian docs — 4.2 hrs to regenerate
    "final_dataset_v4",     # v4 training dataset — hours to rebuild
    "test_documents",
    "real_test_documents",
    "03_documentation",
    "__pycache__",
    ".git",
}

NEVER_DELETE_FILES = {
    "app.py", "forensic_explainer.py", "gradcam_truthlens.py",
    "generate_indian_docs.py", "generate_synthetic_documents.py",
    "build_indian_dataset.py", "create_fakes.py",
    "TruthLens_Training.ipynb", "requirements.txt",
    ".gitignore", "README.md",
    "cleanup_round2.py", "scan_project.py", "cleanup_truthlens.py",
}

# ====================================================================
#  DELETE LIST — only raw downloads + old versions
# ====================================================================
TO_DELETE = [
    # Raw downloads — all available on Kaggle to re-download
    ("real_datasets",
     "27.09 GB — raw DocTamper downloads. Available on Kaggle."),

    ("doctamper_extracted",
     "150 MB — raw extracted DocTamper. Available on Kaggle."),

    ("DocTamper",
     "9.3 MB — small DocTamper subset. Available on Kaggle."),

    ("industry_datasets",
     "489 MB — raw industry downloads. Available on Kaggle."),

    # Old dataset versions — replaced by final_dataset_v4 and prepared_data
    ("final_dataset_v3",
     "1.45 GB — old v3 dataset. Superseded by v4."),

    ("final_dataset_v3_fixed",
     "1009 MB — old v3 fixed dataset. Superseded by v4."),

    ("final_dataset_v2",
     "850 MB — old v2 dataset. Superseded by v4."),

    ("final_dataset",
     "247 MB — old v1 dataset. Superseded by v4."),

    # Old training data folders
    ("training_data_v3",
     "334 MB — old training data v3. Superseded by v4."),

    ("training_data_v2",
     "334 MB — old training data v2. Superseded by v4."),

    ("training_data",
     "228 MB — old training data v1. Superseded by v4."),

    # Old code and empty folders
    ("_archive_old_code",
     "94.8 MB — archived old code. All current code is in root."),

    ("04_testing",
     "594 B — almost empty testing folder."),
]

# --------------------------------------------------------------------

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

print()
print("=" * 64)
print("  TruthLens Round 2 Cleanup — FINAL SAFE VERSION")
print("  PREVIEW ONLY — nothing deleted until you type YES")
print("=" * 64)

# Show what is protected
print("\n  PROTECTED — will NEVER be touched:")
print(f"  {'-'*59}")
protected = [
    ("app.py + all core Python files",   "your working system"),
    ("models/best_truthlens_v4.pth",     "your trained model — irreplaceable"),
    ("prepared_data/",                   "final training splits"),
    ("indian_dataset/",                  "generated Indian docs — 4.2 hrs to regenerate"),
    ("final_dataset_v4/",               "your v4 training dataset — hours to rebuild"),
    ("test_documents/",                  "test samples"),
    ("real_test_documents/",             "test samples"),
    ("03_documentation/",               "documentation"),
    ("venv/",                            "virtual environment"),
    ("TruthLens_Training.ipynb",         "Kaggle training notebook"),
]
for item, reason in protected:
    print(f"    KEEP  {item}")
    print(f"          Reason: {reason}")

# Show what will be deleted
print(f"\n  WILL BE DELETED (old versions + raw downloads):")
print(f"  {'-'*59}")

confirmed_delete = []
total_bytes = 0

for folder, reason in TO_DELETE:
    # Safety check
    if folder in NEVER_DELETE_FOLDERS:
        print(f"    PROTECTED  {folder}/")
        continue
    if os.path.isdir(folder):
        size = get_size_str(folder)
        print(f"    DELETE  {folder}/  ({size})")
        print(f"            {reason}")
        confirmed_delete.append(folder)
        for r, _, files in os.walk(folder):
            for f in files:
                try: total_bytes += os.path.getsize(os.path.join(r, f))
                except: pass
    else:
        print(f"    SKIP    {folder}/  (not found on disk)")

# Summary
print()
print("=" * 64)
print(f"  Folders to delete    : {len(confirmed_delete)}")
print(f"  Estimated space free : {get_size_str(total_bytes)}")
print()
print(f"  KEEPING (safe on your laptop, never going to GitHub):")
print(f"    models/best_truthlens_v4.pth  — your trained v4 model")
print(f"    indian_dataset/               — generated Indian docs")
print(f"    final_dataset_v4/             — v4 training dataset")
print(f"    prepared_data/                — final training splits")
print("=" * 64)
print()
print("  Everything being deleted is either:")
print("  (a) An old dataset version replaced by v4, OR")
print("  (b) A raw download available on Kaggle to re-download")
print()

confirm = input("  Type  YES  to delete, or anything else to cancel: ")
print()

if confirm.strip().upper() != "YES":
    print("  Cancelled — nothing was deleted. Your files are safe.")
else:
    deleted = 0
    failed  = 0

    for folder in confirmed_delete:
        # Double safety check
        if folder in NEVER_DELETE_FOLDERS:
            print(f"    SKIPPED (protected): {folder}/")
            continue
        try:
            shutil.rmtree(folder)
            print(f"    Deleted: {folder}/")
            deleted += 1
        except Exception as e:
            print(f"    FAILED:  {folder}/ => {e}")
            failed += 1

    print()
    print("=" * 64)
    print(f"  DONE! Deleted {deleted} folders ({failed} failed)")
    print("=" * 64)
    print()
    print("  Remaining folders and files:")
    print()
    for item in sorted(os.listdir(".")):
        if item in {"venv", ".venv", ".git", "__pycache__"}:
            continue
        if os.path.isdir(item):
            print(f"    FOLDER  {item}/  ({get_size_str(item)})")
        elif os.path.isfile(item):
            print(f"    FILE    {item}  ({get_size_str(item)})")

    print()
    print("  Next steps:")
    print("  1. Run: streamlit run app.py  (verify it still works)")
    print("  2. Paste the file list above here in chat")
    print("  3. I will create your new README.md and .gitignore")
    print("  4. Then push cleanly to GitHub")