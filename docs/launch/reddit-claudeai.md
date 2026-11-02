# Launch Draft: r/ClaudeAI

**Suggested Title:** Stop Claude Code from hallucinating messy Laravel architectures: we built a machine-validated specification skill with 29 invariant checks

---

Hey r/ClaudeAI!

If you've used Claude Code (or any coding agent) on non-trivial web apps, you've probably hit the "premature code generation" trap:

You give Claude a prompt like:
> *"Build me a multi-vendor marketplace with Filament admin, vendor payouts, and order tracking."*

Claude immediately starts spitting out migration files, controllers, and livewire components. By file 15:
- It used `$table->float('amount')` for prices, setting you up for IEEE 754 floating-point rounding nightmares.
- It forgot `$table->index('vendor_id')` on foreign keys.
- It created Filament Resources with zero authorization policies, leaving them wide open.
- The Order lifecycle has unreachable states or dead ends.
- If the agent context resets, it forgets where it was and hallucinates a duplicate milestone.

To fix this, we built **`laravel-spec-skill`** — an open-source [Agent Skill](https://github.com/agentskills/agentskills) that puts a **machine-validated specification gate** between requirements and code generation.

---

### How It Works (The 5-Phase Protocol)

1. **Discovery**: Claude inspects `composer.json` and existing models first, then asks at most 7 batched questions. No endless ping-pong.
2. **Spec Synthesis**: Claude outputs a single canonical `spec/spec.json` and renders 10 modular markdown docs (`00-overview.md` to `09-open-questions.md`) + dry-run Artisan scaffolding commands.
3. **Machine Validation Gate**: Before writing a single line of PHP, Claude runs `python scripts/validate_spec.py spec/spec.json`. A zero-dependency Python rule engine checks **29 architectural invariants**:
   - Relational integrity & foreign key index checks (`REL_001` - `REL_004`)
   - State machine reachability & dead-end detection (`SM_001` - `SM_006`)
   - Financial precision enforcement (`NUM_001`: hard error on `float` currency)
   - Policy completeness & super-admin verification (`AUTH_001` - `AUTH_006`)
   - Acyclic milestone DAG verification via Kahn's algorithm (`DAG_001`)
   - PII audit logging & tenant query scoping (`SEC_001` - `SEC_004`)
   If any rule fails, Claude fixes `spec.json` and re-validates. **Zero errors required.**
4. **Review Gate**: Claude presents a concise <= 15-line architectural summary and pauses for user sign-off.
5. **Resumable TDD Build**: Claude executes milestones strictly in topological DAG order, writing Pest/PHPUnit tests first, running Pint/Larastan, and logging checkpoints to `spec/PROGRESS.md`.

---

### Key Features
- **Zero Runtime Dependencies**: The validator, doc renderer, and command generator use Python 3.10+ standard library only.
- **Battle-Tested Presets**: Bundles architectural presets for Persian RTL (`rtl-fa`), Iranian payment gateways with idempotency keys (`iran-payments`), SMS OTP passwordless auth (`otp-login`), and SaaS multi-tenancy (`multi-tenant`).
- **Complete Reference Examples**: Includes full specifications for a multi-vendor marketplace and an enterprise CRM.
- **Cross-Agent**: Works with Claude Code, Antigravity, Cursor, and OpenAI Codex CLI.

### Quickstart
```bash
# Install via Agent Skills CLI
npx skills add github:example/laravel-spec-skill

# Or install with the bundled installer
git clone https://github.com/example/laravel-spec-skill.git
python laravel-spec-skill/scripts/install.py --target claude
```

Repo: https://github.com/example/laravel-spec-skill (MIT Licensed)

Would love your thoughts, feedback, and what other validation rules you'd like to see!
