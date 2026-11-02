"""Artisan command generator for Laravel and Filament specifications.

Extracts models, policies, and Filament panel resources from spec.json
and generates an ordered list of dry-run artisan CLI commands (e.g.,
make:model -mfsc, make:policy, make:filament-resource).
Standard library only (Python 3.10+). NEVER executes commands.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import deque
from pathlib import Path
from typing import Any


def _as_list(val: Any) -> list[Any]:
    """Ensure value is a list; otherwise return empty list."""
    if isinstance(val, list):
        return val
    return []


def _as_dict(val: Any) -> dict[str, Any]:
    """Ensure value is a dictionary; otherwise return empty dictionary."""
    if isinstance(val, dict):
        return val
    return {}


def _studly(name: str) -> str:
    """Convert snake_case or kebab-case to StudlyCase."""
    clean = name.replace("-", "_")
    return "".join(part.capitalize() for part in clean.split("_") if part)


def sort_models_by_dependency(models: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort models topologically so referenced parent models precede dependents.

    If dependencies form a cycle or cannot be resolved, falls back gracefully
    to original declaration order.
    """
    valid_models = [m for m in _as_list(models) if isinstance(m, dict) and m.get("name")]
    model_names = [str(m.get("name")) for m in valid_models]
    model_set = set(model_names)
    model_by_name = {str(m.get("name")): m for m in valid_models}

    in_degree: dict[str, int] = {name: 0 for name in model_names}
    adj: dict[str, list[str]] = {name: [] for name in model_names}

    for m in valid_models:
        mname = str(m.get("name"))

        # Look for referenced foreign models
        dep_names: set[str] = set()
        for f in _as_list(m.get("fields")):
            if isinstance(f, dict) and isinstance(f.get("foreign"), dict):
                target = f.get("foreign", {}).get("model")
                if target and str(target) in model_set and str(target) != mname:
                    dep_names.add(str(target))

        for r in _as_list(m.get("relations")):
            if isinstance(r, dict) and r.get("type") in ("belongsTo", "morphTo"):
                target = r.get("model")
                if target and str(target) in model_set and str(target) != mname:
                    dep_names.add(str(target))

        # target must be created before mname: edge target -> mname
        for dep in sorted(dep_names):
            adj[dep].append(mname)
            in_degree[mname] += 1

    queue = deque([name for name in model_names if in_degree[name] == 0])
    ordered_names: list[str] = []

    while queue:
        curr = queue.popleft()
        ordered_names.append(curr)
        for neighbor in adj[curr]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # If cycle detected or some models skipped, append remaining in original order
    if len(ordered_names) < len(model_names):
        remaining = [name for name in model_names if name not in ordered_names]
        ordered_names.extend(remaining)

    return [model_by_name[name] for name in ordered_names if name in model_by_name]


def generate_artisan_commands(spec: dict[str, Any] | None) -> list[str]:
    """Generate ordered list of artisan commands from specification.

    Args:
        spec: Valid specification dictionary or None.

    Returns:
        List of command strings ready for inspection or script execution.
    """
    commands: list[str] = []
    safe_spec = _as_dict(spec)

    models = [m for m in _as_list(safe_spec.get("models")) if isinstance(m, dict) and m.get("name")]
    policies = [
        p for p in _as_list(safe_spec.get("policies")) if isinstance(p, dict) and p.get("model")
    ]
    filament = _as_dict(safe_spec.get("filament"))
    panels = [pan for pan in _as_list(filament.get("panels")) if isinstance(pan, dict)]

    # 1. Filament Panels (skip default 'admin' if only admin, or create explicit)
    created_panels: set[str] = set()
    for pan in panels:
        pid = pan.get("id")
        if pid and pid != "admin" and pid not in created_panels:
            commands.append(f"php artisan make:filament-panel {pid}")
            created_panels.add(pid)

    # 2. Enums (for enum fields defined on models)
    created_enums: set[str] = set()
    for m in models:
        mname = m.get("name", "")
        for f in _as_list(m.get("fields")):
            if isinstance(f, dict) and str(f.get("type", "")).lower() == "enum":
                fname = f.get("name", "")
                enum_name = f"{mname}{_studly(fname)}Enum"
                if enum_name not in created_enums:
                    commands.append(f"php artisan make:enum {enum_name}")
                    created_enums.add(enum_name)

    # 3. Eloquent Models with Migration, Factory, Seeder, and Controller
    ordered_models = sort_models_by_dependency(models)
    for m in ordered_models:
        mname = m.get("name")
        commands.append(f"php artisan make:model {mname} -mfsc")

    # 4. Authorization Policies
    created_policies: set[str] = set()
    for pol in policies:
        mname = pol.get("model")
        if mname and mname not in created_policies:
            commands.append(f"php artisan make:policy {mname}Policy --model={mname}")
            created_policies.add(mname)

    # 5. Filament Resources
    created_resources: set[tuple[str, str]] = set()
    for pan in panels:
        pid = pan.get("id", "admin") or "admin"
        for res in _as_list(pan.get("resources")):
            if isinstance(res, dict) and res.get("model"):
                mname = res.get("model")
                res_key = (pid, str(mname))
                if res_key in created_resources:
                    continue
                created_resources.add(res_key)
                if pid == "admin":
                    commands.append(f"php artisan make:filament-resource {mname}")
                else:
                    commands.append(f"php artisan make:filament-resource {mname} --panel={pid}")

    return commands


