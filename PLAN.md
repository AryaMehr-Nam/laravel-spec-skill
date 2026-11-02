# PLAN: laravel-spec-skill

## Overview
`laravel-spec-skill` is an open-source, multi-agent skill that transforms a plain-language project description into a complete, internally consistent, machine-validated specification (`spec/spec.json` and rendered markdown files) for a Laravel + Filament application, then orchestrates a verified, test-driven build one milestone at a time.

---

## Architectural Principles & Differentiators
1. **Single Source of Truth**: `spec/spec.json` is the sole canonical source. All markdown files (`00-overview.md` through `09-open-questions.md`) are generated deterministically and never edited manually.
2. **Exhaustive Machine Validation**: Built-in Python rule engine (zero runtime dependencies, standard library only) validating relational integrity, authorization matrix completeness, state machine reachability, currency precision, milestone DAG acyclicity, PII/audit logging, and file upload safety.
3. **Laravel & Filament Native**: Adheres to modern Laravel (v11/v12/v13) and Filament (v3/v4) architecture (Panels, Resources, Pages, Relation Managers, Widgets, Actions, Filters, Eloquent Policies, Migrations).
4. **Resumable Build Protocol**: Milestone execution tracked via `spec/PROGRESS.md` with explicit acceptance criteria, enabling any session or agent to resume seamlessly.
5. **Multi-Agent Portability**: Works out-of-the-box across **Antigravity**, **Claude Code**, **Cursor**, and **OpenAI Codex CLI** with a dedicated reversible installer.
6. **Curated Presets**: Modular extensions for Persian RTL (`rtl-fa`), Iranian payment gateways (`iran-payments`), SMS OTP authentication (`otp-login`), and multi-tenancy (`multi-tenant`).

---

## Milestones

### Milestone 0: Project Setup & Specification Schema
- **Scope**:
  - Initialize repository layout (`skill/`, `examples/`, `tests/`, `scripts/`, `schemas/`).
  - Configure developer tooling: `pyproject.toml`, `.gitignore`, `ruff`, `pytest`.
  - Author formal JSON Schema: `skill/laravel-spec/schemas/spec.schema.json` reflecting the complete data model (project, roles, models, fields, relations, states, policies, filament panels/resources, integrations, milestones).
- **Verification**: `ruff check` clean, JSON schema validated.

