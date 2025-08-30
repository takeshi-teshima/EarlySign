"""Sphinx extension to generate a _generated_toc.rst listing docs not present in any toctree.

This runs on builder-inited and writes docs/_generated_toc.rst under the docs source dir.
It avoids index.rst and files starting with '_' and tries not to duplicate entries already present in existing toctrees.
"""

from pathlib import Path
import re


def find_doc_files(root: Path):
    exts = {".md", ".rst"}
    files = []
    for p in root.rglob("*"):
        if p.is_file() and p.suffix in exts:
            if "build" in p.parts or "_build" in p.parts:
                continue
            rel = p.relative_to(root).as_posix()
            files.append(rel)
    return sorted(files)


def parse_toctree_entries(root: Path):
    entries = set()
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
                while i < len(lines) and re.match(r"\s*:\w+:", lines[i]):
                    i += 1
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


def write_generated_toc(root: Path, entries):
    gen = root / "_generated_toc.rst"
    lines = [".. _generated_toc:", "", ".. toctree::", "   :maxdepth: 2", ""]
    for e in sorted(entries):
        lines.append("   " + e)
    gen.write_text("\n".join(lines) + "\n", encoding="utf-8")


def generate(root_path: str):
    root = Path(root_path)
    files = find_doc_files(root)
    existing = parse_toctree_entries(root)

    # normalize existing: consider .md/.rst variants
    normalized = set(existing)
    for e in list(existing):
        if not Path(e).suffix:
            normalized.add(e + ".md")
            normalized.add(e + ".rst")

    # exclude index and generated file itself and any private files
    candidates = [
        f
        for f in files
        if f not in normalized
        and not f.startswith("_")
        and f != "index.rst"
        and f != "_generated_toc.rst"
    ]

    # convert to toctree-friendly paths (strip extensions)
    entries = []
    for c in candidates:
        p = Path(c)
        stem = str(p.with_suffix("")).replace("\\", "/")
        entries.append(stem)

    if entries:
        write_generated_toc(root, entries)


def setup(app):
    docs_dir = Path(__file__).parent

    def on_builder_inited(app):
        try:
            generate(str(docs_dir))
        except Exception:
            # Fail silently to avoid breaking builds; admins can run the script separately
            pass

    app.connect("builder-inited", on_builder_inited)


if __name__ == "__main__":
    # allow running standalone for debugging
    generate(str(Path(__file__).parent))