def render_shell_script(spec: dict[str, Any] | None, commands: list[str]) -> str:
    """Render commands into a structured executable shell script format."""
    safe_spec = _as_dict(spec)
    proj = _as_dict(safe_spec.get("project"))
    proj_name = proj.get("name", "Laravel Application") or "Laravel Application"

    lines = [
        "#!/usr/bin/env bash",
        "# " + "-" * 75,
        f"# Laravel & Filament Artisan Commands for: {proj_name}",
        "# Generated deterministically from spec.json",
        "# NOTE: Dry-run inspection only. Review before running in production.",
        "# " + "-" * 75,
        "set -euo pipefail",
        "",
        'echo "==> Starting Artisan scaffolding for ' + proj_name + '..."',
        "",
    ]

    panel_cmds = [c for c in commands if "make:filament-panel" in c]
    enum_cmds = [c for c in commands if "make:enum" in c]
    model_cmds = [c for c in commands if "make:model" in c]
    policy_cmds = [c for c in commands if "make:policy" in c]
    resource_cmds = [c for c in commands if "make:filament-resource" in c]

    if panel_cmds:
        lines.append("# Step 1: Filament Panels")
        for c in panel_cmds:
            lines.append(c)
        lines.append("")

    if enum_cmds:
        lines.append("# Step 2: Enums")
        for c in enum_cmds:
            lines.append(c)
        lines.append("")

    if model_cmds:
        lines.append("# Step 3: Eloquent Models & Migrations (-mfsc)")
        for c in model_cmds:
            lines.append(c)
        lines.append("")

    if policy_cmds:
        lines.append("# Step 4: Authorization Policies")
        for c in policy_cmds:
            lines.append(c)
        lines.append("")

    if resource_cmds:
        lines.append("# Step 5: Filament Resources")
        for c in resource_cmds:
            lines.append(c)
        lines.append("")

    lines.append('echo "==> Artisan scaffolding completed successfully."')
    lines.append("")
    return "\n".join(lines)


def render_commands(spec: dict[str, Any] | None, format_type: str = "shell") -> str:
    """Render artisan commands in specified format ('shell', 'list', 'json').

    Args:
        spec: Valid specification dictionary or None.
        format_type: Output format: 'shell' (bash script), 'list' (lines), or 'json'.

    Returns:
        Formatted string representation.
    """
    commands = generate_artisan_commands(spec)

    if format_type == "json":
        return json.dumps(commands, indent=2) + "\n"
    if format_type == "list":
        return "\n".join(commands) + ("\n" if commands else "")
    return render_shell_script(spec, commands)


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for render_commands."""
    parser = argparse.ArgumentParser(
        description="Generate ordered Artisan CLI commands from spec.json (dry-run only)."
    )
    parser.add_argument(
        "spec_file",
        nargs="?",
        default="spec/spec.json",
        help="Path to spec.json (default: 'spec/spec.json')",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["shell", "list", "json"],
        default="shell",
        help="Output format: shell (default), list, or json",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Optional destination file to save rendered commands",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Dry run flag (always enabled; commands are never executed)",
    )

    args = parser.parse_args(argv)

    try:
        spec_path = Path(args.spec_file).resolve()
        if not spec_path.is_file():
            sys.stderr.write(f"Error: Specification file not found at '{spec_path}'\n")
            return 1

        with open(spec_path, encoding="utf-8") as f:
            spec = json.load(f)

        rendered = render_commands(spec, format_type=args.format)

        if args.output:
            out_file = Path(args.output).resolve()
            out_file.parent.mkdir(parents=True, exist_ok=True)
            out_file.write_text(rendered, encoding="utf-8", newline="\n")
            print(f"Rendered {args.format} artisan commands saved to: {out_file}")
        else:
            sys.stdout.write(rendered)

        return 0

    except Exception as err:
        sys.stderr.write(f"Failed to render commands: {err}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
