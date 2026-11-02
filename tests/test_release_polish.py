"""Tests for Milestone 6 documentation, release artifacts, and QA polish."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent


class TestReleaseDocumentation:
    """Verifies that all required documentation files exist and meet quality gates."""

    def test_readme_exists_and_contains_required_sections(self) -> None:
        readme_path = ROOT_DIR / "README.md"
        assert readme_path.is_file(), "README.md must exist in root"
        content = readme_path.read_text(encoding="utf-8")

        # Pitch and badges
        assert "Spec-driven development skill for AI agents" in content
        assert "10-Second Demo" in content
        assert "python scripts/validate_spec.py" in content

        # Installation in <= 2 commands & manual copy
        assert "npx skills add" in content
        assert "python laravel-spec-skill/scripts/install.py" in content
        assert "Manual Copy" in content

        # Cross-agent compatibility matrix
        assert "Antigravity" in content and "Verified" in content
        assert "Claude Code" in content and "Experimental" in content
        assert "Cursor" in content and "Experimental" in content
        assert "OpenAI Codex CLI" in content and "Experimental" in content
        assert "Honesty Rule" in content

        # 5 phases
        assert "Phase 1: Discovery" in content
        assert "Phase 2: Spec Generation" in content
        assert "Phase 3: Machine Validation" in content
        assert "Phase 4: Review Gate" in content
        assert "Phase 5: Resumable TDD Build" in content

        # Validation rules overview
        assert "STRUC_001" in content
        assert "NUM_001" in content
        assert "DAG_001" in content
        assert "SEC_001" in content
        assert "29" in content

        # Presets guide
        assert "rtl-fa" in content
        assert "iran-payments" in content
        assert "otp-login" in content
        assert "multi-tenant" in content

        # Limitations & roadmap
        assert "Honest Limitations" in content
        assert "Roadmap" in content

        # Contributing
        assert "Contributing a Preset" in content
        assert "CONTRIBUTING.md" in content

    def test_contributing_guide_completeness(self) -> None:
        contrib_path = ROOT_DIR / "CONTRIBUTING.md"
        assert contrib_path.is_file(), "CONTRIBUTING.md must exist"
        content = contrib_path.read_text(encoding="utf-8")

        assert "pytest -v" in content
        assert "ruff check ." in content
        assert "How to Add New Validation Rules" in content
        assert "Rule Identifier Conventions" in content
        assert "RuleViolation" in content
        assert "Severity" in content
        assert "How to Author New Presets" in content
        assert "Pull Request Checklist" in content

    def test_ci_workflow_configuration(self) -> None:
        ci_path = ROOT_DIR / ".github" / "workflows" / "ci.yml"
        assert ci_path.is_file(), ".github/workflows/ci.yml must exist"
        content = ci_path.read_text(encoding="utf-8")

        # Verify python version matrix
        for py_ver in ["3.10", "3.11", "3.12", "3.13"]:
            assert f'"{py_ver}"' in content or f"'{py_ver}'" in content or py_ver in content

        assert "actions/checkout@v4" in content
        assert "actions/setup-python@v5" in content
        assert "ruff check ." in content
        assert "pytest -v" in content

    def test_issue_templates_exist_and_have_frontmatter(self) -> None:
        issue_template_dir = ROOT_DIR / ".github" / "ISSUE_TEMPLATE"
        assert issue_template_dir.is_dir(), ".github/ISSUE_TEMPLATE directory must exist"

        bug_report = issue_template_dir / "bug_report.md"
        preset_request = issue_template_dir / "preset_request.md"

        assert bug_report.is_file(), "bug_report.md template must exist"
        assert preset_request.is_file(), "preset_request.md template must exist"

        bug_content = bug_report.read_text(encoding="utf-8")
        assert bug_content.startswith("---")
        assert "name: Bug Report" in bug_content
        assert "labels: ['bug', 'triage']" in bug_content or "labels:" in bug_content

        preset_content = preset_request.read_text(encoding="utf-8")
        assert preset_content.startswith("---")
        assert "name: Preset Request" in preset_content
        assert "labels:" in preset_content

    def test_launch_drafts_exist_and_are_informative(self) -> None:
        launch_dir = ROOT_DIR / "docs" / "launch"
        assert launch_dir.is_dir(), "docs/launch directory must exist"

        reddit_claude = launch_dir / "reddit-claudeai.md"
        reddit_laravel = launch_dir / "reddit-laravel.md"
        show_hn = launch_dir / "show-hn.md"

        assert reddit_claude.is_file(), "reddit-claudeai.md must exist"
        assert reddit_laravel.is_file(), "reddit-laravel.md must exist"
        assert show_hn.is_file(), "show-hn.md must exist"

        claude_content = reddit_claude.read_text(encoding="utf-8")
        assert "Claude Code" in claude_content
        assert "29" in claude_content or "invariant" in claude_content

        laravel_content = reddit_laravel.read_text(encoding="utf-8")
        assert "Filament" in laravel_content
        assert "NUM_001" in laravel_content or "float" in laravel_content

        hn_content = show_hn.read_text(encoding="utf-8")
        assert "Show HN" in hn_content
        assert "laravel-spec" in hn_content

    def test_changelog_has_v0_1_0_release_entry(self) -> None:
        changelog_path = ROOT_DIR / "CHANGELOG.md"
        assert changelog_path.is_file()
        content = changelog_path.read_text(encoding="utf-8")

        # Must have release version 0.1.0 with date
        match = re.search(r"## \[0\.1\.0\] - \d{4}-\d{2}-\d{2}", content)
        assert match is not None, "CHANGELOG.md must contain ## [0.1.0] - YYYY-MM-DD"

        # Must document all milestones 0 to 6
        for m in range(7):
            assert f"Milestone {m}" in content, f"Milestone {m} missing from CHANGELOG.md"

    def test_root_forwarding_scripts_execute_cleanly(self, tmp_path: Path) -> None:
        marketplace_spec = ROOT_DIR / "examples" / "marketplace" / "spec.json"

        # 1. validate_spec.py
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT_DIR / "scripts" / "validate_spec.py"),
                str(marketplace_spec),
                "--strict",
            ],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, f"validate_spec stderr: {proc.stderr}"
        assert "PASS" in proc.stdout

        # 2. render_docs.py
        docs_out = tmp_path / "docs"
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT_DIR / "scripts" / "render_docs.py"),
                str(marketplace_spec),
                "--output-dir",
                str(docs_out),
            ],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, f"render_docs stderr: {proc.stderr}"
        assert (docs_out / "00-overview.md").is_file()

        # 3. render_commands.py
        cmds_out = tmp_path / "commands.sh"
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT_DIR / "scripts" / "render_commands.py"),
                str(marketplace_spec),
                "--output",
                str(cmds_out),
            ],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, f"render_commands stderr: {proc.stderr}"
        assert cmds_out.is_file()

        # 4. init_spec.py
        init_out = tmp_path / "new_spec.json"
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT_DIR / "scripts" / "init_spec.py"),
                "--name",
                "TestApp",
                "--output",
                str(init_out),
            ],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, f"init_spec stderr: {proc.stderr}"
        assert init_out.is_file()

        # 5. install.py with --target all
        install_proj = tmp_path / "install_proj"
        install_home = tmp_path / "install_home"
        install_proj.mkdir()
        install_home.mkdir()
        proc = subprocess.run(
            [
                sys.executable,
                str(ROOT_DIR / "scripts" / "install.py"),
                "--target",
                "all",
                "--project-dir",
                str(install_proj),
                "--home-dir",
                str(install_home),
                "--json",
            ],
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 0, f"install.py stderr: {proc.stderr}"
        assert (install_proj / "CLAUDE.md").is_file()
        assert (install_proj / "GEMINI.md").is_file()
        assert (install_proj / "AGENTS.md").is_file()

    def test_demo_tape_exists_and_is_valid_vhs_script(self) -> None:
        tape_file = ROOT_DIR / "demo.tape"
        assert tape_file.is_file(), "demo.tape must exist in repository root"
        content = tape_file.read_text(encoding="utf-8")
        assert "Output demo.gif" in content
        assert "python scripts/validate_spec.py" in content
        assert "render_docs.py" in content
        assert "render_commands.py" in content
