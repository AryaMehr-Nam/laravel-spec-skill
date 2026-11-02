# Contributing to `laravel-spec-skill`

Thank you for contributing to `laravel-spec-skill`! We are building a rock-solid, machine-validated specification foundation for AI agents building Laravel and Filament applications.

---

## Code of Conduct & Principles

1. **Deterministic & Machine-Validated**: Everything we build must be verifiable. We favor explicit validation rules, reproducible tests, and zero-hallucination specifications over fuzzy instructions.
2. **Standard Library First**: Tooling scripts (`validate_spec.py`, `render_docs.py`, `render_commands.py`, `init_spec.py`, `install.py`) must run on Python 3.10+ standard library alone with **zero third-party dependencies**.
3. **Strict Quality Gates**: Every pull request must pass the full test suite (`pytest`) and linting (`ruff`) across Python 3.10 through 3.13.

---

## Development Setup

### 1. Prerequisites
- Python 3.10 or higher (Python 3.10, 3.11, 3.12, or 3.13)
- `git`

### 2. Fork & Clone Repository
```bash
git clone https://github.com/your-username/laravel-spec-skill.git
cd laravel-spec-skill
```

### 3. Virtual Environment & Dependencies
Create a virtual environment and install development dependencies in editable mode:

```bash
# Create virtual environment
python -m venv .venv

# Activate on Linux/macOS:
source .venv/bin/activate

# Activate on Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Install development dependencies (pytest, ruff)
pip install --upgrade pip
pip install -e ".[dev]"
```

### 4. Running Tests & Quality Checks
Before writing code or opening a PR, ensure all checks pass:

```bash
# Run full pytest suite
pytest -v

# Run linter
ruff check .

# Check code formatting
ruff format --check .
```

---

## How to Add New Validation Rules

The validation engine resides in [`skills/laravel-spec/scripts/validate_spec.py`](skills/laravel-spec/scripts/validate_spec.py).

### 1. Rule Identifier Conventions
Rule IDs follow the pattern `<CATEGORY>_<3-DIGIT-NUMBER>`:
- `STRUC_XXX`: Structural schema and root dictionary requirements.
- `UNIQ_XXX`: Identifier and table uniqueness.
- `REL_XXX`: Relational integrity and foreign keys.
- `AUTH_XXX`: Authorization matrix, policies, and roles.
- `SM_XXX`: State machine graphs and lifecycle transitions.
- `NUM_XXX`: Numerical and financial precision.
- `ENUM_XXX`: Enum value arrays and integrity.
- `DAG_XXX`: Milestone acyclic graph and task scope.
- `SEC_XXX`: Security, PII, uploads, and tenancy scoping.

When adding a new category, use a 3-4 letter uppercase prefix.

### 2. Implement the Rule in `validate_spec.py`
Add your check within `SpecValidator.validate()` or a dedicated helper method. Every rule violation emits a `RuleViolation`:

```python
self.violations.append(
    RuleViolation(
        rule_id="SEC_005",
        severity=Severity.ERROR,  # or Severity.WARNING
        message="Model 'Order' declares soft deletes but lacks deleted_at column definition",
        path="models.Order",
        fix_hint="Add a nullable timestamp field 'deleted_at' or remove soft delete declaration.",
    )
)
```

### 3. Document the Rule
Update [`skills/laravel-spec/references/validation-rules.md`](skills/laravel-spec/references/validation-rules.md):
- Add entry to the summary table.
- Add detailed section with Severity, Trigger condition, Example of violation, and Fix hint.

### 4. Add Automated Regression Tests
Every rule **must** have a corresponding test:
1. **Fixture-based (Recommended)**: Create a minimal JSON file in `tests/fixtures/broken/broken_<RULE_ID>.json`. The parameterized test in `tests/test_validator.py` (`test_broken_fixture_triggers_expected_rule`) will automatically discover and verify it!
2. **Direct Python API**: You can also add explicit unit tests using `SpecValidator` or `validate_spec`:

```python
def test_rule_sec_005_soft_delete_missing_field():
    spec = create_valid_spec_baseline()
    spec["models"][0]["soft_deletes"] = True
    # remove deleted_at if present
    result = SpecValidator(spec).validate()
    assert any(v.rule_id == "SEC_005" for v in result.violations)
```

---

## How to Author New Presets

Presets provide domain-specific architectural extensions (e.g. localized payments, specialized auth, multi-tenant patterns).

### 1. Create the Preset Guide
Create a new markdown file in `skills/laravel-spec/references/presets/<preset-name>.md`:
Follow this standardized structure:
```markdown
# Preset: <Preset Name> (`<preset-id>`)

## 1. Overview & Use Case
Explain why this preset exists and what architectural problem it solves.

## 2. Composer & Framework Dependencies
List exact packages with minimum version constraints (e.g., `spatie/laravel-permission:^6.0`).

## 3. Schema Extensions & Spec Fragment
Provide a concrete YAML/JSON fragment showing how `spec.json` models, fields, or integrations should be configured.

## 4. Architectural Guidelines & Best Practices
Provide concrete implementation guidance for Laravel and Filament (migrations, service providers, models, policies).

## 5. Security & Edge Case Checklist
Detail pitfalls (e.g. rate limits, replay attacks, isolation leaks, currency overflow).

## 6. Verification & Testing Strategy
List automated test scenarios (Pest/PHPUnit) required to verify the integration.
```

### 2. Update Documentation & Schemas
- Add the preset name to `skills/laravel-spec/schemas/spec.schema.json` under `project.presets.items.enum` (if schema validation is enforced).
- Update the Presets table in `README.md` and `skills/laravel-spec/SKILL.md`.
- Add test coverage in `tests/test_examples.py` ensuring the preset reference file exists and meets documentation standards.

---

## Pull Request Checklist

Before submitting your PR:
- [ ] Code follows PEP 8 and project style: `ruff check .` and `ruff format --check .` pass cleanly.
- [ ] Test suite is 100% green: `pytest` passes with zero failures.
- [ ] No third-party dependencies added to runtime scripts (`validate_spec.py`, `render_docs.py`, etc.).
- [ ] Documentation updated (`README.md`, `validation-rules.md`, or relevant preset).
- [ ] Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/):
  - `feat(...)`: New feature or preset
  - `fix(...)`: Bug fix or validation correction
  - `docs(...)`: Documentation improvements
  - `test(...)`: Test additions or hardening
  - `refactor(...)`: Code cleanup with no functional changes

Thank you for helping make specification-driven Laravel development robust and reliable!
