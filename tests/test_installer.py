"""Tests for multi-agent installer and rollback functionality."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Ensure repo root is on sys.path for importing scripts.install
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.install import (  # noqa: E402
    AGENT_TARGETS,
    ALL_AGENTS,
    MANIFEST_FILENAME,
    POINTER_END,
    POINTER_START,
    Installer,
    inject_pointer_block,
    locate_source_skill_dir,
    main,
    remove_pointer_block,
)

SOURCE_SKILL_DIR = REPO_ROOT / "skills" / "laravel-spec"
INSTALL_SCRIPT = REPO_ROOT / "scripts" / "install.py"


@pytest.fixture
def temp_env(tmp_path: Path):
    """Provide isolated project and home directories for installer testing."""
    proj_dir = tmp_path / "project"
    home_dir = tmp_path / "home"
    proj_dir.mkdir(parents=True)
    home_dir.mkdir(parents=True)
    return proj_dir, home_dir


def test_locate_source_skill_dir():
    """Verify locate_source_skill_dir resolves the canonical skill directory."""
    found = locate_source_skill_dir()
    assert found.is_dir()
    assert (found / "SKILL.md").is_file()
    assert (found / "schemas" / "spec.schema.json").is_file()

    # Custom valid path
    assert locate_source_skill_dir(SOURCE_SKILL_DIR) == SOURCE_SKILL_DIR.resolve()

    # Invalid path
    with pytest.raises(FileNotFoundError):
        locate_source_skill_dir("/non/existent/path/xyz")


def test_pointer_block_lifecycle(tmp_path: Path):
    """Test non-destructive injection and clean removal of pointer blocks."""
    pointer_file = tmp_path / "AGENTS.md"

    # Step 1: Inject into non-existent file
    assert not pointer_file.exists()
    inject_pointer_block(pointer_file)
    assert pointer_file.exists()
    content = pointer_file.read_text(encoding="utf-8")
    assert POINTER_START in content
    assert POINTER_END in content
    assert "Laravel Spec Skill" in content

    # Step 2: Idempotent re-injection (should not duplicate block)
    inject_pointer_block(pointer_file)
    content2 = pointer_file.read_text(encoding="utf-8")
    assert content2.count(POINTER_START) == 1

    # Step 3: Remove from file created exclusively for pointer
    remove_pointer_block(pointer_file)
    assert not pointer_file.exists()


def test_pointer_block_preserves_user_content(tmp_path: Path):
    """Test pointer block injection and removal preserves existing user instructions."""
    pointer_file = tmp_path / "CLAUDE.md"
    user_header = "# Project Rules\n\n1. Always run tests.\n2. Keep code clean.\n"
    pointer_file.write_text(user_header, encoding="utf-8")

    # Inject
    inject_pointer_block(pointer_file)
    injected_content = pointer_file.read_text(encoding="utf-8")
    assert injected_content.startswith("# Project Rules")
    assert POINTER_START in injected_content
    assert POINTER_END in injected_content

    # Remove
    remove_pointer_block(pointer_file)
    assert pointer_file.exists()
    final_content = pointer_file.read_text(encoding="utf-8")
    assert final_content.strip() == user_header.strip()
    assert POINTER_START not in final_content


@pytest.mark.parametrize("agent_id", ALL_AGENTS)
def test_individual_agent_installation_project_mode(agent_id: str, temp_env: tuple[Path, Path]):
    """Verify project-mode installation for each individual agent."""
    proj_dir, home_dir = temp_env
    installer = Installer(project_dir=proj_dir, home_dir=home_dir, source_dir=SOURCE_SKILL_DIR)

    res = installer.install(agents=[agent_id], mode="project")
    target = AGENT_TARGETS[agent_id]
    skill_dir = proj_dir / target.project_skill_path
    pointer_file = proj_dir / target.project_pointer_file

    assert skill_dir.is_dir()
    assert (skill_dir / "SKILL.md").is_file()
    assert (skill_dir / MANIFEST_FILENAME).is_file()
    assert pointer_file.is_file()
    assert POINTER_START in pointer_file.read_text(encoding="utf-8")

    manifest = json.loads((skill_dir / MANIFEST_FILENAME).read_text(encoding="utf-8"))
    assert manifest["agent"] == agent_id
    assert manifest["mode"] == "project"

    assert str(skill_dir) in res["installed_skills"]
    assert str(pointer_file) in res["updated_pointers"]


@pytest.mark.parametrize("agent_id", ALL_AGENTS)
def test_individual_agent_installation_global_mode(agent_id: str, temp_env: tuple[Path, Path]):
    """Verify global-mode installation for each individual agent."""
    proj_dir, home_dir = temp_env
    installer = Installer(project_dir=proj_dir, home_dir=home_dir, source_dir=SOURCE_SKILL_DIR)

    res = installer.install(agents=[agent_id], mode="global")
    target = AGENT_TARGETS[agent_id]
    skill_dir = home_dir / target.global_skill_path
    pointer_file = home_dir / target.global_pointer_file

    assert skill_dir.is_dir()
    assert (skill_dir / "SKILL.md").is_file()
    assert (skill_dir / MANIFEST_FILENAME).is_file()
    assert pointer_file.is_file()
    assert POINTER_START in pointer_file.read_text(encoding="utf-8")

    manifest = json.loads((skill_dir / MANIFEST_FILENAME).read_text(encoding="utf-8"))
    assert manifest["agent"] == agent_id
    assert manifest["mode"] == "global"

    assert str(skill_dir) in res["installed_skills"]
    assert str(pointer_file) in res["updated_pointers"]


def test_install_all_agents_project_mode(temp_env: tuple[Path, Path]):
    """Test installing all agents simultaneously in project mode."""
    proj_dir, home_dir = temp_env
    installer = Installer(project_dir=proj_dir, home_dir=home_dir, source_dir=SOURCE_SKILL_DIR)

    res = installer.install(agents=ALL_AGENTS, mode="project")
    assert len(res["installed_skills"]) >= 3  # claude, cursor, codex/antigravity share .agents

    # Verify skill dirs
    assert (proj_dir / ".claude" / "skills" / "laravel-spec" / "SKILL.md").is_file()
    assert (proj_dir / ".cursor" / "skills" / "laravel-spec" / "SKILL.md").is_file()
    assert (proj_dir / ".agents" / "skills" / "laravel-spec" / "SKILL.md").is_file()

    # Verify pointer files
    assert (proj_dir / "CLAUDE.md").is_file()
    assert (proj_dir / "AGENTS.md").is_file()
    assert (proj_dir / "GEMINI.md").is_file()


def test_idempotent_reinstall(temp_env: tuple[Path, Path]):
    """Test that running install multiple times does not corrupt or duplicate data."""
    proj_dir, home_dir = temp_env
    installer = Installer(project_dir=proj_dir, home_dir=home_dir, source_dir=SOURCE_SKILL_DIR)

    # First install
    installer.install(agents=["claude"], mode="project")
    pointer = proj_dir / "CLAUDE.md"
    first_content = pointer.read_text(encoding="utf-8")

    # Second install
    installer.install(agents=["claude"], mode="project")
    second_content = pointer.read_text(encoding="utf-8")

    assert first_content == second_content
    assert second_content.count(POINTER_START) == 1


def test_clean_uninstall_rollback(temp_env: tuple[Path, Path]):
    """Test complete rollback on uninstall across all targets."""
    proj_dir, home_dir = temp_env
    installer = Installer(project_dir=proj_dir, home_dir=home_dir, source_dir=SOURCE_SKILL_DIR)

    # Install all
    installer.install(agents=ALL_AGENTS, mode="project")

    # Uninstall all
    installer.uninstall(agents=ALL_AGENTS, mode="project")

    # Skills removed
    assert not (proj_dir / ".claude" / "skills" / "laravel-spec").exists()
    assert not (proj_dir / ".cursor" / "skills" / "laravel-spec").exists()
    assert not (proj_dir / ".agents" / "skills" / "laravel-spec").exists()

    # Pointers cleanly removed
    assert not (proj_dir / "CLAUDE.md").exists()
    assert not (proj_dir / "AGENTS.md").exists()
    assert not (proj_dir / "GEMINI.md").exists()

    # Calling uninstall again is completely safe and idempotent
    res = installer.uninstall(agents=ALL_AGENTS, mode="project")
    assert res["removed_skills"] == []
    assert res["cleaned_pointers"] == []


def test_preexisting_directory_backup_and_restore(temp_env: tuple[Path, Path]):
    """Verify that pre-existing directories without manifest are backed up and restored."""
    proj_dir, home_dir = temp_env
    target_skill_dir = proj_dir / ".claude" / "skills" / "laravel-spec"
    target_skill_dir.mkdir(parents=True)
    custom_file = target_skill_dir / "custom_user_file.txt"
    custom_file.write_text("precious user content", encoding="utf-8")

    installer = Installer(project_dir=proj_dir, home_dir=home_dir, source_dir=SOURCE_SKILL_DIR)

    # Install will detect pre-existing directory and create backup
    installer.install(agents=["claude"], mode="project")
    assert (target_skill_dir / "SKILL.md").is_file()
    assert (target_skill_dir / MANIFEST_FILENAME).is_file()

    # Uninstall will remove installed skill and restore the pre-existing directory
    installer.uninstall(agents=["claude"], mode="project")
    assert target_skill_dir.is_dir()
    assert custom_file.is_file()
    assert custom_file.read_text(encoding="utf-8") == "precious user content"
    assert not (target_skill_dir / MANIFEST_FILENAME).exists()


def test_cli_install_and_uninstall(temp_env: tuple[Path, Path]):
    """Test main() CLI execution with argument passing."""
    proj_dir, home_dir = temp_env

    # CLI install --project --agent cursor --json
    code = main([
        "--project",
        "--agent",
        "cursor",
        "--project-dir",
        str(proj_dir),
        "--home-dir",
        str(home_dir),
        "--source",
        str(SOURCE_SKILL_DIR),
        "--json",
    ])
    assert code == 0
    assert (proj_dir / ".cursor" / "skills" / "laravel-spec" / "SKILL.md").is_file()
    assert (proj_dir / "AGENTS.md").is_file()

    # CLI uninstall --project --agent cursor --json
    code_un = main([
        "--project",
        "--agent",
        "cursor",
        "--project-dir",
        str(proj_dir),
        "--home-dir",
        str(home_dir),
        "--source",
        str(SOURCE_SKILL_DIR),
        "--uninstall",
        "--json",
    ])
    assert code_un == 0
    assert not (proj_dir / ".cursor" / "skills" / "laravel-spec").exists()
    assert not (proj_dir / "AGENTS.md").exists()


def test_cli_subprocess_invocation(temp_env: tuple[Path, Path]):
    """Verify installer works via real subprocess execution."""
    proj_dir, home_dir = temp_env

    cmd = [
        sys.executable,
        str(INSTALL_SCRIPT),
        "--agent",
        "antigravity",
        "--project",
        "--project-dir",
        str(proj_dir),
        "--home-dir",
        str(home_dir),
        "--source",
        str(SOURCE_SKILL_DIR),
    ]

    # Install via subprocess
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 0
    assert "Successfully installed laravel-spec for antigravity" in proc.stdout
    assert (proj_dir / ".agents" / "skills" / "laravel-spec" / "SKILL.md").is_file()
    assert (proj_dir / "GEMINI.md").is_file()

    # Uninstall via subprocess
    cmd_un = cmd + ["--uninstall"]
    proc_un = subprocess.run(cmd_un, capture_output=True, text=True)
    assert proc_un.returncode == 0
    assert "Successfully uninstalled laravel-spec for antigravity" in proc_un.stdout
    assert not (proj_dir / ".agents" / "skills" / "laravel-spec").exists()
    assert not (proj_dir / "GEMINI.md").exists()


def test_cli_invalid_arguments():
    """Verify CLI error handling on invalid flags."""
    with pytest.raises(SystemExit) as exc:
        main(["--agent", "invalid-agent"])
    assert exc.value.code != 0


def test_cli_mutually_exclusive_project_and_global():
    """Verify CLI rejects both --project and --global together."""
    with pytest.raises(SystemExit) as exc:
        main(["--project", "--global"])
    assert exc.value.code != 0


def test_shared_skill_directory_partial_uninstall(temp_env: tuple[Path, Path]):
    """Verify partial uninstall preserves shared skill directory and pointers."""
    proj_dir, home_dir = temp_env
    installer = Installer(project_dir=proj_dir, home_dir=home_dir, source_dir=SOURCE_SKILL_DIR)

    # Both codex and antigravity share .agents/skills/laravel-spec in project mode
    installer.install(agents=["codex", "antigravity"], mode="project")
    shared_skill = proj_dir / ".agents" / "skills" / "laravel-spec"
    assert shared_skill.is_dir()
    assert (proj_dir / "AGENTS.md").is_file()
    assert (proj_dir / "GEMINI.md").is_file()

    # Uninstall ONLY antigravity
    res1 = installer.uninstall(agents=["antigravity"], mode="project")
    assert shared_skill.is_dir()  # Still exists for codex!
    assert (proj_dir / "AGENTS.md").is_file()  # Still needed by codex
    assert not (proj_dir / "GEMINI.md").exists()  # Cleanly removed
    assert res1["removed_skills"] == []  # Not removed yet

    # Now uninstall codex
    res2 = installer.uninstall(agents=["codex"], mode="project")
    assert not shared_skill.exists()  # Now cleanly removed
    assert not (proj_dir / "AGENTS.md").exists()  # Cleanly removed
    assert str(shared_skill) in res2["removed_skills"]


def test_invalid_source_path_cli(temp_env: tuple[Path, Path]):
    """Verify CLI returns non-zero error when source path is invalid."""
    proj_dir, home_dir = temp_env
    code = main([
        "--source",
        str(proj_dir / "nonexistent_source"),
        "--project-dir",
        str(proj_dir),
    ])
    assert code != 0


def test_corrupted_manifest_refuses_uninstall(temp_env: tuple[Path, Path]):
    """Verify that a corrupted or non-spec manifest is protected against deletion on uninstall."""
    proj_dir, home_dir = temp_env
    claude_skill = proj_dir / ".claude" / "skills" / "laravel-spec"
    claude_skill.mkdir(parents=True)
    manifest_file = claude_skill / MANIFEST_FILENAME
    manifest_file.write_text("{invalid json corrupt!", encoding="utf-8")
    user_file = claude_skill / "my_precious_notes.txt"
    user_file.write_text("Do not lose this content", encoding="utf-8")

    installer = Installer(project_dir=proj_dir, home_dir=home_dir, source_dir=SOURCE_SKILL_DIR)
    res = installer.uninstall(agents=["claude"], mode="project")

    # Directory and files must remain untouched
    assert claude_skill.is_dir()
    assert user_file.is_file()
    assert user_file.read_text(encoding="utf-8") == "Do not lose this content"
    assert res["removed_skills"] == []


def test_corrupted_manifest_backed_up_on_install(temp_env: tuple[Path, Path]):
    """Verify pre-existing directory with invalid manifest is backed up before install."""
    proj_dir, home_dir = temp_env
    claude_skill = proj_dir / ".claude" / "skills" / "laravel-spec"
    claude_skill.mkdir(parents=True)
    (claude_skill / MANIFEST_FILENAME).write_text("not json", encoding="utf-8")
    user_file = claude_skill / "pre_existing.txt"
    user_file.write_text("pre-existing unmanaged data", encoding="utf-8")

    installer = Installer(project_dir=proj_dir, home_dir=home_dir, source_dir=SOURCE_SKILL_DIR)
    installer.install(agents=["claude"], mode="project")

    # Backup was created
    bak_dir = claude_skill.with_name(claude_skill.name + ".bak.laravel-spec")
    assert bak_dir.is_dir()
    assert (bak_dir / "pre_existing.txt").is_file()

    # Installed skill is active
    assert (claude_skill / "SKILL.md").is_file()

    # Uninstall restores the backup
    installer.uninstall(agents=["claude"], mode="project")
    assert claude_skill.is_dir()
    restored_file = claude_skill / "pre_existing.txt"
    assert restored_file.is_file()
    assert restored_file.read_text(encoding="utf-8") == "pre-existing unmanaged data"


def test_pointer_block_in_middle_preserves_section_separation(tmp_path: Path):
    """Test pointer block removal when placed between sections preserves blank line separation."""
    pointer_file = tmp_path / "CLAUDE.md"
    middle_content = (
        f"# Section A\n\nNotes for section A.\n\n{POINTER_START}\n"
        f"### Laravel Spec Skill\nSome skill notes\n{POINTER_END}\n\n"
        f"# Section B\n\nNotes for section B.\n"
    )
    pointer_file.write_text(middle_content, encoding="utf-8")

    remove_pointer_block(pointer_file)
    cleaned = pointer_file.read_text(encoding="utf-8")
    assert POINTER_START not in cleaned
    assert "# Section A\n\nNotes for section A.\n\n# Section B" in cleaned


def test_same_source_and_target_directory(tmp_path: Path):
    """Verify installing when source_dir equals target_dir updates manifest safely."""
    from scripts.install import install_skill_directory

    temp_skill = tmp_path / "skill"
    temp_skill.mkdir()
    (temp_skill / "SKILL.md").write_text("# Skill", encoding="utf-8")

    # Install targeting itself
    install_skill_directory(temp_skill, temp_skill, "claude", "project")
    assert (temp_skill / MANIFEST_FILENAME).is_file()


def test_case_insensitive_agent_ids(temp_env: tuple[Path, Path]):
    """Verify installer handles uppercase/mixed-case agent IDs properly."""
    proj_dir, home_dir = temp_env
    installer = Installer(project_dir=proj_dir, home_dir=home_dir, source_dir=SOURCE_SKILL_DIR)

    res_in = installer.install(agents=["CLAUDE", "Cursor"], mode="project")
    assert len(res_in["installed_skills"]) == 2
    assert (proj_dir / ".claude" / "skills" / "laravel-spec" / "SKILL.md").is_file()
    assert (proj_dir / ".cursor" / "skills" / "laravel-spec" / "SKILL.md").is_file()

    res_un = installer.uninstall(agents=["claude", "CURSOR"], mode="project")
    assert len(res_un["removed_skills"]) == 2
    assert not (proj_dir / ".claude" / "skills" / "laravel-spec").exists()
    assert not (proj_dir / ".cursor" / "skills" / "laravel-spec").exists()


def test_forwarding_scripts_cli():
    """Verify root scripts/ forwarding entrypoints execute properly."""
    validate_script = REPO_ROOT / "scripts" / "validate_spec.py"
    crm_spec = REPO_ROOT / "examples" / "crm" / "spec.json"

    proc = subprocess.run(
        [sys.executable, str(validate_script), str(crm_spec), "--strict"],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert "PASS:" in proc.stdout


