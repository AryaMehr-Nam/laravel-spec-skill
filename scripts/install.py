"""Multi-agent installer and configuration manager for laravel-spec skill.

Supports Claude Code, Cursor, OpenAI Codex CLI, and Antigravity across
both project-local and user-global installation targets.
Zero runtime dependencies (Python 3.10+ standard library only).
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

MANIFEST_FILENAME = ".laravel-spec-manifest.json"
BACKUP_SUFFIX = ".bak.laravel-spec"

POINTER_START = "<!-- LARAVEL-SPEC-SKILL:START -->"
POINTER_END = "<!-- LARAVEL-SPEC-SKILL:END -->"
POINTER_BLOCK = f"""{POINTER_START}
### Laravel Spec Skill
This environment is configured with `laravel-spec` for specification-driven
Laravel and Filament development. When tasked with specifying, architecting,
or building Laravel or Filament applications, activate and follow `laravel-spec`.
{POINTER_END}"""


@dataclass(frozen=True)
class AgentTarget:
    """Target directory and pointer specification for a supported agent."""

    agent_id: str
    display_name: str
    project_skill_path: Path
    global_skill_path: Path
    project_pointer_file: Path
    global_pointer_file: Path


AGENT_TARGETS: dict[str, AgentTarget] = {
    "claude": AgentTarget(
        agent_id="claude",
        display_name="Claude Code",
        project_skill_path=Path(".claude/skills/laravel-spec"),
        global_skill_path=Path(".claude/skills/laravel-spec"),
        project_pointer_file=Path("CLAUDE.md"),
        global_pointer_file=Path(".claude/CLAUDE.md"),
    ),
    "cursor": AgentTarget(
        agent_id="cursor",
        display_name="Cursor",
        project_skill_path=Path(".cursor/skills/laravel-spec"),
        global_skill_path=Path(".cursor/skills/laravel-spec"),
        project_pointer_file=Path("AGENTS.md"),
        global_pointer_file=Path(".cursor/AGENTS.md"),
    ),
    "codex": AgentTarget(
        agent_id="codex",
        display_name="OpenAI Codex CLI",
        project_skill_path=Path(".agents/skills/laravel-spec"),
        global_skill_path=Path(".codex/skills/laravel-spec"),
        project_pointer_file=Path("AGENTS.md"),
        global_pointer_file=Path(".codex/AGENTS.md"),
    ),
    "antigravity": AgentTarget(
        agent_id="antigravity",
        display_name="Antigravity",
        project_skill_path=Path(".agents/skills/laravel-spec"),
        global_skill_path=Path(".gemini/config/skills/laravel-spec"),
        project_pointer_file=Path("GEMINI.md"),
        global_pointer_file=Path(".gemini/GEMINI.md"),
    ),
}

ALL_AGENTS = list(AGENT_TARGETS.keys())


def locate_source_skill_dir(custom_path: str | Path | None = None) -> Path:
    """Locate source skills/laravel-spec directory."""
    if custom_path:
        p = Path(custom_path).resolve()
        if p.is_dir() and (p / "SKILL.md").is_file():
            return p
        raise FileNotFoundError(f"Custom source skill path invalid: {custom_path}")

    # Relative to this script in scripts/install.py -> repo_root/skills/laravel-spec
    script_parent = Path(__file__).resolve().parent
    candidates = [
        script_parent.parent / "skills" / "laravel-spec",
        script_parent / "skills" / "laravel-spec",
        Path.cwd() / "skills" / "laravel-spec",
    ]
    for cand in candidates:
        if cand.is_dir() and (cand / "SKILL.md").is_file():
            return cand.resolve()

    raise FileNotFoundError(
        "Could not automatically locate 'skills/laravel-spec' source directory. "
        "Please provide --source /path/to/skills/laravel-spec."
    )


def inject_pointer_block(pointer_file: Path) -> bool:
    """Non-destructively append marked pointer block to pointer file.

    Preserves all existing user instructions. If pointer file does not exist,
    creates it. Idempotent: does not duplicate if already present.
    """
    if pointer_file.exists():
        content = pointer_file.read_text(encoding="utf-8")
        if POINTER_START in content:
            return True  # Already present

        # Create backup if not already present
        bak_file = pointer_file.with_name(pointer_file.name + BACKUP_SUFFIX)
        if not bak_file.exists():
            bak_file.write_text(content, encoding="utf-8")

        separator = ""
        if content and not content.endswith("\n\n"):
            separator = "\n" if content.endswith("\n") else "\n\n"
        new_content = f"{content}{separator}{POINTER_BLOCK}\n"
        pointer_file.write_text(new_content, encoding="utf-8")
    else:
        pointer_file.parent.mkdir(parents=True, exist_ok=True)
        pointer_file.write_text(f"{POINTER_BLOCK}\n", encoding="utf-8")
    return True


def remove_pointer_block(pointer_file: Path) -> bool:
    """Cleanly remove marked pointer block from pointer file without touching user content.

    If file becomes empty and was created solely for this pointer, it is cleanly deleted.
    """
    if not pointer_file.exists():
        return True

    content = pointer_file.read_text(encoding="utf-8")
    if POINTER_START not in content:
        return True

    pattern = rf"(?:\r?\n)*{re.escape(POINTER_START)}[\s\S]*?{re.escape(POINTER_END)}(?:\r?\n)*"
    cleaned = re.sub(pattern, "\n", content).strip()

    bak_file = pointer_file.with_name(pointer_file.name + BACKUP_SUFFIX)

    if not cleaned:
        pointer_file.unlink()
        if bak_file.exists():
            bak_file.unlink()
    else:
        pointer_file.write_text(cleaned + "\n", encoding="utf-8")
        if bak_file.exists():
            bak_content = bak_file.read_text(encoding="utf-8").strip()
            if cleaned == bak_content:
                bak_file.unlink()
    return True


def _cleanup_empty_parents(parent: Path) -> None:
    """Recursively remove empty parent directories up to 2 levels."""
    for _ in range(2):
        if parent.exists() and not any(parent.iterdir()):
            try:
                parent.rmdir()
                parent = parent.parent
            except OSError:
                break
        else:
            break


def install_skill_directory(
    source_dir: Path, target_dir: Path, agent_id: str, mode: str
) -> None:
    """Copy skill directory tree to target destination with manifest and backup protection."""
    manifest_file = target_dir / MANIFEST_FILENAME
    existing_agents: list[str] = []

    if target_dir.exists():
        if manifest_file.exists():
            try:
                data = json.loads(manifest_file.read_text(encoding="utf-8"))
                existing_agents = list(data.get("agents", []))
                if not existing_agents and "agent" in data:
                    existing_agents = [data["agent"]]
            except Exception:
                existing_agents = []
        else:
            # Target existed before installer touched it; create backup
            bak_dir = target_dir.with_name(target_dir.name + BACKUP_SUFFIX)
            if not bak_dir.exists():
                shutil.copytree(target_dir, bak_dir, dirs_exist_ok=True)

    if agent_id not in existing_agents:
        existing_agents.append(agent_id)

    target_dir.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        source_dir,
        target_dir,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache", ".DS_Store"),
    )

    manifest_data: dict[str, Any] = {
        "skill": "laravel-spec",
        "agent": agent_id,
        "agents": list(sorted(set(existing_agents))),
        "mode": mode,
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "source_path": str(source_dir.resolve()),
    }
    manifest_file.write_text(json.dumps(manifest_data, indent=2), encoding="utf-8")


def uninstall_skill_directory(target_dir: Path, agent_id: str | None = None) -> bool:
    """Safely remove skill directory or unregister agent, restoring backup when empty.

    Returns:
        True if the skill directory was completely removed, False if retained for other agents.
    """
    if not target_dir.exists():
        return True

    manifest_file = target_dir / MANIFEST_FILENAME
    bak_dir = target_dir.with_name(target_dir.name + BACKUP_SUFFIX)

    if manifest_file.exists():
        try:
            data = json.loads(manifest_file.read_text(encoding="utf-8"))
            agents = list(data.get("agents", []))
            if not agents and "agent" in data:
                agents = [data["agent"]]
        except Exception:
            agents = []

        if agent_id and agent_id in agents:
            agents.remove(agent_id)

        if not agents or not agent_id:
            shutil.rmtree(target_dir, ignore_errors=True)
            if bak_dir.exists():
                shutil.copytree(bak_dir, target_dir, dirs_exist_ok=True)
                shutil.rmtree(bak_dir, ignore_errors=True)
            _cleanup_empty_parents(target_dir.parent)
            return True
        else:
            data["agents"] = agents
            manifest_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
            return False
    else:
        # Pre-existing user directory with no manifest: do not delete
        return False


def is_agent_installed(installer: Installer, agent_id: str, mode: str) -> bool:
    """Check if a specific agent currently has an active installed skill."""
    target = AGENT_TARGETS[agent_id]
    skill_path = installer.get_skill_path(target, mode)
    if not skill_path.is_dir():
        return False
    manifest_file = skill_path / MANIFEST_FILENAME
    if not manifest_file.is_file():
        return False
    try:
        data = json.loads(manifest_file.read_text(encoding="utf-8"))
        agents = data.get("agents", [])
        if not agents and "agent" in data:
            agents = [data["agent"]]
        return agent_id in agents
    except Exception:
        return False


class Installer:
    """Coordinates installation, pointer injection, and rollback across agents."""

    def __init__(
        self,
        project_dir: Path | None = None,
        home_dir: Path | None = None,
        source_dir: Path | None = None,
    ) -> None:
        self.project_dir = (project_dir or Path.cwd()).resolve()
        self.home_dir = (home_dir or Path.home()).resolve()
        self.source_dir = locate_source_skill_dir(source_dir)

    def get_skill_path(self, target: AgentTarget, mode: str) -> Path:
        """Resolve absolute skill destination path for given agent and mode."""
        if mode == "global":
            return (self.home_dir / target.global_skill_path).resolve()
        return (self.project_dir / target.project_skill_path).resolve()

    def get_pointer_path(self, target: AgentTarget, mode: str) -> Path:
        """Resolve absolute pointer file path for given agent and mode."""
        if mode == "global":
            return (self.home_dir / target.global_pointer_file).resolve()
        return (self.project_dir / target.project_pointer_file).resolve()

    def install(self, agents: list[str], mode: str = "project") -> dict[str, Any]:
        """Install laravel-spec skill for specified agents and mode."""
        installed_skills: list[str] = []
        updated_pointers: list[str] = []

        for agent_id in agents:
            target = AGENT_TARGETS[agent_id]
            skill_dest = self.get_skill_path(target, mode)
            pointer_dest = self.get_pointer_path(target, mode)

            install_skill_directory(self.source_dir, skill_dest, agent_id, mode)
            installed_skills.append(str(skill_dest))

            inject_pointer_block(pointer_dest)
            updated_pointers.append(str(pointer_dest))

        return {
            "mode": mode,
            "agents": agents,
            "installed_skills": list(sorted(set(installed_skills))),
            "updated_pointers": list(sorted(set(updated_pointers))),
        }

    def uninstall(self, agents: list[str], mode: str = "project") -> dict[str, Any]:
        """Uninstall laravel-spec skill for specified agents and mode."""
        removed_skills: list[str] = []
        cleaned_pointers: list[str] = []

        # Step 1: Remove or unregister agents from skill directories
        for agent_id in agents:
            target = AGENT_TARGETS[agent_id]
            skill_dest = self.get_skill_path(target, mode)
            if skill_dest.exists():
                was_removed = uninstall_skill_directory(skill_dest, agent_id=agent_id)
                if was_removed:
                    removed_skills.append(str(skill_dest))

        # Step 2: Clean up pointer files only if no remaining installed agent needs them
        for agent_id in agents:
            target = AGENT_TARGETS[agent_id]
            pointer_dest = self.get_pointer_path(target, mode)

            if not pointer_dest.exists():
                continue

            still_needed = any(
                is_agent_installed(self, other_id, mode)
                for other_id in ALL_AGENTS
                if self.get_pointer_path(AGENT_TARGETS[other_id], mode) == pointer_dest
            )
            if not still_needed:
                remove_pointer_block(pointer_dest)
                cleaned_pointers.append(str(pointer_dest))

        return {
            "mode": mode,
            "agents": agents,
            "removed_skills": list(sorted(set(removed_skills))),
            "cleaned_pointers": list(sorted(set(cleaned_pointers))),
        }


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="install.py",
        description="Multi-agent installer and configurator for laravel-spec skill.",
    )
    parser.add_argument(
        "--agent",
        choices=["claude", "cursor", "codex", "antigravity", "all"],
        default="all",
        help="Target agent environment (default: all).",
    )
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--project",
        action="store_true",
        help="Install locally in project workspace (default mode).",
    )
    mode_group.add_argument(
        "--global",
        dest="global_mode",
        action="store_true",
        help="Install globally in user home directory.",
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="Remove installed skill and pointer blocks.",
    )
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=None,
        help="Override project root directory (useful for testing).",
    )
    parser.add_argument(
        "--home-dir",
        type=Path,
        default=None,
        help="Override home directory (useful for testing).",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=None,
        help="Override source skills/laravel-spec directory.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output structured JSON summary.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI execution entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)

    mode = "global" if args.global_mode else "project"
    agents = ALL_AGENTS if args.agent == "all" else [args.agent]

    try:
        installer = Installer(
            project_dir=args.project_dir,
            home_dir=args.home_dir,
            source_dir=args.source,
        )
    except FileNotFoundError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1

    if args.uninstall:
        result = installer.uninstall(agents=agents, mode=mode)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Successfully uninstalled laravel-spec for {', '.join(agents)} ({mode} mode).")
            for p in result["removed_skills"]:
                print(f"  - Removed skill: {p}")
            for p in result["cleaned_pointers"]:
                print(f"  - Cleaned pointer: {p}")
    else:
        result = installer.install(agents=agents, mode=mode)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Successfully installed laravel-spec for {', '.join(agents)} ({mode} mode).")
            for p in result["installed_skills"]:
                print(f"  - Installed skill: {p}")
            for p in result["updated_pointers"]:
                print(f"  - Updated pointer: {p}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
