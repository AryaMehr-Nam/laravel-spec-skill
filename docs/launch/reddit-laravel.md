# Launch Draft: r/laravel

**Suggested Title:** We built an open-source spec engine and Agent Skill for Laravel 11/12 + Filament v3/v4 to prevent AI agents from generating garbage architectures

---

Hey r/laravel!

Like many of you, our team uses AI coding agents (Claude Code, Cursor, Antigravity) to accelerate feature development. But when you ask an LLM to scaffold or build a complete Laravel + Filament application, the failure modes are predictable and frustrating:

1. **Floating point money**: The LLM writes `$table->float('price')` instead of `$table->unsignedBigInteger('amount_cents')` or `$table->decimal('amount', 12, 2)`.
2. **Missing FK indexes**: It defines `user_id` or `tenant_id` foreign keys without indexes, killing database performance under load.
3. **Forgotten Filament Policies**: It scaffolds Filament resources but forgets to bind Eloquent policies or scopes, exposing sensitive tenant records across panels.
4. **State Machine Bugs**: It defines order or payment statuses with dead-end states, impossible transitions, or missing role permissions.
5. **Chaotic Build Sequence**: It starts generating controllers before migrations, or forgets which models need to be built first.

To solve this, we created **`laravel-spec-skill`**: an open-source specification compiler, validation suite, and agent skill designed specifically for modern Laravel (11/12) and Filament (v3/v4).

---

### What it Does

Rather than letting the AI jump straight to writing PHP files, `laravel-spec-skill` forces a **machine-validated specification gate**:

1. **Structured Specification (`spec/spec.json`)**:
   Captures models, fields, relations, policies, Filament panels/resources, integrations, and milestones in a machine-readable schema.

2. **29-Rule Zero-Dependency Validation Suite (`validate_spec.py`)**:
   Runs standard-library Python to enforce strict Laravel best practices before a single file is touched:
   - `NUM_001`: Prohibits `float` on currency fields.
   - `REL_003`: Flags foreign keys missing indexes.
   - `AUTH_002`: Fails if a Filament Resource lacks a policy.
   - `AUTH_004`: Requires an explicit super-admin role.
   - `SM_001` - `SM_006`: Validates state transition reachability, dead-end states, and authorized roles.
   - `DAG_001`: Detects circular milestone dependencies using Kahn's topological sort.
   - `SEC_001`: Mandates `project.audit_log: true` if any model contains PII.
   - `SEC_004`: Enforces tenancy `query_scope` on Filament resources when ownership fields exist.

3. **Deterministic Documentation & Command Scaffolding**:
   - `render_docs.py` compiles `spec.json` into 10 modular docs (`00-overview.md` to `09-open-questions.md`). Byte-for-byte identical every run.
   - `render_commands.py` outputs dry-run Artisan CLI commands (`make:model -mfsc`, `make:policy`, `make:filament-resource`) sorted in dependency order.

4. **Curated Presets**:
   - `rtl-fa`: Persian RTL support in Filament, Morilog Jalali solar dates, local Vazirmatn font (zero CDN dependencies).
   - `iran-payments`: Multi-gateway routing (Zarinpal, Shepa, Saman SEP), atomic verification, `idempotency_key` unique constraints, and Rial/Toman normalization.
   - `otp-login`: Mobile SMS authentication with rate limiting, 120s expiry, single-use nonces, and enumeration defense.
   - `multi-tenant`: Single-database row scoping and multi-database isolation patterns (`stancl/tenancy`).

5. **Resumable TDD Build**:
   Tracks progress in `spec/PROGRESS.md`. When your agent's session ends, the next session reads the progress checkpoint and resumes the exact next milestone with test-first rigor.

---

### Check Out the Repo & Examples

The repository includes complete, fully validated reference specifications:
- `examples/marketplace/`: Multi-vendor marketplace with vendor escrow, commissions, orders, and Filament admin/vendor panels.
- `examples/crm/`: CRM reference example with sales lead lifecycles, customer scoping, and audit logs.

```bash
git clone https://github.com/AryaMehr-Nam/laravel-spec-skill.git
cd laravel-spec-skill

# Run validation on the marketplace example
python scripts/validate_spec.py examples/marketplace/spec.json --strict
```

Repo: https://github.com/AryaMehr-Nam/laravel-spec-skill (MIT License)

We'd love to hear your feedback, bug reports, and ideas for additional validation rules!
