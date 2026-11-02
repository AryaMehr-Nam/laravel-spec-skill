"""CLI entrypoint and module forwarding to skills/laravel-spec/scripts/render_commands.py."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

_SKILL_SCRIPTS_DIR = (
    Path(__file__).resolve().parent.parent / "skills" / "laravel-spec" / "scripts"
)
if str(_SKILL_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_SCRIPTS_DIR))

from render_commands import (  # noqa: E402
    CommandGenerator,
    generate_all_commands,
    main,
)

__all__ = [
    "CommandGenerator",
    "generate_all_commands",
    "main",
]

if __name__ == "__main__":
    _TARGET = _SKILL_SCRIPTS_DIR / "render_commands.py"
    runpy.run_path(str(_TARGET), run_name="__main__")
