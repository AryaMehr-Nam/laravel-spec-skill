"""Tests for specification initialization, documentation, and commands."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# Ensure skills/laravel-spec/scripts is on sys.path
SCRIPTS_DIR = (
    Path(__file__).resolve().parent.parent / "skills" / "laravel-spec" / "scripts"
)
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from init_spec import (  # noqa: E402
    get_default_skeleton,
    init_spec,
    write_spec,
)
from render_commands import (  # noqa: E402
    generate_artisan_commands,
    render_commands,
    sort_models_by_dependency,
)
from render_docs import (  # noqa: E402
    DOC_FILENAMES,
    render_docs,
    render_docs_from_file,
    write_docs,
)
from validate_spec import validate_spec  # noqa: E402

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
VALID_DIR = FIXTURES_DIR / "valid"


def load_fixture(name: str) -> dict[str, Any]:
    with open(VALID_DIR / name, encoding="utf-8") as f:
        return json.load(f)


class TestInitSpec:
    """Tests for init_spec module."""

    def test_default_init_passes_validator(self) -> None:
        spec = init_spec()
        assert spec["project"]["name"] == "Laravel Application"
        assert spec["project"]["laravel_version"] == "12"
        assert spec["project"]["filament_version"] == "v3"
        result = validate_spec(spec, strict=True)
        assert result.is_valid is True, f"Validation failed: {result.violations}"

    def test_custom_arguments_applied(self) -> None:
        spec = init_spec(
            name="Custom CRM",
            description="Enterprise CRM portal",
            locale="fa",
            timezone="Asia/Tehran",
            laravel_version="13",
            filament_version="v4",
            presets=["rtl-fa", "iran-payments"],
        )
        assert spec["project"]["name"] == "Custom CRM"
        assert spec["project"]["locale"] == "fa"
        assert spec["project"]["timezone"] == "Asia/Tehran"
        assert spec["project"]["laravel_version"] == "13"
        assert spec["project"]["filament_version"] == "v4"
        assert spec["project"]["presets"] == ["rtl-fa", "iran-payments"]

        result = validate_spec(spec, strict=True)
        assert result.is_valid is True

    def test_fallback_skeleton_when_no_template(self) -> None:
        skeleton = get_default_skeleton(name="Fallback App")
        assert skeleton["project"]["name"] == "Fallback App"
        assert len(skeleton["roles"]) == 1
        assert skeleton["roles"][0]["is_super_admin"] is True
        result = validate_spec(skeleton, strict=True)
        assert result.is_valid is True

    def test_write_spec_file_and_force_flag(self, tmp_path: Path) -> None:
        spec = init_spec(name="Disk Test App")
        out_file = tmp_path / "spec" / "spec.json"

        # First write succeeds
        written = write_spec(spec, out_file)
        assert written.is_file()
        assert written == out_file

        # Reading back matches
        with open(written, encoding="utf-8") as f:
            loaded = json.load(f)
        assert loaded["project"]["name"] == "Disk Test App"

        # Overwrite without force raises FileExistsError
        import pytest

        with pytest.raises(FileExistsError):
            write_spec(spec, out_file, force=False)

        # Overwrite with force succeeds
        spec["project"]["name"] = "Overwritten App"
        write_spec(spec, out_file, force=True)
        with open(written, encoding="utf-8") as f:
            updated = json.load(f)
        assert updated["project"]["name"] == "Overwritten App"

    def test_cli_print_only(self) -> None:
        cmd = [
            sys.executable,
            str(SCRIPTS_DIR / "init_spec.py"),
            "--name",
            "CLI App",
            "--print",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert proc.returncode == 0
        data = json.loads(proc.stdout)
        assert data["project"]["name"] == "CLI App"

    def test_cli_write_file(self, tmp_path: Path) -> None:
        out_file = tmp_path / "cli_spec.json"
        cmd = [
            sys.executable,
            str(SCRIPTS_DIR / "init_spec.py"),
            "--name",
            "CLI File App",
            "-o",
            str(out_file),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert proc.returncode == 0
        assert out_file.is_file()
        data = json.loads(out_file.read_text(encoding="utf-8"))
        assert data["project"]["name"] == "CLI File App"


class TestRenderDocs:
    """Tests for render_docs deterministic markdown generation."""

    def test_all_10_files_rendered(self) -> None:
        spec = load_fixture("marketplace_valid.json")
        docs = render_docs(spec)
        assert len(docs) == 10
        for name in DOC_FILENAMES:
            assert name in docs
            assert isinstance(docs[name], str)
            assert len(docs[name]) > 50

    def test_byte_for_byte_determinism_across_passes(self) -> None:
        spec = load_fixture("marketplace_valid.json")

        initial_hashes: dict[str, str] = {}
        first_pass = render_docs(spec)
        for name, content in first_pass.items():
            initial_hashes[name] = hashlib.sha256(content.encode("utf-8")).hexdigest()

        # Repeat rendering 5 times and assert SHA-256 match
        for _ in range(5):
            repeated = render_docs(spec)
            for name, content in repeated.items():
                curr_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
                assert curr_hash == initial_hashes[name], (
                    f"Non-deterministic output detected in {name}!"
                )

    def test_minimal_spec_renders_cleanly(self) -> None:
        spec = load_fixture("minimal_valid.json")
        docs = render_docs(spec)
        assert len(docs) == 10
        # Check overview metadata
        assert "Minimal Spec" in docs["00-overview.md"]
        assert "Total Models" in docs["00-overview.md"] or "Domain Models" in docs["00-overview.md"]
        # Check database
        assert "Database Schema" in docs["02-database.md"]
        # Check build plan
        assert "M0" in docs["08-build-plan.md"]

    def test_marketplace_spec_contents(self) -> None:
        spec = load_fixture("marketplace_valid.json")
        docs = render_docs(spec)

        # Overview
        assert "Marketplace Pro" in docs["00-overview.md"]
        # Modules
        assert "Product Module" in docs["01-modules.md"]
        assert "Order Module" in docs["01-modules.md"]
        # Database
        db_doc = docs["02-database.md"].lower()
        assert "decimal(12, 2)" in db_doc or "decimal" in db_doc
        assert "belongsTo" in docs["02-database.md"]
        # Roles and policies
        assert "super-admin" in docs["03-roles-permissions.md"]
        assert "`Product` Policy" in docs["03-roles-permissions.md"]
        assert "owner_field:vendor_id" in docs["03-roles-permissions.md"]
        # Filament
        assert "ProductResource" in docs["04-filament.md"]
        assert "scopedToVendor" in docs["04-filament.md"]
        # Workflows
        assert "`Order` Workflow" in docs["05-workflows.md"]
        assert "pending" in docs["05-workflows.md"]
        assert "completed" in docs["05-workflows.md"]
        # Integrations
        assert "activity_log" in docs["06-integrations.md"]
        # Security
        assert "PII" in docs["07-security.md"]
        assert "cover_image" in docs["07-security.md"]
        # Build plan
        assert "M0" in docs["08-build-plan.md"]
        assert "M1" in docs["08-build-plan.md"]
        assert "M2" in docs["08-build-plan.md"]

    def test_write_docs_creates_expected_files(self, tmp_path: Path) -> None:
        spec = load_fixture("marketplace_valid.json")
        docs = render_docs(spec)
        out_dir = tmp_path / "docs" / "spec"
        written = write_docs(docs, out_dir)
        assert len(written) == 10
        for p in written:
            assert p.is_file()
            # Verify LF line endings
            content_bytes = p.read_bytes()
            assert b"\r\n" not in content_bytes

    def test_render_docs_from_file_api(self, tmp_path: Path) -> None:
        spec_path = VALID_DIR / "marketplace_valid.json"
        out_dir = tmp_path / "rendered"
        written = render_docs_from_file(spec_path, out_dir)
        assert len(written) == 10
        assert (out_dir / "00-overview.md").exists()

    def test_cli_render_docs_stdout(self) -> None:
        spec_path = str(VALID_DIR / "minimal_valid.json")
        cmd = [
            sys.executable,
            str(SCRIPTS_DIR / "render_docs.py"),
            spec_path,
            "--stdout",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert proc.returncode == 0
        assert "<!-- BEGIN: 00-overview.md -->" in proc.stdout
        assert "<!-- END: 09-open-questions.md -->" in proc.stdout


class TestRenderCommands:
    """Tests for render_commands artisan CLI generation."""

    def test_command_ordering_respects_dependencies(self) -> None:
        spec = load_fixture("marketplace_valid.json")
        commands = generate_artisan_commands(spec)

        # Find indexes of make:model commands
        user_idx = -1
        product_idx = -1
        order_idx = -1

        for idx, cmd in enumerate(commands):
            if "make:model User" in cmd:
                user_idx = idx
            elif "make:model Product" in cmd:
                product_idx = idx
            elif "make:model Order" in cmd:
                order_idx = idx

        # User is parent to Product (vendor_id) and Order (customer_id)
        assert user_idx != -1
        assert product_idx != -1
        assert order_idx != -1
        assert user_idx < product_idx, "User model must be generated before Product!"
        assert user_idx < order_idx, "User model must be generated before Order!"

    def test_model_commands_use_flags(self) -> None:
        spec = load_fixture("marketplace_valid.json")
        commands = generate_artisan_commands(spec)
        model_cmds = [c for c in commands if "make:model" in c]
        assert len(model_cmds) == 3
        for c in model_cmds:
            assert "-mfsc" in c

    def test_policies_and_resources_generated(self) -> None:
        spec = load_fixture("marketplace_valid.json")
        commands = generate_artisan_commands(spec)

        policy_cmds = [c for c in commands if "make:policy" in c]
        assert len(policy_cmds) == 3
        assert any("UserPolicy --model=User" in c for c in policy_cmds)
        assert any("ProductPolicy --model=Product" in c for c in policy_cmds)
        assert any("OrderPolicy --model=Order" in c for c in policy_cmds)

        resource_cmds = [c for c in commands if "make:filament-resource" in c]
        assert len(resource_cmds) == 3
        assert any("User" in c for c in resource_cmds)
        assert any("Product" in c for c in resource_cmds)
        assert any("Order" in c for c in resource_cmds)

    def test_models_precede_policies_and_resources(self) -> None:
        spec = load_fixture("marketplace_valid.json")
        commands = generate_artisan_commands(spec)

        last_model_idx = max(i for i, c in enumerate(commands) if "make:model" in c)
        first_policy_idx = min(i for i, c in enumerate(commands) if "make:policy" in c)
        first_resource_idx = min(i for i, c in enumerate(commands) if "make:filament-resource" in c)

        assert last_model_idx < first_policy_idx
        assert last_model_idx < first_resource_idx

    def test_sort_models_by_dependency_handles_cycle(self) -> None:
        # A references B and B references A
        cyclic_models = [
            {
                "name": "Alpha",
                "fields": [{"name": "beta_id", "foreign": {"model": "Beta"}}],
            },
            {
                "name": "Beta",
                "fields": [{"name": "alpha_id", "foreign": {"model": "Alpha"}}],
            },
        ]
        sorted_models = sort_models_by_dependency(cyclic_models)
        assert len(sorted_models) == 2
        names = [m["name"] for m in sorted_models]
        assert "Alpha" in names
        assert "Beta" in names

    def test_render_formats(self) -> None:
        spec = load_fixture("marketplace_valid.json")

        # Shell format
        sh_out = render_commands(spec, format_type="shell")
        assert "#!/usr/bin/env bash" in sh_out
        assert "set -euo pipefail" in sh_out
        assert "php artisan make:model" in sh_out

        # List format
        list_out = render_commands(spec, format_type="list")
        lines = [line.strip() for line in list_out.strip().splitlines() if line.strip()]
        for line in lines:
            assert line.startswith("php artisan ")

        # JSON format
        json_out = render_commands(spec, format_type="json")
        arr = json.loads(json_out)
        assert isinstance(arr, list)
        assert all(isinstance(cmd, str) and cmd.startswith("php artisan ") for cmd in arr)

    def test_cli_render_commands(self) -> None:
        spec_path = str(VALID_DIR / "marketplace_valid.json")
        cmd = [
            sys.executable,
            str(SCRIPTS_DIR / "render_commands.py"),
            spec_path,
            "--format",
            "list",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        assert proc.returncode == 0
        assert "php artisan make:model User -mfsc" in proc.stdout
        assert "php artisan make:filament-resource Product" in proc.stdout

    def test_render_commands_with_enum_and_custom_panel(self) -> None:
        spec = {
            "project": {"name": "Enum App"},
            "models": [
                {
                    "name": "Article",
                    "fields": [
                        {"name": "id", "type": "bigInteger"},
                        {
                            "name": "status",
                            "type": "enum",
                            "enum_values": ["draft", "published"],
                        },
                    ],
                }
            ],
            "filament": {
                "panels": [
                    {
                        "id": "author",
                        "path": "author",
                        "resources": [{"model": "Article"}],
                    }
                ]
            },
        }
        cmds = generate_artisan_commands(spec)
        assert "php artisan make:filament-panel author" in cmds
        assert "php artisan make:enum ArticleStatusEnum" in cmds
        assert "php artisan make:model Article -mfsc" in cmds
        assert "php artisan make:filament-resource Article --panel=author" in cmds

    def test_render_docs_and_commands_empty_spec(self) -> None:
        empty_spec: dict[str, Any] = {"project": {"name": "Empty"}}
        docs = render_docs(empty_spec)
        assert len(docs) == 10
        cmds = generate_artisan_commands(empty_spec)
        assert cmds == []
