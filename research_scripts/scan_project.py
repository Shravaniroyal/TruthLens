"""
TruthLens Project Scanner
Run this in your TruthLens project folder root.
It will print every file with its size so we know what to keep or delete.
"""

import os

# ── Change this to your actual TruthLens folder path ──────────────────────────
PROJECT_PATH = "."   # "." means current folder — run from inside TruthLens folder
# ──────────────────────────────────────────────────────────────────────────────

SKIP_DIRS = {"venv", ".venv", "__pycache__", ".git", "node_modules", ".idea", ".vscode"}

def get_size(path):
    try:
        size = os.path.getsize(path)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size/1024:.1f} KB"
        else:
            return f"{size/1024/1024:.1f} MB"
    except:
        return "?"

def scan(folder, prefix=""):
    try:
        entries = sorted(os.listdir(folder))
    except PermissionError:
        return

    dirs  = [e for e in entries if os.path.isdir(os.path.join(folder, e)) and e not in SKIP_DIRS]
    files = [e for e in entries if os.path.isfile(os.path.join(folder, e))]

    for i, d in enumerate(dirs):
        connector = "└── " if (i == len(dirs) - 1 and not files) else "├── "
        print(f"{prefix}{connector}📁 {d}/")
        extension = "    " if (i == len(dirs) - 1 and not files) else "│   "
        scan(os.path.join(folder, d), prefix + extension)

    for i, f in enumerate(files):
        connector = "└── " if i == len(files) - 1 else "├── "
        size = get_size(os.path.join(folder, f))
        print(f"{prefix}{connector}📄 {f}  ({size})")

print("=" * 60)
print(f"  TRUTHLENS PROJECT SCAN")
print(f"  Folder: {os.path.abspath(PROJECT_PATH)}")
print("=" * 60)
print()
scan(PROJECT_PATH)
print()
print("=" * 60)

# ── Also count totals ──────────────────────────────────────────────────────────
total_files = 0
total_size  = 0
for root, dirs, files in os.walk(PROJECT_PATH):
    dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
    for f in files:
        total_files += 1
        try:
            total_size += os.path.getsize(os.path.join(root, f))
        except:
            pass

print(f"  Total files : {total_files}")
print(f"  Total size  : {total_size/1024/1024:.1f} MB  (excluding venv/.git)")
print("=" * 60)
print()
print("Copy the output above and paste it in the chat!")