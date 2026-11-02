"""Tests for Laravel Filament specification validator."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Ensure skills/laravel-spec/scripts is on sys.path
SCRIPTS_DIR = Path(__file__).resolve().parent.parent / "skills" / "laravel-spec" / "scripts"
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

    def test_none_spec_handled_gracefully(self) -> None:
        result = validate_spec(None)
        assert result.is_valid is False
        assert any(v.rule_id == "STRUC_001" for v in result.errors)
        assert any("must be a JSON object" in v.message for v in result.errors)

    def test_non_dict_spec_handled_gracefully(self) -> None:
        result = validate_spec("this is a string, not a dict")
        assert result.is_valid is False
        assert any(v.rule_id == "STRUC_001" for v in result.errors)

    def test_null_top_level_collections(self) -> None:
        raw_spec = {
            "project": {
                "name": "App",
                "description": "Desc",
                "locale": "en",
                "timezone": "UTC",
                "laravel_version": "12",
                "filament_version": "v3",
            },
            "roles": None,
            "models": None,
            "policies": None,
            "filament": {"panels": None},
            "milestones": None,
        }
        result = validate_spec(raw_spec)
        assert result.is_valid is False
        assert any(v.rule_id == "STRUC_001" for v in result.errors)

    def test_nested_none_collections_handled_safely(self) -> None:
        raw_spec = {
            "project": {
                "name": "App",
                "description": "Desc",
                "locale": "en",
                "timezone": "UTC",
                "laravel_version": "12",
                "filament_version": "v3",
            },
            "roles": [{"name": "super-admin", "is_super_admin": True}],
            "models": [
                {
                    "name": "TestModel",
                    "table": "test_models",
                    "fields": None,
                    "relations": None,
                    "states": None,
                }
            ],
            "policies": [],
            "filament": {"panels": []},
            "milestones": [
                {
                    "id": "M0",
                    "title": "Init",
                    "depends_on": [],
                    "scope": ["TestModel"],
                    "acceptance": ["Acc 1", "Acc 2"],
                }
            ],
        }
        result = validate_spec(raw_spec)
        assert isinstance(result, ValidationResult)

    def test_sec_004_path_format(self) -> None:
        path = BROKEN_DIR / "broken_SEC_004.json"
        result = validate_spec_file(path)
        assert result.is_valid is False
        sec_004_violations = [v for v in result.violations if v.rule_id == "SEC_004"]
        assert len(sec_004_violations) > 0
        # Ensure path contains exact panel index format
        assert sec_004_violations[0].path == "filament.panels[0].resources[0].table"

    def test_polymorphic_morphto_wildcard_valid(self) -> None:
        raw_spec = {
            "project": {
                "name": "Polymorphic App",
                "description": "App with morphTo relations",
                "locale": "en",
                "timezone": "UTC",
                "laravel_version": "12",
                "filament_version": "v3",
            },
            "roles": [{"name": "super-admin", "is_super_admin": True}],
            "models": [
                {
                    "name": "Comment",
                    "table": "comments",
                    "fields": [{"name": "id", "type": "bigInteger"}],
                    "relations": [{"name": "commentable", "type": "morphTo", "model": "*"}],
                }
            ],
            "policies": [
                {
                    "model": "Comment",
                    "ownership": "none",
                    "abilities": {
                        "viewAny": ["super-admin"],
                        "view": ["super-admin"],
                        "create": ["super-admin"],
                        "update": ["super-admin"],
                        "delete": ["super-admin"],
                    },
                }
            ],
            "filament": {"panels": []},
            "milestones": [
                {
                    "id": "M0",
                    "title": "Comments",
                    "depends_on": [],
                    "scope": ["Comment"],
                    "acceptance": ["Acc 1", "Acc 2"],
                }
            ],
        }
        result = validate_spec(raw_spec)
        assert result.is_valid is True
        assert result.error_count == 0

    def test_bidirectional_intermediate_loop_with_terminal_state_passes(self) -> None:
        raw_spec = {
            "project": {
                "name": "State Loop App",
                "description": "State machine with bidirectional loop reaching terminal state",
                "locale": "en",
                "timezone": "UTC",
                "laravel_version": "12",
                "filament_version": "v3",
            },
            "roles": [{"name": "super-admin", "is_super_admin": True}],
            "models": [
                {
                    "name": "Ticket",
                    "table": "tickets",
                    "fields": [
                        {"name": "id", "type": "bigInteger"},
                        {"name": "status", "type": "string"},
                    ],
                    "states": {
                        "field": "status",
                        "initial": "open",
                        "final": ["resolved"],
                        "transitions": [
                            {"from": "open", "to": "in_progress", "roles": ["super-admin"]},
                            {"from": "in_progress", "to": "review", "roles": ["super-admin"]},
                            {"from": "review", "to": "in_progress", "roles": ["super-admin"]},
                            {"from": "review", "to": "resolved", "roles": ["super-admin"]},
                        ],
                    },
                }
            ],
            "policies": [],
            "filament": {"panels": []},
            "milestones": [
                {
                    "id": "M0",
                    "title": "Tickets",
                    "depends_on": [],
                    "scope": ["Ticket"],
                    "acceptance": ["Acc 1", "Acc 2"],
                }
            ],
        }
        result = validate_spec(raw_spec)
        # Should NOT trigger SM_004 because both in_progress and review reach resolved
        assert not any(v.rule_id == "SM_004" for v in result.violations)

    def test_decimal_scale_exceeding_precision_triggers_num_001(self) -> None:
        raw_spec = {
            "project": {
                "name": "Decimal Bound App",
                "description": "App testing decimal scale > precision",
                "locale": "en",
                "timezone": "UTC",
                "laravel_version": "12",
                "filament_version": "v3",
            },
            "roles": [{"name": "super-admin", "is_super_admin": True}],
            "models": [
                {
                    "name": "Item",
                    "table": "items",
                    "fields": [
                        {"name": "id", "type": "bigInteger"},
                        {
                            "name": "price",
                            "type": "decimal",
                            "precision": 2,
                            "scale": 4,
                        },
                    ],
                }
            ],
            "policies": [],
            "filament": {"panels": []},
            "milestones": [
                {
                    "id": "M0",
                    "title": "Items",
                    "depends_on": [],
                    "scope": ["Item"],
                    "acceptance": ["Acc 1", "Acc 2"],
                }
            ],
        }
        result = validate_spec(raw_spec)
        assert result.is_valid is False
        assert any(
            v.rule_id == "NUM_001" and "scale >= 0, scale <= precision" in v.message
            for v in result.errors
        )

    def test_multi_cluster_dag_cycle_detection(self) -> None:
        raw_spec = {
            "project": {
                "name": "Multi Cluster App",
                "description": "App with disconnected milestone clusters and cycles",
                "locale": "en",
                "timezone": "UTC",
                "laravel_version": "12",
                "filament_version": "v3",
            },
            "roles": [{"name": "super-admin", "is_super_admin": True}],
            "models": [],
            "policies": [],
            "filament": {"panels": []},
            "milestones": [
                # Cluster 1: Valid chain
                {
                    "id": "M0",
                    "title": "Base",
                    "depends_on": [],
                    "scope": [],
                    "acceptance": ["A1", "A2"],
                },
                {
                    "id": "M1",
                    "title": "Feat1",
                    "depends_on": ["M0"],
                    "scope": [],
                    "acceptance": ["A1", "A2"],
                },
                # Cluster 2: Disconnected cycle M2 <-> M3
                {
                    "id": "M2",
                    "title": "Cycle1",
                    "depends_on": ["M3"],
                    "scope": [],
                    "acceptance": ["A1", "A2"],
                },
                {
                    "id": "M3",
                    "title": "Cycle2",
                    "depends_on": ["M2"],
                    "scope": [],
                    "acceptance": ["A1", "A2"],
                },
                # Cluster 3: Standalone valid
                {
                    "id": "M4",
                    "title": "Independent",
                    "depends_on": [],
                    "scope": [],
                    "acceptance": ["A1", "A2"],
                },
            ],
        }
        result = validate_spec(raw_spec)
        assert result.is_valid is False
        dag_violations = [v for v in result.errors if v.rule_id == "DAG_001"]
        assert len(dag_violations) == 1
        assert "M2" in dag_violations[0].message
        assert "M3" in dag_violations[0].message
        assert "M0" not in dag_violations[0].message
        assert "M1" not in dag_violations[0].message
        assert "M4" not in dag_violations[0].message

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


class TestEnumValidation:
    """Tests verifying ENUM_001 validation rules."""

    def _base_spec(self, field_def: dict) -> dict:
        return {
            "project": {
                "name": "Enum Test",
                "description": "Testing enum fields",
                "locale": "en",
                "timezone": "UTC",
                "laravel_version": "12",
                "filament_version": "v3",
            },
            "roles": [{"name": "super-admin", "is_super_admin": True}],
            "models": [
                {
                    "name": "Post",
                    "table": "posts",
                    "fields": [{"name": "id", "type": "bigInteger"}, field_def],
                    "relations": [],
                }
            ],
            "policies": [],
            "filament": {"panels": []},
            "milestones": [
                {
                    "id": "M0",
                    "title": "Init",
                    "depends_on": [],
                    "scope": ["Post"],
                    "acceptance": ["Post model created", "Enum status field supported"],
                }
            ],
        }

    def test_missing_enum_values_fails(self) -> None:
        spec = self._base_spec({"name": "status", "type": "enum"})
        res = validate_spec(spec)
        assert res.is_valid is False
        assert any(v.rule_id == "ENUM_001" for v in res.errors)

    def test_empty_enum_values_fails(self) -> None:
        spec = self._base_spec({"name": "status", "type": "enum", "enum_values": []})
        res = validate_spec(spec)
        assert res.is_valid is False
        assert any(v.rule_id == "ENUM_001" for v in res.errors)

    def test_non_string_enum_values_fails(self) -> None:
        spec = self._base_spec({"name": "status", "type": "enum", "enum_values": [1, 2]})
        res = validate_spec(spec)
        assert res.is_valid is False
        assert any(v.rule_id == "ENUM_001" for v in res.errors)

    def test_blank_string_enum_values_fails(self) -> None:
        spec = self._base_spec({"name": "status", "type": "enum", "enum_values": ["   "]})
        res = validate_spec(spec)
        assert res.is_valid is False
        assert any(v.rule_id == "ENUM_001" for v in res.errors)

    def test_duplicate_enum_values_fails(self) -> None:
        spec = self._base_spec(
            {"name": "status", "type": "enum", "enum_values": ["draft", "draft"]}
        )
        res = validate_spec(spec)
        assert res.is_valid is False
        assert any(v.rule_id == "ENUM_001" for v in res.errors)

    def test_valid_enum_values_passes(self) -> None:
        spec = self._base_spec(
            {"name": "status", "type": "enum", "enum_values": ["draft", "published"]}
        )
        res = validate_spec(spec)
        assert res.is_valid is True
        assert not any(v.rule_id == "ENUM_001" for v in res.violations)


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
