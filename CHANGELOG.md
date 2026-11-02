# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-11-02

### Added
- **Milestone 0**: Repository layout, `pyproject.toml`, standard developer tooling (`pytest`, `ruff`), and formal JSON Schema `skills/laravel-spec/schemas/spec.schema.json`.
- **Milestone 1**: Zero-dependency Python validation engine `skills/laravel-spec/scripts/validate_spec.py` with 29 granular rule IDs (including `ENUM_001` for enum field values), severity tiers (`error`, `warning`), actionable fix hints, and test suite covering valid specs and 26 broken fixtures.
- **Milestone 2**: Spec scaffolding and documentation renderers:
  - `skills/laravel-spec/scripts/init_spec.py`: Scaffold generator producing schema-compliant `spec.json` skeletons from template or CLI flags.
  - `skills/laravel-spec/scripts/render_docs.py`: Converts `spec.json` into 10 modular, strictly deterministic (byte-for-byte identical hash) markdown documents (`00-overview.md` through `09-open-questions.md`).
  - `skills/laravel-spec/scripts/render_commands.py`: Dependency-ordered generator for Artisan CLI scaffold commands (`make:model -mfsc`, `make:policy`, `make:filament-resource`, etc.) in dry-run mode (never executes).
  - `tests/test_renderers.py`: Determinism verification, hash identity across render passes, topological command ordering tests, and CLI execution tests.
- **Milestone 3**: Real-world architectural presets and production-grade specification examples:
  - Preset reference guides in `skills/laravel-spec/references/presets/`:
    - `rtl-fa.md`: Persian RTL layout for Filament, Jalali dates (`morilog/jalali`), Persian digit normalization, local Vazirmatn font with zero CDN dependencies.
    - `iran-payments.md`: Multi-gateway payment processing (Zarinpal, Shepa, Saman SEP), atomic callback verification, `idempotency_key` unique constraints, and Rial/Toman conversion handling.
    - `otp-login.md`: Passwordless SMS OTP authentication, tiered rate limiting, 120-second expiration, single-use cryptographic nonces, and user enumeration defense.
    - `multi-tenant.md`: Single-database row-level tenant scoping (`tenant_id`, native Filament panel tenancy) and multi-database isolation (`stancl/tenancy`).
  - Production reference examples with full deterministic artifacts:
    - `examples/marketplace/`: Valid multi-vendor e-commerce marketplace (`spec.json`, 10 rendered markdown docs, `commands.sh`, `validation.txt`).
    - `examples/crm/`: Valid enterprise CRM (`spec.json`, 10 rendered markdown docs, `commands.sh`, `validation.txt`).
  - `tests/test_examples.py`: Comprehensive test suite verifying strict validation, deterministic doc and command generation, and preset documentation completeness.
- **Milestone 4**: Canonical Agent Skill and deep architectural reference guides:
  - `skills/laravel-spec/SKILL.md`: Vendor-neutral specification skill (246 lines, strictly under 500 lines) detailing the 5 operational phases (Discovery with batched questionnaire <= 7 questions & workspace inference, Spec generation, Machine validation loop, Review gate <= 15 lines, and Resumable TDD build protocol).
  - Deep reference guides in `skills/laravel-spec/references/`:
    - `spec-format.md`: Complete JSON specification schema documentation and field reference.
    - `validation-rules.md`: Complete catalog of all 29 validation rules (`STRUC`, `UNIQ`, `REL`, `AUTH`, `SM`, `NUM`, `ENUM`, `DAG`, `SEC`) with severities, trigger conditions, examples, and fix hints.
    - `filament-notes.md`: Filament v3/v4 panel providers, resources, form/table schemas, relation managers, policies, and ownership query scoping.
    - `build-protocol.md`: Step-by-step TDD build protocol, milestone lifecycle, Red-Green-Refactor, Pint/Larastan QA, and `spec/PROGRESS.md` checkpoint format.
- **Milestone 5**: Multi-agent installer, root CLI forwarding entrypoints, and packaging test suite:
  - `scripts/install.py`: Standalone, zero-dependency CLI installer supporting Claude Code, Cursor, OpenAI Codex CLI, and Antigravity across project-local and user-global targets with non-destructive pointer block injection (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`), data loss defense on corrupted manifests, and clean rollback via `--uninstall`.
  - Root CLI forwarding scripts: `scripts/validate_spec.py`, `scripts/render_docs.py`, `scripts/render_commands.py`, and `scripts/init_spec.py` for direct CLI execution from repository root.
  - `tests/test_installer.py`: 27 automated tests verifying multi-agent targets, idempotent re-installation, non-destructive pointer block injection and clean removal, pre-existing directory backup and restore, corrupted manifest protection, middle pointer removal, and CLI subprocess execution.
- **Milestone 6**: Documentation, Quality Assurance, and Release Polish:
  - Comprehensive `README.md` containing first-screen pitch, 10-second demo script with exact shell commands to record it, quickstart installation (at most 2 commands via `npx skills add` and `python scripts/install.py`), manual copy documentation, cross-agent compatibility matrix with honesty rule (Antigravity = verified; Claude Code, Cursor, Codex = experimental), 5-phase workflow explanation, 29 validation rules overview, architectural presets guide (`rtl-fa`, `iran-payments`, `otp-login`, `multi-tenant`), honest limitations and roadmap, and preset contribution guide.
  - Comprehensive `CONTRIBUTING.md` developer guide covering virtual environment setup, `pytest` and `ruff` commands, step-by-step instructions for implementing new validation rule IDs and updating reference documentation/fixtures, guide for authoring new presets, and PR checklist.
  - Continuous Integration workflow `.github/workflows/ci.yml` matrix testing across Python 3.10, 3.11, 3.12, and 3.13 on `ubuntu-latest` with ruff linting and pytest test execution.
  - GitHub issue templates `.github/ISSUE_TEMPLATE/bug_report.md` and `.github/ISSUE_TEMPLATE/preset_request.md`.
  - Launch announcement drafts in `docs/launch/`: `reddit-claudeai.md`, `reddit-laravel.md`, and `show-hn.md`.
  - Formal release tag `v0.1.0`.

[Unreleased]: https://github.com/AryaMehr-Nam/laravel-spec-skill/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/AryaMehr-Nam/laravel-spec-skill/releases/tag/v0.1.0
