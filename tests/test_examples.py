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

    @pytest.mark.parametrize("example_dir", [MARKETPLACE_DIR, CRM_DIR])
    def test_validator_cli_json_mode_on_examples(self, example_dir: Path) -> None:
        spec_file = example_dir / "spec.json"
        cmd = [
            sys.executable,
            str(SCRIPTS_DIR / "validate_spec.py"),
            str(spec_file),
            "--strict",
            "--json",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert proc.returncode == 0
        payload = json.loads(proc.stdout)
        assert payload.get("valid") is True
        assert payload.get("error_count") == 0
        assert payload.get("warning_count") == 0
        assert payload.get("strict") is True


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

    @pytest.mark.parametrize("example_dir", [MARKETPLACE_DIR, CRM_DIR])
    def test_render_docs_cli_matches_directory(self, example_dir: Path, tmp_path: Path) -> None:
        spec_file = example_dir / "spec.json"
        out_dir = tmp_path / f"docs_{example_dir.name}"
        cmd = [
            sys.executable,
            str(SCRIPTS_DIR / "render_docs.py"),
            str(spec_file),
            "-o",
            str(out_dir),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert proc.returncode == 0

        for fname in DOC_FILENAMES:
            gen_file = out_dir / fname
            exp_file = example_dir / fname
            assert gen_file.is_file()
            assert gen_file.read_text(encoding="utf-8") == exp_file.read_text(encoding="utf-8")

    @pytest.mark.parametrize("example_dir", [MARKETPLACE_DIR, CRM_DIR])
    def test_render_commands_cli_formats(self, example_dir: Path, tmp_path: Path) -> None:
        spec_file = example_dir / "spec.json"
        shell_out = tmp_path / f"cmd_{example_dir.name}.sh"

        cmd_shell = [
            sys.executable,
            str(SCRIPTS_DIR / "render_commands.py"),
            str(spec_file),
            "-f",
            "shell",
            "-o",
            str(shell_out),
        ]
        proc_shell = subprocess.run(cmd_shell, capture_output=True, text=True, check=False)
        assert proc_shell.returncode == 0
        expected_shell = (example_dir / "commands.sh").read_text(encoding="utf-8")
        assert shell_out.read_text(encoding="utf-8") == expected_shell

        cmd_json = [
            sys.executable,
            str(SCRIPTS_DIR / "render_commands.py"),
            str(spec_file),
            "-f",
            "json",
        ]
        proc_json = subprocess.run(cmd_json, capture_output=True, text=True, check=False)
        assert proc_json.returncode == 0
        parsed_cmds = json.loads(proc_json.stdout)
        assert isinstance(parsed_cmds, list)
        assert len(parsed_cmds) > 0
        assert any("make:model" in c for c in parsed_cmds)
        assert any("make:policy" in c for c in parsed_cmds)
        assert any("make:filament-resource" in c for c in parsed_cmds)


class TestPresetsArchitecture:
    """Tests validating presence and structure of presets reference guides."""

    EXPECTED_PRESETS = [
        (
            "rtl-fa.md",
            [
                "rtl-fa",
                "Vazirmatn",
                "morilog/jalali",
                "Jalali",
                "zero external cdn",
                "Persian",
                "toLatin",
            ],
        ),
        (
            "iran-payments.md",
            [
                "iran-payments",
                "Zarinpal",
                "Shepa",
                "Saman",
                "idempotency_key",
                "lockForUpdate",
                "Rial",
                "Toman",
            ],
        ),
        (
            "otp-login.md",
            [
                "otp-login",
                "120",
                "nonce",
                "rate limit",
                "enumeration",
                "hash_equals",
            ],
        ),
        (
            "multi-tenant.md",
            [
                "multi-tenant",
                "tenant_id",
                "Filament",
                "stancl/tenancy",
                "BelongsToTenant",
                "scopedToTenant",
            ],
        ),
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

    @pytest.mark.parametrize("filename,_", EXPECTED_PRESETS)
    def test_preset_json_code_blocks_are_valid_json(self, filename: str, _: list[str]) -> None:
        import re

        preset_file = PRESETS_DIR / filename
        content = preset_file.read_text(encoding="utf-8")
        json_blocks = re.findall(r"```json\s*(.*?)\s*```", content, re.DOTALL)
        assert len(json_blocks) >= 1, f"Expected at least 1 json code block in {filename}"

        for i, block in enumerate(json_blocks):
            try:
                parsed = json.loads(block)
                assert isinstance(parsed, dict)
            except Exception as err:
                pytest.fail(f"Invalid JSON in block {i} of {filename}: {err}")


class TestExamplesDomainInvariants:
    """Tests verifying domain-specific architecture invariants across example specs."""

    def test_marketplace_payment_invariants(self) -> None:
        spec = load_example_spec(MARKETPLACE_DIR)
        models = {m["name"]: m for m in spec.get("models", [])}
        assert "Payment" in models
        payment_fields = {f["name"]: f for f in models["Payment"]["fields"]}

        # Idempotency and audit integrity
        assert "idempotency_key" in payment_fields
        assert payment_fields["idempotency_key"].get("unique") is True
        assert "authority" in payment_fields
        assert "tracking_code" in payment_fields
        assert "card_pan_masked" in payment_fields
        assert "verified_at" in payment_fields
        assert "failure_reason" in payment_fields

        # Precision rule: decimal amount with explicit scale
        assert payment_fields["amount"]["type"] == "decimal"
        assert "precision" in payment_fields["amount"]
        assert "scale" in payment_fields["amount"]

    def test_crm_deal_and_activity_workflows(self) -> None:
        spec = load_example_spec(CRM_DIR)
        models = {m["name"]: m for m in spec.get("models", [])}

        assert "Deal" in models
        deal_states = models["Deal"].get("states")
        assert deal_states is not None
        assert deal_states["initial"] == "lead"
        assert set(deal_states["final"]) == {"closed_won", "closed_lost"}

        assert "Activity" in models
        act_states = models["Activity"].get("states")
        assert act_states is not None
        assert act_states["initial"] == "scheduled"
        assert set(act_states["final"]) == {"completed", "cancelled"}

    def test_both_examples_have_complete_milestone_coverage(self) -> None:
        for example_dir in [MARKETPLACE_DIR, CRM_DIR]:
            spec = load_example_spec(example_dir)
            all_model_names = {m["name"] for m in spec.get("models", [])}
            covered_models: set[str] = set()
            for ms in spec.get("milestones", []):
                covered_models.update(ms.get("scope", []))

            uncovered = all_model_names - covered_models
            assert not uncovered, (
                f"{example_dir.name} models not covered in milestones: {uncovered}"
            )
