# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
