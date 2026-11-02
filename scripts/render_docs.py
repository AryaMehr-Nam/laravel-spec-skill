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
    DocsRenderer,
    main,
    render_all_docs,
)

__all__ = [
    "DocsRenderer",
    "main",
    "render_all_docs",
]

if __name__ == "__main__":
    _TARGET = _SKILL_SCRIPTS_DIR / "render_docs.py"
    runpy.run_path(str(_TARGET), run_name="__main__")