### Milestone 1: Validation Engine & Rule Suite
- **Scope**:
  - Implement `skill/laravel-spec/scripts/validate_spec.py` using Python 3.10+ standard library only.
  - Implement rule engine with rule IDs (e.g., `REL_001`, `AUTH_001`, `SM_001`, `NUM_001`, `DAG_001`, `SEC_001`), severities (`error`, `warning`), and actionable fix hints.
  - Support validation rules:
    - Target relation existence & foreign key index checks.
    - Policy binding for every Filament resource & valid declared role references.
    - Super-admin role path & unreferenced role detection.
    - State machine transition validity (dead-end and unreachable state detection).
    - Float currency prohibition (enforcing integer minor units or decimal with scale).
    - Milestone acyclic DAG verification (Kahn's algorithm) & model coverage.
    - Ownership scoping & Filament query scope declarations.
    - Upload field constraints (max size, allowed mimes).
    - PII flagging with audit log declarations.
    - Name uniqueness across entities.
  - Author test suite: valid baseline specs pass; minimum 25 deliberately broken fixture specs each triggering exact expected rule ID.
- **Verification**: `pytest tests/test_validator.py` 100% green.

### Milestone 2: Spec Generators & Command Renderer
- **Scope**:
  - Implement `skill/laravel-spec/scripts/init_spec.py`: interactive or scaffold generator for empty project templates.
  - Implement `skill/laravel-spec/scripts/render_docs.py`: converts `spec.json` into modular markdown documentation (`00-overview.md` to `09-open-questions.md`). Guarantee byte-for-byte deterministic rendering.
  - Implement `skill/laravel-spec/scripts/render_commands.py`: generates ordered Artisan CLI commands (`make:model -mfsc`, `make:policy`, `make:filament-resource`, etc.) for dry-run inspection without direct execution.
  - Author determinism and generator tests.
- **Verification**: `pytest tests/test_renderers.py` green; verify hash identity across multiple render passes.

### Milestone 3: Real-World Examples & Presets
- **Scope**:
  - Author presets with schema fragments and architectural guidance in `skill/laravel-spec/references/presets/`:
    - `rtl-fa.md`: Persian RTL, Jalali dates (Morilog/jalali), local fonts, zero CDN deps.
    - `iran-payments.md`: Zarinpal/Pay.ir/Saman callbacks, idempotency tokens, Rial/Toman normalization.
    - `otp-login.md`: SMS verification, rate limits, expiry, single-use nonce, enumeration protection.
    - `multi-tenant.md`: Single-database / multi-database tenant scoping, Stancl/tenancy integration.
  - Author two production-grade examples:
    - `examples/marketplace/`: Multi-vendor e-commerce with orders, escrows, Filament vendor/admin panels.
    - `examples/crm/`: Customer relationship management with lead states, activities, and audit trails.
  - Ensure all examples pass `validate_spec.py` cleanly and contain pre-rendered markdown & artisan command outputs.
- **Verification**: `pytest tests/test_examples.py` passes validation on all examples.

### Milestone 4: Canonical Agent Skill & Reference Guides
- **Scope**:
  - Author `skill/laravel-spec/SKILL.md` (strictly under 500 lines, adhering to open Agent Skills specification with standard `name` and `description` frontmatter).
  - Structure 5 operational phases in `SKILL.md`:
    - Phase 1: Discovery (batched questionnaire, existing repo inference).
    - Phase 2: Spec generation (`spec.json` + rendered markdown).
    - Phase 3: Machine validation (`validate_spec.py`).
    - Phase 4: User review gate (<= 15-line summary).
    - Phase 5: Resumable TDD build protocol.
  - Author deep reference documents in `skill/laravel-spec/references/`:
    - `spec-format.md`: JSON schema field reference.
    - `validation-rules.md`: Complete rule catalog and resolution strategies.
    - `filament-notes.md`: Filament v3/v4 panel, resource, widget, and action best practices.
    - `build-protocol.md`: Detailed instructions for agent execution and progress checkpoints.
- **Verification**: SKILL.md line count check (< 500 lines), link checks to references.

### Milestone 5: Multi-Agent Installer & Packaging
- **Scope**:
  - Implement `scripts/install.py` / CLI entrypoint supporting:
    - Target agents: `antigravity`, `claude`, `cursor`, `codex`, `all`.
    - Modes: `--project` (local workspace) and `--global` (user home directory).
    - Reversible `uninstall` restoring original configuration.
    - Non-destructive append/cleanup of instruction pointers in `GEMINI.md`, `CLAUDE.md`, and `AGENTS.md`.
  - Maintain repository layout compatible with `npx skills add` (`skills/laravel-spec`).
  - Unit tests for installer in isolated temporary directories.
- **Verification**: `pytest tests/test_installer.py` verifying installation, pointer injection, and idempotent rollback across all targets.

### Milestone 6: Documentation, Quality Assurance & Release
- **Scope**:
  - Comprehensive `README.md` containing:
    - Pitch, recorded 10-second demo script, quickstart in <= 2 commands (`npx skills add` and `python scripts/install.py`).
    - Multi-agent compatibility matrix (Verified vs. Experimental).
    - Core differentiators vs. generic planning skills.
    - Presets guide and roadmap.
  - Project governance: `LICENSE` (MIT), `CHANGELOG.md`, `CONTRIBUTING.md`, `.github/workflows/ci.yml` (ruff + pytest across Python 3.10, 3.11, 3.12, 3.13).
  - Draft launch announcements for r/ClaudeAI, r/laravel, and Show HN.
  - Tag release `v0.1.0`.
- **Verification**: Full CI pipeline passes locally (pytest, ruff); git tag v0.1.0 ready.
