"""Tests for Laravel Filament specification validator."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Ensure skills/laravel-spec/scripts is on sys.path
SCRIPTS_DIR = (
    Path(__file__).resolve().parent.parent / "skills" / "laravel-spec" / "scripts"
)
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from validate_spec import (  # noqa: E402
    RuleViolation,
    Severity,
    ValidationResult,
    validate_spec,
    validate_spec_file,
)

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
VALID_DIR = FIXTURES_DIR / "valid"
BROKEN_DIR = FIXTURES_DIR / "broken"
TEMPLATE_PATH = (
    Path(__file__).resolve().parent.parent
    / "skills"
    / "laravel-spec"
    / "templates"
    / "empty-spec.json"
)


class TestValidFixtures:
    """Tests ensuring valid specifications pass without violations."""

    def test_minimal_valid(self) -> None:
        path = VALID_DIR / "minimal_valid.json"
        result = validate_spec_file(path, strict=True)
        assert result.is_valid is True
        assert result.error_count == 0
        assert result.warning_count == 0
        assert len(result.violations) == 0

    def test_marketplace_valid(self) -> None:
        path = VALID_DIR / "marketplace_valid.json"
        result = validate_spec_file(path, strict=True)
        assert result.is_valid is True
        assert result.error_count == 0
        assert result.warning_count == 0
        assert len(result.violations) == 0

    def test_empty_spec_template(self) -> None:
        assert TEMPLATE_PATH.exists()
        result = validate_spec_file(TEMPLATE_PATH, strict=True)
        assert result.is_valid is True
        assert result.error_count == 0
        assert result.warning_count == 0


class TestBrokenFixtures:
    """Tests verifying that broken fixtures trigger exact expected rule IDs."""

    @pytest.mark.parametrize(
        "fixture_file",
        [f.name for f in BROKEN_DIR.glob("*.json")],
    )
    def test_broken_fixture_triggers_expected_rule(self, fixture_file: str) -> None:
        path = BROKEN_DIR / fixture_file
        # Parse expected rule ID from filename, e.g. broken_REL_001.json -> REL_001
        parts = fixture_file.replace("broken_", "").replace(".json", "").split("_")
        expected_rule_id = f"{parts[0]}_{parts[1]}"

        # Validate with strict=True so both errors and warnings cause failure
        result = validate_spec_file(path, strict=True)
        assert result.is_valid is False, f"Fixture {fixture_file} unexpectedly passed!"

        triggered_rule_ids = {v.rule_id for v in result.violations}
        assert expected_rule_id in triggered_rule_ids, (
            f"Expected rule {expected_rule_id} not triggered in {fixture_file}. "
            f"Got: {triggered_rule_ids}"
        )

        # Ensure all violations have complete metadata
        for violation in result.violations:
            assert violation.rule_id
            assert violation.message
            assert violation.path
            assert violation.fix_hint
            assert isinstance(violation.severity, Severity)


class TestStrictMode:
    """Tests verifying behavior of strict mode on warnings."""

    def test_warning_in_normal_mode_is_valid(self) -> None:
        path = BROKEN_DIR / "broken_REL_003.json"
        result = validate_spec_file(path, strict=False)
        assert result.is_valid is True
        assert result.error_count == 0
        assert result.warning_count > 0
        assert any(v.rule_id == "REL_003" for v in result.warnings)

    def test_warning_in_strict_mode_is_invalid(self) -> None:
        path = BROKEN_DIR / "broken_REL_003.json"
        result = validate_spec_file(path, strict=True)
        assert result.is_valid is False
        assert result.error_count == 0
        assert result.warning_count > 0

    def test_unreferenced_role_warning(self) -> None:
        path = BROKEN_DIR / "broken_AUTH_005.json"
        normal_res = validate_spec_file(path, strict=False)
        strict_res = validate_spec_file(path, strict=True)
        assert normal_res.is_valid is True
        assert strict_res.is_valid is False
        assert any(v.rule_id == "AUTH_005" for v in normal_res.warnings)


class TestEdgeCasesAndFileHandling:
    """Tests covering error paths, malformed files, and direct validation API."""

    def test_file_not_found(self, tmp_path: Path) -> None:
        non_existent = tmp_path / "does_not_exist.json"
        result = validate_spec_file(non_existent)
        assert result.is_valid is False
        assert any(v.rule_id == "STRUC_001" for v in result.errors)

    def test_malformed_json_file(self, tmp_path: Path) -> None:
        bad_json = tmp_path / "bad.json"
        bad_json.write_text("{ this is not json }", encoding="utf-8")
        result = validate_spec_file(bad_json)
        assert result.is_valid is False
        assert any(v.rule_id == "STRUC_001" for v in result.errors)

    def test_top_level_project_not_dict(self) -> None:
        raw_spec = {
            "project": "invalid_string",
            "roles": [],
            "models": [],
            "policies": [],
            "filament": {"panels": []},
            "milestones": [],
        }
        result = validate_spec(raw_spec)
        assert result.is_valid is False
        assert any("must be an object" in v.message for v in result.errors)

    def test_data_structures_serialization(self) -> None:
        violation = RuleViolation(
            rule_id="TEST_001",
            severity=Severity.ERROR,
            message="Test message",
            path="spec.test",
            fix_hint="Test fix hint",
        )
        res = ValidationResult(is_valid=False, violations=[violation], strict=False)
        d = res.to_dict()
        assert d["valid"] is False
        assert d["error_count"] == 1
        assert d["warning_count"] == 0
        assert len(d["errors"]) == 1
        assert d["errors"][0]["rule_id"] == "TEST_001"
        assert d["errors"][0]["severity"] == "error"


class TestCliInterface:
    """Tests verifying the command line interface via subprocess."""

    def test_cli_valid_spec_exit_code_zero(self) -> None:
        spec_file = str(VALID_DIR / "minimal_valid.json")
        cmd = [sys.executable, str(SCRIPTS_DIR / "validate_spec.py"), spec_file]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert proc.returncode == 0
        assert "PASS:" in proc.stdout

    def test_cli_invalid_spec_exit_code_one(self) -> None:
        spec_file = str(BROKEN_DIR / "broken_STRUC_001.json")
        cmd = [sys.executable, str(SCRIPTS_DIR / "validate_spec.py"), spec_file]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert proc.returncode == 1
        assert "FAIL:" in proc.stdout
        assert "STRUC_001" in proc.stdout

    def test_cli_json_output(self) -> None:
        spec_file = str(VALID_DIR / "marketplace_valid.json")
        cmd = [
            sys.executable,
            str(SCRIPTS_DIR / "validate_spec.py"),
            spec_file,
            "--json",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert proc.returncode == 0
        data = json.loads(proc.stdout)
        assert data["valid"] is True
        assert data["error_count"] == 0

    def test_cli_strict_flag_fails_on_warning(self) -> None:
        spec_file = str(BROKEN_DIR / "broken_REL_003.json")
        # Without --strict -> exit 0
        proc_normal = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "validate_spec.py"), spec_file],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc_normal.returncode == 0

        # With --strict -> exit 1
        proc_strict = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIR / "validate_spec.py"),
                spec_file,
                "--strict",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc_strict.returncode == 1
