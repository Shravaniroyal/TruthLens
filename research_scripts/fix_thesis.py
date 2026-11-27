"""
TruthLens Thesis — Auto-Fix Script
====================================
Run this in the same folder as your main.tex file.

Usage:
    python fix_thesis.py
"""

import os
import shutil
from datetime import datetime

INPUT_FILE  = "main.tex"
OUTPUT_FILE = "main_fixed.tex"
BACKUP_FILE = f"main_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.tex"

FIXES = [

    # ── TITLE PAGE ─────────────────────────────────────────────────
    (
        r"{\large Roll No:\quad [Your Roll Number]}",
        r"{\large Roll No:\quad 25MDA135}",
        "Title page — Roll Number"
    ),
    (
        r"[Supervisor Name, Designation]",
        r"Dr. Utkarsh Mahadeo Khaire, Assistant Professor",
        "Title page — Supervisor name and designation"
    ),

    # ── DECLARATION ────────────────────────────────────────────────
    (
        r"supervision of [Supervisor Name]. The results",
        r"supervision of Dr. Utkarsh Mahadeo Khaire. The results",
        "Declaration — Supervisor name in body"
    ),
    (
        r"Roll No: [Your Roll Number]",
        r"Roll No: 25MDA135",
        "Declaration/Certificate — Roll number"
    ),
    (
        r"(Roll No: [Your Roll Number])",
        r"(Roll No: 25MDA135)",
        "Certificate — Roll number in brackets"
    ),

    # ── CERTIFICATE ────────────────────────────────────────────────
    (
        r"[Supervisor Name]\\{}[Designation]\\{}Department of CSE",
        r"Dr. Utkarsh Mahadeo Khaire\\{}Assistant Professor\\{}Department of CSE",
        "Certificate — Supervisor signature block"
    ),

    # ── ACKNOWLEDGEMENTS ───────────────────────────────────────────
    (
        r"[Supervisor Name], [Designation], Department of Computer Science",
        r"Dr. Utkarsh Mahadeo Khaire, Assistant Professor, Department of Computer Science",
        "Acknowledgements — Supervisor name and designation"
    ),
    (
        r"[Supervisor Name], [Designation], Department of Computer",
        r"Dr. Utkarsh Mahadeo Khaire, Assistant Professor, Department of Computer",
        "Acknowledgements — Supervisor (short variant)"
    ),

    # ── BUG 1: TRAINING CONFIG TABLE ───────────────────────────────
    (
        r"97.95\% (epoch 23) (epoch 17) \\",
        r"97.95\% at Epoch 23 \\",
        "Bug fix — Training config table (duplicate epoch 17)"
    ),
    (
        "97.95\\% (epoch 23) (epoch 17) \\\\",
        "97.95\\% at Epoch 23 \\\\",
        "Bug fix — Training config table (escaped variant)"
    ),

    # ── BUG 2: TRAINING CURVES FIGURE CAPTION ──────────────────────
    (
        r"best validation accuracy 97.95\% at epoch 17. Right:",
        r"best validation accuracy 97.95\% at epoch 23. Right:",
        "Bug fix — Training curves figure caption (epoch 17 → 23)"
    ),
    (
        "best validation accuracy 97.95\\% at epoch 17. Right:",
        "best validation accuracy 97.95\\% at epoch 23. Right:",
        "Bug fix — Training curves figure caption (escaped variant)"
    ),
]

def apply_fixes(content):
    results = []
    for find, replace, description in FIXES:
        if find in content:
            content = content.replace(find, replace)
            results.append(("FIXED  ✅", description))
        else:
            results.append(("SKIP   ⚪", f"{description} (not found — may already be fixed)"))
    return content, results

def main():
    print()
    print("=" * 60)
    print("  TruthLens Thesis — Auto-Fix Script")
    print("=" * 60)

    if not os.path.exists(INPUT_FILE):
        print(f"\n  ERROR: '{INPUT_FILE}' not found.")
        print(f"  Run this script in the same folder as main.tex")
        return

    shutil.copy2(INPUT_FILE, BACKUP_FILE)
    print(f"\n  Backup created: {BACKUP_FILE}")

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"  File loaded: {len(content):,} characters\n")
    print("  Applying fixes:")
    print(f"  {'-'*55}")

    fixed_content, results = apply_fixes(content)

    fixed_count = 0
    for status, description in results:
        print(f"    {status}  {description}")
        if "FIXED" in status:
            fixed_count += 1

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(fixed_content)

    print()
    print("=" * 60)
    print(f"  Fixed {fixed_count} issues")
    print(f"  Output saved: {OUTPUT_FILE}")
    print("=" * 60)
    print()
    print("  Upload 'main_fixed.tex' to Overleaf and recompile!")
    print()

if __name__ == "__main__":
    main()