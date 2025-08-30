import os
import sys

# Put project root on sys.path so autodoc can import the package if needed
sys.path.insert(0, os.path.abspath("../.."))
# Ensure local docs extensions are importable
sys.path.insert(0, os.path.abspath("."))

project = "EarlySign"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "myst_nb",
    "sphinx_copybutton",
]
templates_path = ["_templates"]
exclude_patterns = []

# Use a book-style theme for a book-like layout when available; fall back to
# a bundled theme (alabaster) so CI/local checks don't fail if the theme
# isn't installed yet (this lets `make check` run successfully while the
# dependency is being added via Poetry).
try:
    import importlib
    import importlib.util
    if importlib.util.find_spec("sphinx_book_theme") is not None:
        html_theme = "sphinx_book_theme"
        html_theme_options = {
            "repository_url": "https://github.com/takeshi-teshima/EarlySign",
            "use_repository_button": True,
            "use_issues_button": True,
            "path_to_docs": "docs/source",
        }
    else:
        html_theme = "alabaster"
        html_theme_options = {}
except Exception:
    html_theme = "alabaster"
    html_theme_options = {}


# ロゴ画像とCSSの設定（グローバル）
# myst config: enable useful parsing extensions for notebook-style content
myst_enable_extensions = [
    "deflist",
    "html_admonition",
    "html_image",
    "colon_fence",
]

master_doc = "index"

# Static assets and logo: place a logo image at docs/logo.png (project root)
# and reference it here so it appears in the top-left of the generated site.
# Use an absolute path to the repository-level docs/logo.png so Sphinx can
# include it even though it's outside docs/source/_static.
html_static_path = ['_static']
html_logo = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logo.png"))
