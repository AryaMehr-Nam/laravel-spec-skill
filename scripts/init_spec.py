"""CLI entrypoint and module forwarding to skills/laravel-spec/scripts/init_spec.py."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

_SKILL_SCRIPTS_DIR = (
    Path(__file__).resolve().parent.parent / "skills" / "laravel-spec" / "scripts"
)
if str(_SKILL_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_SCRIPTS_DIR))

from init_spec import (  # noqa: E402
    SpecInitializer,
    init_spec_project,
    main,
)

__all__ = [
    "SpecInitializer",
    "init_spec_project",
    "main",
]

if __name__ == "__main__":
    _TARGET = _SKILL_SCRIPTS_DIR / "init_spec.py"
    runpy.run_path(str(_TARGET), run_name="__main__")
