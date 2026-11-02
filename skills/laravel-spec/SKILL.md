---
name: laravel-spec
description: Transform a plain-language project description into a complete, machine-validated specification for a Laravel + Filament application, then orchestrate a test-driven build.
---

# Laravel Spec Skill

Transform plain-language software requirements into a complete, internally consistent, machine-validated specification (`spec/spec.json` and 10 modular markdown documents) for a Laravel and Filament application, then orchestrate a verified test-driven build one milestone at a time.

---

## Operating Principles

1. **Single Source of Truth**: `spec/spec.json` is the sole canonical source. Markdown documentation (`spec/00-overview.md` through `spec/09-open-questions.md`) and CLI scaffolding commands (`spec/commands.sh`) are generated deterministically and never edited manually.
2. **Exhaustive Machine Validation**: The Python rule engine (`scripts/validate_spec.py`) enforces 29 structural, relational, authorization, state machine, financial precision, milestone DAG, and security rules before any application code is written.
3. **Laravel & Filament Native**: Adheres to modern Laravel (v11/v12/v13) and Filament (v3/v4) architecture: Panel Providers, Resources, Pages, Relation Managers, Widgets, Actions, Filters, Eloquent Policies, and Database Migrations.
4. **Resumable Build Protocol**: Milestone execution is tracked in `spec/PROGRESS.md` with explicit acceptance criteria, enabling any session or agent to resume immediately.
5. **Vendor Neutrality**: Operational instructions use standard actions (ask the user, inspect files, execute scripts) compatible with any agent environment.

---

## The 5-Phase Workflow

```
[Phase 1: Discovery]
        │
        ▼
[Phase 2: Spec Generation] ──► Render Docs & Scaffolding
        │
        ▼
[Phase 3: Machine Validation] ◄──┐ Fix violations
        │                        │
        ├── Errors > 0 ──────────┘
        ▼
[Phase 4: Review Gate] ──► <= 15-line summary ──► Await user approval
        │
        ▼ (Approved)
[Phase 5: Resumable TDD Build] ──► Test-First ──► Scaffolding ──► Pint/Larastan ──► PROGRESS.md
```

---

## Phase 1: Discovery

Gather application requirements through repo inspection and a single batched questionnaire.

### 1.1 Existing Repository Inspection
Before prompting the user, inspect the active workspace to detect existing architecture:
- **`composer.json`**: Identify Laravel framework version, installed packages (e.g., `filament/filament`, `laravel/sanctum`, `stancl/tenancy`, `spatie/laravel-permission`), and PHP version constraints.
- **`app/Models/`**: Catalog existing Eloquent models, traits, fillable attributes, and declared relationships.
- **`routes/`**: Inspect `web.php` and `api.php` for existing endpoints, controller bindings, and middleware groups.
- **`database/migrations/`**: Check existing database schema tables and foreign keys.

If existing models or configurations are found, incorporate them into the discovery context and avoid asking redundant questions.

### 1.2 Batched Questionnaire (<= 7 Questions)
Present all applicable questions in a single prompt to minimize turn latency. Adapt questions to fill gaps not answered by workspace inspection:

1. **Domain Scope & Core Entities**: What is the primary purpose of the application, and what are the main domain entities (e.g., User, Product, Order, Invoice)?
2. **User Roles & Authorization**: What distinct user roles exist (e.g., `super-admin`, `admin`, `vendor`, `customer`), and what are their primary privileges?
3. **Filament Panels & UI**: Which Filament panels are required (e.g., Admin panel at `/admin`, Vendor portal at `/vendor`), and which resources belong to each?
4. **Workflows & State Lifecycles**: Do any models follow state transitions (e.g., Order: `pending` -> `processing` -> `completed` / `cancelled`), and who may trigger transitions?
5. **External Integrations**: What third-party services are required (e.g., payment gateways, SMS OTP providers, cloud storage, external webhooks)?
6. **Curated Presets**: Are any domain presets required?
   - `rtl-fa`: Persian RTL layout, Jalali dates (`morilog/jalali`), Vazirmatn font.
   - `iran-payments`: Iranian payment gateways (Zarinpal, Pay.ir, Saman), Rial/Toman currency normalization, idempotency tokens.
   - `otp-login`: Mobile SMS authentication, rate limiting, single-use nonces.
   - `multi-tenant`: Single or multi-database tenant scoping (`stancl/tenancy`).
7. **Tech Stack & Versions**: Any specific requirements for Laravel version (default: 12), Filament version (default: v3), or primary database?

---

## Phase 2: Spec Generation

Synthesize discovery findings into `spec/spec.json` matching `schemas/spec.schema.json`.

