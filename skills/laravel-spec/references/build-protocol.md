# Resumable TDD Build Execution Protocol

This protocol defines the step-by-step execution lifecycle for implementing a Laravel and Filament application from a validated specification (`spec/spec.json`). It guarantees zero regressions, continuous progress tracking, and effortless resumption across independent agent sessions.

---

## 1. Architectural Foundations

1. **Topological Execution**: Milestones defined in `spec/spec.json` form a Directed Acyclic Graph (DAG). They MUST be executed in topological order (e.g., `M0` -> `M1` -> `M2`).
2. **Test-First Discipline (Red-Green-Refactor)**: No application feature code or Filament resource is considered complete without automated tests proving its acceptance criteria.
3. **Resumable State**: The exact project status is tracked in `spec/PROGRESS.md`. Any agent or engineer can resume work instantly by reading this single file.

---

## 2. Pre-Flight Verification Checklist

Before initiating Milestone 0:
- [ ] `spec/spec.json` exists and passes validation: `python skills/laravel-spec/scripts/validate_spec.py spec/spec.json --strict`.
- [ ] Generated documentation exists in `spec/` (`00-overview.md` through `09-open-questions.md`).
- [ ] Generated Artisan commands script exists in `spec/commands.sh`.
- [ ] Application database is configured and connection verified (`php artisan migrate:status` or sqlite file accessible).
- [ ] Test runner (Pest or PHPUnit) is installed and executable (`vendor/bin/pest` or `php artisan test`).

---

## 3. The 5-Step Milestone Execution Loop

Execute each milestone through the five formal steps:

```
┌───────────────────────────────────────────────┐
│ Step 1: Checkpoint M(X) in spec/PROGRESS.md   │
└───────────────────────┬───────────────────────┘
                        ▼
┌───────────────────────────────────────────────┐
│ Step 2: RED - Write failing acceptance tests  │
└───────────────────────┬───────────────────────┘
                        ▼
┌───────────────────────────────────────────────┐
│ Step 3: GREEN - Implement code & pass tests   │
└───────────────────────┬───────────────────────┘
                        ▼
┌───────────────────────────────────────────────┐
│ Step 4: REFACTOR & QA - Run Pint & Larastan   │
└───────────────────────┬───────────────────────┘
                        ▼
┌───────────────────────────────────────────────┐
│ Step 5: COMMIT & Finalize PROGRESS.md         │
└───────────────────────────────────────────────┘
```

### Step 1: Checkpoint Initialization
- Update `spec/PROGRESS.md` setting current milestone to `IN_PROGRESS`.
- Copy acceptance criteria from `spec/spec.json` into unchecked markdown task items (`- [ ]`).

### Step 2: RED (Author Failing Tests)
- Create targeted feature and unit tests in `tests/Feature/` and `tests/Unit/`.
- Test model relations, validation rules, state machine transitions, policy abilities, and Filament resource visibility.
- Run the test suite:
  ```bash
  vendor/bin/pest --filter MilestoneXTest
  # or
  php artisan test --filter MilestoneXTest
  ```
- **Verify that the tests fail** for the right reasons before writing any implementation code.

### Step 3: GREEN (Implementation)
- Inspect `spec/commands.sh` for the relevant Artisan generators (e.g. `php artisan make:model Product -mfs`, `php artisan make:filament-resource Product`).
- Execute migrations to establish database schema: `php artisan migrate`.
- Implement model classes, relationships, accessors, casts, and state machine transition guards.
- Implement authorization policies in `app/Policies/` and register them.
- Scaffold and configure Filament resources, forms, tables, filters, and actions.
- Re-run test suite until **all tests pass cleanly**.

### Step 4: REFACTOR & Quality Assurance
- Format code according to Laravel standards using Pint:
  ```bash
  vendor/bin/pint --test
  # To auto-fix:
  vendor/bin/pint
  ```
- Run static analysis using Larastan / PHPStan:
  ```bash
  vendor/bin/phpstan analyse --level=5
  ```
- Ensure zero syntax warnings, type errors, or formatting violations.

### Step 5: COMMIT & Checkpoint Finalization
- In `spec/PROGRESS.md`, mark all fulfilled acceptance criteria as completed (`- [x]`).
- Update milestone status to `COMPLETED` and record the completion timestamp.
- Recalculate overall progress percentage.
- Commit all changes using conventional commits:
  ```bash
  git add .
  git commit -m "feat(mX): implement [milestone title]"
  ```

---

## 4. `spec/PROGRESS.md` Format Specification

The `spec/PROGRESS.md` document follows this standardized structure:

```markdown
# Implementation Progress: [Project Name]

- **Status**: [IN_PROGRESS | COMPLETED | BLOCKED]
- **Current Milestone**: M1 (Order Management & Escrow)
- **Overall Completion**: 33% (1 of 3 milestones completed)
- **Last Updated**: 2026-11-02 10:00:00 UTC

---

## Milestones Overview

| Milestone ID | Title | Status | Scope | Depends On | Completed Date |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `M0` | Foundation & Authentication | COMPLETED | User, Role | None | 2026-11-02 |
| `M1` | Order Management & Escrow | IN_PROGRESS | Order, Item | M0 | - |
| `M2` | Payment Gateway & Invoicing | PENDING | Payment | M1 | - |

---

## Active Milestone: M1 - Order Management & Escrow

- **Scope**: `Order`, `OrderItem`
- **Prerequisites**: `M0` (Completed)

### Acceptance Criteria Checklist
- [x] Database migration creates `orders` and `order_items` tables with appropriate indexes
- [x] Eloquent models define reciprocal relationships (`orders()` and `items()`)
- [ ] Order state machine transitions enforce role permissions (`pending` -> `paid` -> `fulfilled`)
- [ ] Filament OrderResource isolates records to owning vendor via query scope

### Verification Record
- **Tests**: `tests/Feature/OrderManagementTest.php` (4 passed, 2 pending)
- **Static Analysis**: `phpstan` level 5 clean
- **Code Style**: `pint` clean

### Notes & Decisions
- Minor currency units stored as `total_cents` (bigInteger) per financial precision rules.

---

## Completed Milestones Archive

### M0: Foundation & Authentication (Completed: 2026-11-02)
- All 3 acceptance criteria verified by automated tests.
- Commit: `a1b2c3d`
```

---

## 5. Agent Resumption Protocol

When a new agent session begins or context resets:
1. **Locate Progress File**: Read `spec/PROGRESS.md`.
2. **Identify Active Milestone**: Find the milestone marked `IN_PROGRESS` (or the first `PENDING` milestone if prior was completed).
3. **Verify Baseline**: Run existing test suite (`php artisan test`) to ensure everything previously completed is still green.
4. **Locate Next Criterion**: Find the first unchecked item (`- [ ]`) in the active milestone's acceptance criteria checklist.
5. **Resume TDD Loop**: Write a test for this criterion, implement the code, verify green, and continue the loop.
