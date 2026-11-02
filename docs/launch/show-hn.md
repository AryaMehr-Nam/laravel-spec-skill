# Launch Draft: Show HN

**Title:** Show HN: laravel-spec – Machine-validated specifications for AI-driven Laravel apps

---

Hi HN,

We built **laravel-spec**, an open-source toolchain and agent skill that compiles natural-language project descriptions into machine-validated specifications (`spec/spec.json`), enforces 29 structural and architectural invariants, and drives an iterative test-first build for Laravel 11/12 and Filament v3/v4 applications.

GitHub: https://github.com/example/laravel-spec-skill

### Why we built this

Coding agents (Claude Code, Cursor, Codex, Antigravity) are impressively capable at writing isolated functions, but they struggle with architectural discipline when building entire applications. When tasked with a full web app from scratch, they tend to generate code immediately. By the time 20 files are written, errors have compounded:
- Float types used for currency (`$table->float('price')`), introducing floating-point math bugs.
- Foreign keys declared without database indexes.
- State machines with unreachable states or terminal states that allow outbound transitions.
- Filament admin resources created without authorization policies or tenancy query scopes.
- Milestone dependencies structured with circular dependencies.

Probabilistic models are great at synthesis, but software architecture requires deterministic invariants.

### The Architecture: A Specification Gate

Instead of generating PHP directly, `laravel-spec` interposes a formal validation loop before any application code is written:

1. **Discovery & Synthesis**: The agent inspects `composer.json` and existing models to avoid redundant questions, asks a single batched questionnaire (max 7 questions), and outputs `spec/spec.json`.
2. **29-Rule Zero-Dependency Validation Suite**: Written using only the Python 3.10+ standard library (no pydantic, no external wheels), `validate_spec.py` enforces:
   - **Relational Integrity**: Model existence, bidirectional relations, and foreign key index declarations (`REL_001` - `REL_004`).
   - **Authorization Completeness**: Role existence, required super-admin role, policy binding for all Filament resources (`AUTH_001` - `AUTH_006`).
   - **State Machine Graph Traversal**: Initial state definition, dead-end detection, and reachability via graph traversal (`SM_001` - `SM_006`).
   - **Financial Invariants**: Rejection of float types on currency fields, requiring integer minor units or decimal scale >= 2 (`NUM_001`).
   - **Milestone DAG**: Cycle detection using Kahn's topological sort algorithm and minimum acceptance criteria thresholds (`DAG_001` - `DAG_004`).
   - **Security**: Mandatory audit logging for PII, upload mime/size limits, and Filament tenant query scoping (`SEC_001` - `SEC_004`).
3. **Deterministic Renderers**:
   - `render_docs.py` produces 10 modular markdown files (`00-overview.md` through `09-open-questions.md`). Hash-identical output across repeated runs.
   - `render_commands.py` outputs dependency-ordered, dry-run Artisan scaffolding commands (`make:model -mfsc`, `make:policy`, `make:filament-resource`).
4. **Resumable TDD Build**:
   The agent executes milestones in topological order, writing tests (Pest/PHPUnit) first, running Pint and Larastan, and recording checkpoints in `spec/PROGRESS.md` so work can be resumed across agent context resets.

### Ecosystem Presets

We bundle 4 modular presets:
- `rtl-fa`: Persian RTL layout for Filament, Morilog Jalali solar calendar, and local Vazirmatn font (zero CDN dependencies).
- `iran-payments`: Multi-gateway routing (Zarinpal, Shepa, Saman SEP), unique idempotency keys, and Rial/Toman conversion handling.
- `otp-login`: Passwordless SMS authentication, rate limits, 120s TTL, single-use cryptographic nonces.
- `multi-tenant`: Single-database row scoping and multi-database isolation (`stancl/tenancy`).

### Quick Try

```bash
git clone https://github.com/example/laravel-spec-skill.git
cd laravel-spec-skill

# Run the 29-rule validator on the included multi-vendor marketplace example:
python scripts/validate_spec.py examples/marketplace/spec.json --strict

# Run the test suite (150 tests, standard pytest):
pytest
```

The repo is MIT licensed. We'd love feedback on the schema design, additional invariant checks, or your experience using spec-first agent workflows.