### 2.1 Author `spec/spec.json`
Write `spec/spec.json` covering all required top-level sections:
- **`project`**: `name`, `description`, `locale`, `timezone`, `laravel_version`, `filament_version`, `presets`, `audit_log`.
- **`roles`**: Array of roles with `name`, `description`, and at least one role marked `is_super_admin: true`.
- **`models`**: Array of models with database `table`, `fields` (data types, nullability, uniqueness, defaults, indexes, `currency`, `pii`, upload constraints), `relations` (`belongsTo`, `hasMany`, `belongsToMany`, inverse names, foreign keys), and optional `state_machine`.
- **`policies`**: Authorization policies binding every model, standard abilities (`viewAny`, `view`, `create`, `update`, `delete`), and optional `ownership_field`.
- **`filament`**: Panels (`id`, `path`, `auth_guard`, `roles`), and resources (`model`, `pages`, `relation_managers`, `widgets`, `filters`, `actions`, `query_scope`).
- **`integrations`**: External services (`name`, `type`, `description`, `config_keys`, `events_handled`).
- **`milestones`**: Implementation DAG (`id`, `title`, `depends_on`, `scope`, and at least 2 `acceptance` criteria per milestone).

Reference `references/spec-format.md` for full schema specifications.

### 2.2 Render Documentation and Scaffolding Commands
Execute the bundled Python scripts to render markdown documentation and artisan commands:

```bash
# Render the 10 modular documentation files into spec/
python scripts/render_docs.py spec/spec.json --output-dir spec/
# (or: python skills/laravel-spec/scripts/render_docs.py spec/spec.json --output-dir spec/)

# Generate dry-run Artisan scaffolding commands into spec/commands.sh
python scripts/render_commands.py spec/spec.json --output spec/commands.sh
# (or: python skills/laravel-spec/scripts/render_commands.py spec/spec.json --output spec/commands.sh)
```

The rendered markdown files include:
- `00-overview.md`: Executive summary and metadata.
- `01-modules.md`: High-level domain modules.
- `02-database.md`: Complete database schema and relations.
- `03-roles-permissions.md`: Role definitions and policy matrices.
- `04-filament.md`: Filament panels, resources, pages, and relation managers.
- `05-workflows.md`: State machine diagrams and transition rules.
- `06-integrations.md`: Third-party APIs and environment variables.
- `07-security.md`: Authentication, PII handling, upload safety, ownership scoping.
- `08-build-plan.md`: Milestone dependency DAG and acceptance criteria.
- `09-open-questions.md`: Architecture trade-offs and remaining questions.

---

## Phase 3: Machine Validation

Validate `spec/spec.json` using the built-in rule engine before proceeding to review or implementation.

### 3.1 Execute Validation
Run the validator script with `--strict` mode:

```bash
# Execute validation (scripts/validate_spec.py)
python scripts/validate_spec.py spec/spec.json --strict
# (or: python skills/laravel-spec/scripts/validate_spec.py spec/spec.json --strict)
```

### 3.2 Automated Fix Loop
The validator checks 29 distinct rules across 8 categories:
- **Structural**: Valid top-level sections (`STRUC_001`).
- **Uniqueness**: Distinct role names, model names, field names, table names, panel IDs, milestone IDs (`UNIQ_001`, `UNIQ_002`).
- **Relational Integrity**: Target models exist, inverse relations are reciprocal, foreign keys are indexed (`REL_001` - `REL_004`).
- **Authorization & Policies**: Super-admin role declared, policy for every Filament resource, standard abilities mapped, panel role access declared (`AUTH_001` - `AUTH_006`).
- **State Machines**: Target field exists, initial state defined, no unreachable or dead-end states, final states have no outgoing transitions (`SM_001` - `SM_006`).
- **Financial Precision**: Currency fields must use integer minor units or decimal with scale >= 2; float is prohibited (`NUM_001`).
- **Enums**: Enum fields declare non-empty `enum_values` (`ENUM_001`).
- **Milestone DAG**: Kahn's algorithm verifies acyclic dependencies, valid references, model coverage, and >= 2 acceptance criteria per milestone (`DAG_001` - `DAG_004`).
- **Security & Compliance**: PII fields require audit logging, upload fields require size and MIME constraints, ownership scoping requires matching query scopes (`SEC_001` - `SEC_004`).

If violations are reported:
1. Read the reported `rule_id`, `path`, and `fix_hint`.
2. Update `spec/spec.json` to resolve the violation.
3. Re-render docs: `python scripts/render_docs.py spec/spec.json --output-dir spec/`.
4. Re-run validator until `Validation Status: PASSED (0 errors, 0 warnings)`.

Reference `references/validation-rules.md` for rule catalogs and resolution patterns.

---

## Phase 4: Review Gate

