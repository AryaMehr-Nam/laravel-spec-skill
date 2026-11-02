"""Tests for real-world specification examples and architectural presets."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

# Ensure skills/laravel-spec/scripts is on sys.path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "skills" / "laravel-spec" / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from render_commands import render_commands  # noqa: E402
from render_docs import DOC_FILENAMES, render_docs  # noqa: E402
from validate_spec import (  # noqa: E402
    format_cli_output,
    validate_spec,
    validate_spec_file,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
EXAMPLES_DIR = ROOT_DIR / "examples"
MARKETPLACE_DIR = EXAMPLES_DIR / "marketplace"
CRM_DIR = EXAMPLES_DIR / "crm"
PRESETS_DIR = ROOT_DIR / "skills" / "laravel-spec" / "references" / "presets"


def load_example_spec(directory: Path) -> dict[str, Any]:
    """Helper to load and parse an example's spec.json."""
    spec_path = directory / "spec.json"
    assert spec_path.is_file(), f"Expected spec.json at {spec_path}"
    with open(spec_path, encoding="utf-8") as f:
        return json.load(f)


class TestExamplesValidation:
    """Tests ensuring production example specs pass strict validation."""

    def test_marketplace_spec_validates_cleanly(self) -> None:
        spec_path = MARKETPLACE_DIR / "spec.json"
        assert spec_path.exists()
        result = validate_spec_file(spec_path, strict=True)
        assert result.is_valid is True, f"Errors: {result.errors}, Warnings: {result.warnings}"
        assert result.error_count == 0
        assert result.warning_count == 0
        assert len(result.violations) == 0

    def test_crm_spec_validates_cleanly(self) -> None:
        spec_path = CRM_DIR / "spec.json"
        assert spec_path.exists()
        result = validate_spec_file(spec_path, strict=True)
        assert result.is_valid is True, f"Errors: {result.errors}, Warnings: {result.warnings}"
        assert result.error_count == 0
        assert result.warning_count == 0
        assert len(result.violations) == 0

    @pytest.mark.parametrize("example_dir", [MARKETPLACE_DIR, CRM_DIR])
    def test_validator_cli_passes_on_examples(self, example_dir: Path) -> None:
        spec_file = example_dir / "spec.json"
        cmd = [
            sys.executable,
            str(SCRIPTS_DIR / "validate_spec.py"),
            str(spec_file),
            "--strict",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert proc.returncode == 0
        assert "PASS: Specification is valid and adheres to all architecture rules." in proc.stdout


class TestExamplesRenderedArtifacts:
    """Tests verifying pre-rendered docs and commands match deterministic output."""

    @pytest.mark.parametrize("example_dir", [MARKETPLACE_DIR, CRM_DIR])
    def test_all_10_markdown_docs_exist_and_match(self, example_dir: Path) -> None:
        spec = load_example_spec(example_dir)
        expected_docs = render_docs(spec)

        for filename in DOC_FILENAMES:
            file_path = example_dir / filename
            assert file_path.is_file(), f"Missing rendered doc '{filename}' in {example_dir}"
            disk_content = file_path.read_text(encoding="utf-8")
            assert disk_content == expected_docs[filename], (
                f"Discrepancy detected in rendered doc '{filename}' for {example_dir.name}"
            )

    @pytest.mark.parametrize("example_dir", [MARKETPLACE_DIR, CRM_DIR])
    def test_commands_sh_exists_and_matches(self, example_dir: Path) -> None:
        spec = load_example_spec(example_dir)
        expected_commands = render_commands(spec, format_type="shell")

        commands_path = example_dir / "commands.sh"
        assert commands_path.is_file(), f"Missing commands.sh in {example_dir}"
        disk_content = commands_path.read_text(encoding="utf-8")
        assert disk_content == expected_commands, (
            f"Discrepancy detected in commands.sh for {example_dir.name}"
        )

    @pytest.mark.parametrize("example_dir", [MARKETPLACE_DIR, CRM_DIR])
    def test_validation_report_exists_and_matches(self, example_dir: Path) -> None:
        spec = load_example_spec(example_dir)
        result = validate_spec(spec, strict=True)
        expected_report = format_cli_output(result) + "\n"

        val_path = example_dir / "validation.txt"
        assert val_path.is_file(), f"Missing validation.txt in {example_dir}"
        disk_content = val_path.read_text(encoding="utf-8")
        assert disk_content == expected_report
        assert "PASS: Specification is valid and adheres to all architecture rules." in disk_content


class TestPresetsArchitecture:
    """Tests validating presence and structure of presets reference guides."""

    EXPECTED_PRESETS = [
        ("rtl-fa.md", ["rtl-fa", "Vazirmatn", "morilog/jalali", "Jalali"]),
        (
            "iran-payments.md",
            ["iran-payments", "Zarinpal", "Saman", "idempotency_key", "lockForUpdate"],
        ),
        ("otp-login.md", ["otp-login", "120", "nonce", "rate limit", "enumeration"]),
        ("multi-tenant.md", ["multi-tenant", "tenant_id", "Filament", "stancl/tenancy"]),
    ]

    def test_presets_directory_exists(self) -> None:
        assert PRESETS_DIR.is_dir(), f"Expected presets directory at {PRESETS_DIR}"

    @pytest.mark.parametrize("filename,keywords", EXPECTED_PRESETS)
    def test_preset_file_contains_architectural_guidance(
        self, filename: str, keywords: list[str]
    ) -> None:
        preset_file = PRESETS_DIR / filename
        assert preset_file.is_file(), f"Missing preset reference file: {preset_file}"
        content = preset_file.read_text(encoding="utf-8")
        assert len(content) > 500, f"Preset {filename} is too brief ({len(content)} chars)"

        for kw in keywords:
            assert kw.lower() in content.lower(), (
                f"Preset {filename} missing expected keyword '{kw}'"
            )
