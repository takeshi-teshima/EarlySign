add_missing_toctree.py

Simple helper to detect markdown/rst files under `docs/source` that are not referenced by any `toctree` directive and optionally append them to `docs/source/index.rst`.

Usage:

python docs/scripts/add_missing_toctree.py         # dry-run, lists missing files
python docs/scripts/add_missing_toctree.py --apply # update index.rst (creates index.rst.bak)

Example:

python docs/scripts/add_missing_toctree.py --root docs/source
python docs/scripts/add_missing_toctree.py --root docs/source --apply

Notes:
- The script is conservative and only appends entries to the first toctree found in `index.rst`.
- It recognizes `.md` and `.rst` files.
