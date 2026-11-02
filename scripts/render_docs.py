"""CLI entrypoint and module forwarding to skills/laravel-spec/scripts/render_docs.py."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

_SKILL_SCRIPTS_DIR = (
    Path(__file__).resolve().parent.parent / "skills" / "laravel-spec" / "scripts"
)
if str(_SKILL_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_SCRIPTS_DIR))

from render_docs import (  # noqa: E402
    DOC_FILENAMES,
    main,
    render_docs,
    render_docs_from_file,
    write_docs,
)

# Convenience aliases
DocsRenderer = render_docs
render_all_docs = render_docs

__all__ = [
    "DOC_FILENAMES",
    "DocsRenderer",
    "main",
    "render_all_docs",
    "render_docs",
    "render_docs_from_file",
    "write_docs",
]

if __name__ == "__main__":
    _TARGET = _SKILL_SCRIPTS_DIR / "render_docs.py"
    runpy.run_path(str(_TARGET), run_name="__main__")
