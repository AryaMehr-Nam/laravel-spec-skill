# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Milestone 0**: Repository layout, `pyproject.toml`, standard developer tooling (`pytest`, `ruff`), and formal JSON Schema `skills/laravel-spec/schemas/spec.schema.json`.
- **Milestone 1**: Zero-dependency Python validation engine `skills/laravel-spec/scripts/validate_spec.py` with 27 granular rule IDs, severity tiers (`error`, `warning`), actionable fix hints, and test suite covering valid specs and 25+ broken fixtures.
