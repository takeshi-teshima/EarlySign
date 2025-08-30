#!/usr/bin/env python3
"""Detect files under docs/source not included in any toctree and optionally add them to the main index.rst toctree.

Usage:
  python add_missing_toctree.py [--root PATH] [--apply] [--verbose]

By default this runs as a dry-run and prints missing files. Use --apply to modify docs/source/index.rst (a backup is created).
"""
import argparse
from pathlib import Path
import re
import sys


def find_doc_files(root: Path):
    exts = {".md", ".rst"}
    files = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix in exts:
            # ignore build/output folders
            if "build" in p.parts or "_build" in p.parts:
                continue
            files.append(p.relative_to(root).as_posix())
    return sorted(files)


def parse_toctree_entries(root: Path):
    entries = set()
    # scan .rst files for '.. toctree::' blocks
    for rst in root.rglob("*.rst"):
        try:
            text = rst.read_text(encoding="utf-8")
        except Exception:
            continue
        lines = text.splitlines()
        i = 0
        while i < len(lines):
            if lines[i].strip().startswith(".. toctree::"):
                i += 1
                # consume option lines starting with ':'
                while i < len(lines) and re.match(r"\s*:\w+:", lines[i]):
                    i += 1
                # now collect indented entries (non-empty, leading whitespace)
                while i < len(lines) and (
                    lines[i].strip() == "" or lines[i].startswith("   ")
                ):
                    line = lines[i].strip()
                    if line and not line.startswith(":"):
                        entries.add(line)
                    i += 1
            else:
                i += 1
    return entries


def add_entries_to_index(root: Path, missing, apply_changes=False, verbose=False):
    index_path = root / "index.rst"
    if not index_path.exists():
        print("index.rst not found at", index_path)
        return False
    text = index_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    # find first toctree block
    for i, line in enumerate(lines):
        if line.strip().startswith(".. toctree::"):
            toctree_idx = i
            break
    else:
        print("No toctree:: directive found in index.rst")
        return False

    # move past options
    j = toctree_idx + 1
    while j < len(lines) and re.match(r"\s*:\w+:", lines[j]):
        j += 1

    # find end of existing entries block (contiguous indented non-option lines)
    # collect existing entries and remember insertion point after them
    insertion = j
    while insertion < len(lines) and (
        lines[insertion].strip() == "" or lines[insertion].startswith("   ")
    ):
        insertion += 1

    indent = "   "
    new_lines = []
    for m in sorted(missing):
        new_lines.append(indent + m)

    if not new_lines:
        if verbose:
            print("No missing entries to add")
        return True

    if apply_changes:
        # backup
        backup = index_path.with_suffix(".rst.bak")
        backup.write_text(text, encoding="utf-8")
        updated = lines[:insertion] + new_lines + lines[insertion:]
        index_path.write_text("\n".join(updated) + "\n", encoding="utf-8")
        print(f"Updated {index_path} — backup at {backup}")
    else:
        print("Dry-run — these entries would be added to", index_path)
        for l in new_lines:
            print(l)

    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="docs/source", help="docs source root")
    ap.add_argument("--apply", action="store_true", help="apply changes to index.rst")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    root = Path(args.root)
    if not root.exists():
        print("root not found:", root)
        sys.exit(2)

    files = find_doc_files(root)
    entries = parse_toctree_entries(root)

    # normalize entries: if entry has no extension, consider both .rst/.md
    normalized_entries = set(entries)
    for e in list(entries):
        if not Path(e).suffix:
            normalized_entries.add(e + ".md")
            normalized_entries.add(e + ".rst")

    # avoid adding the index file itself into its own toctree
    missing = [f for f in files if f not in normalized_entries and f != "index.rst"]
    if not missing:
        print("No missing files — all docs are included in toctree(s).")
        return 0

    print("Found", len(missing), "doc files not referenced in any toctree:")
    for m in missing:
        print(" -", m)

    # decide where to add: default to index.rst
    return (
        0
        if add_entries_to_index(
            root, missing, apply_changes=args.apply, verbose=args.verbose
        )
        else 1
    )


if __name__ == "__main__":
    sys.exit(main())