Present an executive summary strictly under 15 lines and pause execution for user approval.

### 4.1 Summary Format
Deliver the review gate block in this exact format:

```markdown
### Specification Review: [Project Name]
- **Target**: Laravel [X] + Filament [Y] (Locale: [L], Timezone: [TZ])
- **Presets**: [Active presets or None]
- **Roles**: [N] declared ([super-admin, ...])
- **Models**: [N] domain models ([User, ...])
- **Filament Panels**: [N] panels ([admin at /admin, ...])
- **State Machines**: [N] declared ([Model.field, ...])
- **Integrations**: [N] declared ([Gateways, ...])
- **Milestones**: [N] staged ([M0 -> M1 -> M2])
- **Validation**: PASSED (0 errors, 0 warnings, strict mode)
- **Artifacts**: `spec/spec.json`, `spec/00-overview.md` to `09-open-questions.md`, `spec/commands.sh`

Awaiting user approval to begin implementation. Please review and approve to proceed with Phase 5.
```

### 4.2 Gate Rule
**DO NOT WRITE ANY APPLICATION CODE** before the user explicitly approves this summary. If the user requests modifications, update `spec/spec.json`, re-render docs, re-validate, and present an updated summary.

---

## Phase 5: Resumable TDD Build Protocol

Once approved, execute implementation one milestone at a time following the topological order defined in `spec/spec.json`.

### 5.1 Initialize `spec/PROGRESS.md`
Create or update `spec/PROGRESS.md` documenting milestone status, current milestone, and checklist criteria:

```markdown
# Implementation Progress: [Project Name]

- **Current Milestone**: M0 (Foundation & Authentication)
- **Status**: IN_PROGRESS
- **Overall Completion**: 0% (0 of N milestones completed)

## Milestones

### [IN_PROGRESS] M0: Foundation & Authentication
- Depends on: None
- Scope: User, Role
- Acceptance Criteria:
  - [ ] Core database schema migrations execute cleanly
  - [ ] Baseline Pest/PHPUnit tests pass for User model and authentication
  - [ ] Filament Admin panel provider is registered and accessible
```

### 5.2 The 5-Step Milestone Execution Loop
For each milestone in topological order:

1. **Checkpoint**: Set milestone status to `IN_PROGRESS` in `spec/PROGRESS.md`.
2. **RED (Test First)**:
   - Author automated tests (Pest or PHPUnit) in `tests/Feature/` or `tests/Unit/` asserting all acceptance criteria for the milestone.
   - Run tests (`php artisan test` or `vendor/bin/pest`) and verify they fail as expected.
3. **GREEN (Implementation)**:
   - Execute relevant scaffolding commands from `spec/commands.sh` (e.g., `make:model -m`, `make:filament-resource`).
   - Implement database migrations, model definitions, Eloquent relationships, state machine casts, and policies.
   - Configure Filament resources, form components, table columns, filters, and actions.
   - Re-run tests until 100% green.
4. **REFACTOR & QA**:
   - Run code formatting: `vendor/bin/pint --test` (or `vendor/bin/pint` to auto-fix).
   - Run static analysis: `vendor/bin/phpstan analyse --level=5`.
   - Resolve any warnings or type errors.
5. **COMMIT & CHECKPOINT**:
   - Mark milestone acceptance criteria as completed `[x]` in `spec/PROGRESS.md`.
   - Update milestone status to `COMPLETED` and recalculate completion percentage.
   - Commit with conventional commit message (e.g., `feat(m0): implement foundation and authentication`).

### 5.3 Resuming Work Across Sessions
Any agent can resume an in-progress project without re-reading the entire codebase:
1. Inspect `spec/PROGRESS.md` to identify the active milestone and remaining unchecked criteria.
2. Run existing tests to verify baseline green status.
3. Resume execution from the first incomplete criterion in the active milestone.

Reference `references/build-protocol.md` for complete testing and checkpoint specifications.

---

## Reference Guides

Deep architecture guidance is available in the `references/` directory:
- `references/spec-format.md`: Formal schema documentation and field reference.
- `references/validation-rules.md`: Complete catalog of 29 validation rules and fix hints.
- `references/filament-notes.md`: Filament v3/v4 panels, resources, pages, relation managers, and authorization.
- `references/build-protocol.md`: TDD implementation protocols, testing standards, and `PROGRESS.md` schema.
- `references/presets/rtl-fa.md`: Persian RTL, Jalali dates, and local typography.
- `references/presets/iran-payments.md`: Iranian payment gateways and currency handling.
- `references/presets/otp-login.md`: SMS OTP authentication and rate limiting.
- `references/presets/multi-tenant.md`: Multi-tenant architecture with Stancl Tenancy.
