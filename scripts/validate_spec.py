"""CLI entrypoint and module forwarding to skills/laravel-spec/scripts/validate_spec.py."""

from __future__ import annotations

import runpy
import sys
from pathlib import Path

_SKILL_SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "skills" / "laravel-spec" / "scripts"
if str(_SKILL_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_SCRIPTS_DIR))

from validate_spec import (  # noqa: E402
    RuleViolation,
    Severity,
    SpecValidator,
    ValidationResult,
    main,
    validate_spec,
    validate_spec_file,
)

__all__ = [
    "RuleViolation",
    "Severity",
    "SpecValidator",
    "ValidationResult",
    "main",
    "validate_spec",
    "validate_spec_file",
]

if __name__ == "__main__":
    _TARGET = _SKILL_SCRIPTS_DIR / "validate_spec.py"
    runpy.run_path(str(_TARGET), run_name="__main__")
