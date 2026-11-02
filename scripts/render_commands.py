"""CLI entrypoint and module forwarding to skills/laravel-spec/scripts/render_commands.py."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

_SKILL_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "skills" / "laravel-spec" / "scripts"
if str(_SKILL_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_SCRIPTS_DIR))

from render_commands import (  # noqa: E402
    generate_artisan_commands,
    main,
    render_commands,
    sort_models_by_dependency,
)

# Convenience aliases
CommandGenerator = render_commands
generate_all_commands = render_commands

__all__ = [
    "CommandGenerator",
    "generate_all_commands",
    "generate_artisan_commands",
    "main",
    "render_commands",
    "sort_models_by_dependency",
]

if __name__ == "__main__":
    _TARGET = _SKILL_SCRIPTS_DIR / "render_commands.py"
    runpy.run_path(str(_TARGET), run_name="__main__")
