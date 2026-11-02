"""Specification initialization script for Laravel Filament applications.

Generates an empty, schema-compliant spec.json skeleton from a template
or CLI arguments. Standard library only (Python 3.10+).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Default path to bundled empty-spec.json template
DEFAULT_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "empty-spec.json"


def get_default_skeleton(
    name: str = "Laravel Application",
    description: str = "Enterprise application built with Laravel and Filament",
    locale: str = "en",
    timezone: str = "UTC",
    laravel_version: str = "12",
    filament_version: str = "v3",
    presets: list[str] | None = None,
) -> dict[str, Any]:
    """Return fallback default specification dictionary."""
    return {
        "project": {
            "name": name,
            "description": description,
            "locale": locale,
            "timezone": timezone,
            "laravel_version": laravel_version,
            "filament_version": filament_version,
            "presets": list(presets or []),
        },
        "roles": [
            {
                "name": "super-admin",
                "description": "Full system administrator with unconstrained access",
                "is_super_admin": True,
            }
        ],
        "models": [],
        "policies": [],
        "filament": {
            "panels": [],
        },
        "integrations": [],
        "milestones": [
            {
                "id": "M0",
                "title": "Foundation & Authentication",
                "depends_on": [],
                "scope": [],
                "acceptance": [
                    "Core database schema and authentication are functional",
                    "Initial test suite passes with baseline coverage",
                ],
            }
        ],
    }


def init_spec(
    name: str = "Laravel Application",
    description: str = "Enterprise application built with Laravel and Filament",
    locale: str = "en",
    timezone: str = "UTC",
    laravel_version: str = "12",
    filament_version: str = "v3",
    presets: list[str] | None = None,
    template_path: str | Path | None = None,
) -> dict[str, Any]:
    """Create an empty spec skeleton dictionary.

    Args:
        name: Project name.
        description: Brief project summary.
        locale: Primary application locale code (e.g. 'en', 'fa').
        timezone: Application timezone string (e.g. 'UTC', 'Asia/Tehran').
        laravel_version: Target major Laravel version ('11', '12', '13').
        filament_version: Target Filament version ('v3', 'v4').
        presets: Optional list of preset identifiers (e.g. ['rtl-fa']).
        template_path: Path to custom template JSON file.

    Returns:
        Structured specification dictionary.
    """
    if template_path:
        tpl_file = Path(template_path).resolve()
        if not tpl_file.is_file():
            raise FileNotFoundError(f"Custom template file not found: {template_path}")
        with open(tpl_file, encoding="utf-8") as f:
            spec: dict[str, Any] = json.load(f)
    elif DEFAULT_TEMPLATE_PATH.is_file():
        try:
            with open(DEFAULT_TEMPLATE_PATH, encoding="utf-8") as f:
                spec = json.load(f)
        except Exception:
            spec = get_default_skeleton()
    else:
        spec = get_default_skeleton()

    # Ensure required top-level sections exist
    if "project" not in spec or not isinstance(spec["project"], dict):
        spec["project"] = {}

    spec["project"]["name"] = name
    spec["project"]["description"] = description
    spec["project"]["locale"] = locale
    spec["project"]["timezone"] = timezone
    spec["project"]["laravel_version"] = laravel_version
    spec["project"]["filament_version"] = filament_version

    if presets is not None:
        spec["project"]["presets"] = list(presets)
    elif not isinstance(spec["project"].get("presets"), list):
        spec["project"]["presets"] = []

    for section in ("roles", "models", "policies", "integrations", "milestones"):
        if section not in spec or not isinstance(spec[section], list):
            spec[section] = []

    if "filament" not in spec or not isinstance(spec["filament"], dict):
        spec["filament"] = {"panels": []}
    elif not isinstance(spec["filament"].get("panels"), list):
        spec["filament"]["panels"] = []

    # Ensure super-admin role exists if roles is empty
    if not spec["roles"]:
        spec["roles"] = [
            {
                "name": "super-admin",
                "description": "Full system administrator with unconstrained access",
                "is_super_admin": True,
            }
        ]

    # Ensure at least M0 milestone exists if milestones is empty
    if not spec["milestones"]:
        spec["milestones"] = [
            {
                "id": "M0",
                "title": "Foundation & Authentication",
                "depends_on": [],
                "scope": [],
                "acceptance": [
                    "Core database schema and authentication are functional",
                    "Initial test suite passes with baseline coverage",
                ],
            }
        ]

    return spec


def write_spec(
    spec_data: dict[str, Any],
    output_path: str | Path,
    force: bool = False,
) -> Path:
    """Serialize and write specification dictionary to disk.

    Args:
        spec_data: Validated specification dictionary.
        output_path: Destination file path.
        force: Overwrite destination file if it already exists.

    Returns:
        Resolved Path of written file.

    Raises:
        FileExistsError: If output_path exists and force is False.
    """
    dest = Path(output_path).resolve()

    if dest.exists() and not force:
        raise FileExistsError(
            f"Target specification file already exists at '{dest}'. Use --force to overwrite."
        )

    dest.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(spec_data, indent=2, ensure_ascii=False) + "\n"
    dest.write_text(content, encoding="utf-8", newline="\n")
    return dest


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for init_spec."""
    parser = argparse.ArgumentParser(
        description="Initialize an empty Laravel + Filament specification skeleton."
    )
    parser.add_argument(
        "--name",
        default="Laravel Application",
        help="Project name (default: 'Laravel Application')",
    )
    parser.add_argument(
        "--description",
        default="Enterprise application built with Laravel and Filament",
        help="Brief project description",
    )
    parser.add_argument(
        "--locale",
        default="en",
        help="Application locale (default: 'en')",
    )
    parser.add_argument(
        "--timezone",
        default="UTC",
        help="Application timezone (default: 'UTC')",
    )
    parser.add_argument(
        "--laravel-version",
        default="12",
        help="Target Laravel version (default: '12')",
    )
    parser.add_argument(
        "--filament-version",
        default="v3",
        help="Target Filament version (default: 'v3')",
    )
    parser.add_argument(
        "--presets",
        nargs="*",
        default=None,
        help="Preset identifiers (e.g. rtl-fa iran-payments otp-login multi-tenant)",
    )
    parser.add_argument(
        "--template",
        default=None,
        help="Path to custom JSON template",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="spec/spec.json",
        help="Output file path (default: 'spec/spec.json')",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Overwrite destination file if it already exists",
    )
    parser.add_argument(
        "--print",
        dest="print_only",
        action="store_true",
        help="Print JSON to stdout without writing to file",
    )

    args = parser.parse_args(argv)

    # Flatten presets in case comma-separated strings were passed
    presets: list[str] | None = None
    if args.presets is not None:
        presets = []
        for p in args.presets:
            presets.extend([item.strip() for item in p.split(",") if item.strip()])

    spec = init_spec(
        name=args.name,
        description=args.description,
        locale=args.locale,
        timezone=args.timezone,
        laravel_version=args.laravel_version,
        filament_version=args.filament_version,
        presets=presets,
        template_path=args.template,
    )

    if args.print_only:
        sys.stdout.write(json.dumps(spec, indent=2, ensure_ascii=False) + "\n")
        return 0

    try:
        out_file = write_spec(spec, args.output, force=args.force)
        print(f"Created specification skeleton at: {out_file}")
        return 0
    except FileExistsError as err:
        sys.stderr.write(f"Error: {err}\n")
        return 1
    except Exception as err:
        sys.stderr.write(f"Failed to write specification: {err}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
