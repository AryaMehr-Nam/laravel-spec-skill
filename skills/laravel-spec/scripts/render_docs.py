"""Markdown documentation renderer for Laravel Filament specifications.

Converts spec/spec.json into 10 modular, strictly deterministic markdown
documents (00-overview.md through 09-open-questions.md).
Standard library only (Python 3.10+).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

DOC_FILENAMES = (
    "00-overview.md",
    "01-modules.md",
    "02-database.md",
    "03-roles-permissions.md",
    "04-filament.md",
    "05-workflows.md",
    "06-integrations.md",
    "07-security.md",
    "08-build-plan.md",
    "09-open-questions.md",
)


def _render_overview(spec: dict[str, Any]) -> str:
    proj = spec.get("project", {})
    models = spec.get("models", [])
    roles = spec.get("roles", [])
    filament = spec.get("filament", {})
    panels = filament.get("panels", []) if isinstance(filament, dict) else []
    integrations = spec.get("integrations", [])
    milestones = spec.get("milestones", [])
    presets = proj.get("presets", [])

    preset_str = ", ".join(f"`{p}`" for p in presets) if presets else "None"
    audit_str = "Enabled" if proj.get("audit_log") else "Disabled"
    desc_str = proj.get("description", "Enterprise application built with Laravel and Filament.")

    lines = [
        f"# Overview: {proj.get('name', 'Laravel Application')}",
        "",
        f"> {desc_str}",
        "",
        "## Project Metadata",
        "",
        "| Property | Value |",
        "| :--- | :--- |",
        f"| **Application Name** | {proj.get('name', 'N/A')} |",
        f"| **Description** | {proj.get('description', 'N/A')} |",
        f"| **Primary Locale** | `{proj.get('locale', 'en')}` |",
        f"| **Default Timezone** | `{proj.get('timezone', 'UTC')}` |",
        f"| **Laravel Version** | `v{proj.get('laravel_version', '12')}` |",
        f"| **Filament Version** | `{proj.get('filament_version', 'v3')}` |",
        f"| **Audit Logging** | {audit_str} |",
        f"| **Presets** | {preset_str} |",
        "",
        "## Architectural Summary",
        "",
        f"- **Domain Models**: {len(models)} declared",
        f"- **Security Roles**: {len(roles)} declared",
        f"- **Filament Panels**: {len(panels)} configured",
        f"- **External Integrations**: {len(integrations)} configured",
        f"- **Implementation Milestones**: {len(milestones)} staged in dependency graph",
        "",
    ]
    return "\n".join(lines)


def _render_modules(spec: dict[str, Any]) -> str:
    models = spec.get("models", [])
    lines = [
        "# Functional Modules & Domain Entities",
        "",
        "This document details the functional domains and entity boundaries.",
        "",
        "## Domain Entities Summary",
        "",
        "| Model | Table | Fields | Relations | State Machine |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]

    if not models:
        lines.append("| _None_ | _None_ | 0 | 0 | None |")
    else:
        for m in models:
            mname = m.get("name", "Unknown")
            table = m.get("table", "unknown")
            fcount = len(m.get("fields", []))
            rcount = len(m.get("relations", []))
            has_sm = "Yes" if m.get("states") else "No"
            lines.append(f"| **{mname}** | `{table}` | {fcount} | {rcount} | {has_sm} |")

    lines.append("")
    lines.append("## Module Structure")
    lines.append("")

    if not models:
        lines.append("_No domain models declared in this specification._\n")
    else:
        for m in models:
            mname = m.get("name", "Unknown")
            table = m.get("table", "unknown")
            desc = m.get("description", f"Encapsulates domain logic for `{mname}` entities.")
            fields = m.get("fields", [])
            relations = m.get("relations", [])

            lines.append(f"### {mname} Module")
            lines.append(f"- **Database Table**: `{table}`")
            lines.append(f"- **Purpose**: {desc}")
            kfields = [f.get("name") for f in fields[:5] if isinstance(f, dict) and f.get("name")]
            kstr = ", ".join(f"`{k}`" for k in kfields) if kfields else "N/A"
            lines.append(f"- **Key Attributes**: {kstr}")
            rel_names = [r.get("name") for r in relations if isinstance(r, dict) and r.get("name")]
            rel_str = ", ".join(f"`{r}`" for r in rel_names) if rel_names else "None"
            lines.append(f"- **Associated Relations**: {rel_str}")
            lines.append("")

    return "\n".join(lines)


def _render_database(spec: dict[str, Any]) -> str:
    models = spec.get("models", [])
    lines = [
        "# Database Schema & Data Models",
        "",
        "This document details the database schema, column types, and relationships.",
        "",
        "## Tables Overview",
        "",
        "| Model | Table | Primary Key | Foreign References |",
        "| :--- | :--- | :--- | :--- |",
    ]

    if not models:
        lines.append("| _None_ | _None_ | N/A | None |")
    else:
        for m in models:
            mname = m.get("name", "Unknown")
            table = m.get("table", "unknown")
            fkeys = [
                f"{f.get('name')} -> {f.get('foreign', {}).get('model', 'Unknown')}"
                for f in m.get("fields", [])
                if isinstance(f, dict) and isinstance(f.get("foreign"), dict)
            ]
            fkey_str = ", ".join(f"`{k}`" for k in fkeys) if fkeys else "None"
            lines.append(f"| **{mname}** | `{table}` | `id` (bigInteger) | {fkey_str} |")

    lines.append("")
    lines.append("## Detailed Schema Definitions")
    lines.append("")

    if not models:
        lines.append("_No database tables defined in specification._\n")
    else:
        for m in models:
            mname = m.get("name", "Unknown")
            table = m.get("table", "unknown")
            fields = m.get("fields", [])
            relations = m.get("relations", [])

            lines.append(f"### `{mname}` (`{table}`)")
            lines.append("")
            lines.append("#### Columns")
            lines.append("")
            lines.append("| Column | Type | Nullable | Index / Unique | Constraints & Details |")
            lines.append("| :--- | :--- | :--- | :--- | :--- |")

            for f in fields:
                if not isinstance(f, dict):
                    continue
                fname = f.get("name", "")
                ftype = f.get("type", "string")
                nullable = "Yes" if f.get("nullable") else "No"
                idx_parts = []
                if f.get("unique"):
                    idx_parts.append("UNIQUE")
                if f.get("index"):
                    idx_parts.append("INDEX")
                idx_str = ", ".join(idx_parts) if idx_parts else "-"

                details: list[str] = []
                if f.get("foreign"):
                    details.append(f"FK -> {f.get('foreign', {}).get('model')}")
                if ftype == "enum" and f.get("enum_values"):
                    details.append(f"Values: [{', '.join(f.get('enum_values', []))}]")
                if ftype == "decimal":
                    prec = f.get("precision", 10)
                    scale = f.get("scale", 2)
                    details.append(f"Decimal({prec}, {scale})")
                if ftype in ("file", "image"):
                    max_kb = f.get("max_size_kb")
                    mimes = f.get("allowed_mimes", [])
                    details.append(f"Max: {max_kb}KB, Mimes: {', '.join(mimes)}")
                if f.get("pii"):
                    details.append("PII: Encrypted/Audited")

                detail_str = "; ".join(details) if details else "-"
                lines.append(f"| `{fname}` | `{ftype}` | {nullable} | {idx_str} | {detail_str} |")

            lines.append("")
            lines.append("#### Eloquent Relationships")
            lines.append("")
            if not relations:
                lines.append("_No Eloquent relationships defined for this model._")
            else:
                lines.append("| Method | Type | Related Model | Foreign Key | Inverse Method |")
                lines.append("| :--- | :--- | :--- | :--- | :--- |")
                for r in relations:
                    if not isinstance(r, dict):
                        continue
                    rname = r.get("name", "")
                    rtype = r.get("type", "")
                    rmodel = r.get("model", "")
                    rfk = r.get("foreign_key", f"{rname}_id")
                    rinv = r.get("inverse", "-")
                    lines.append(
                        f"| `{rname}()` | `{rtype}` | `{rmodel}` | `{rfk}` | `{rinv}` |"
                    )

            lines.append("")

    return "\n".join(lines)


def _render_roles_permissions(spec: dict[str, Any]) -> str:
    roles = spec.get("roles", [])
    policies = spec.get("policies", [])

    lines = [
        "# Roles, Permissions & Authorization Matrix",
        "",
        "This document specifies system roles, policy abilities, and ownership scoping rules.",
        "",
        "## Defined Roles",
        "",
        "| Role | Super Administrator | Description |",
        "| :--- | :--- | :--- |",
    ]

    for r in roles:
        if not isinstance(r, dict):
            continue
        rname = r.get("name", "")
        is_super = "Yes (Full Access)" if r.get("is_super_admin") else "No"
        desc = r.get("description", "-")
        lines.append(f"| **{rname}** | {is_super} | {desc} |")

    lines.append("")
    lines.append("## Policy Authorization Matrix")
    lines.append("")

    if not policies:
        lines.append("_No policies declared in specification._\n")
    else:
        for p in policies:
            if not isinstance(p, dict):
                continue
            model = p.get("model", "Unknown")
            ownership = p.get("ownership", "none")
            abilities = p.get("abilities", {})

            lines.append(f"### `{model}` Policy (`{model}Policy`)")
            lines.append(f"- **Ownership Constraint**: `{ownership}`")
            lines.append("")
            lines.append("| Ability | Authorized Roles | Ownership Scoped |")
            lines.append("| :--- | :--- | :--- |")

            sorted_abilities = sorted(abilities.keys()) if isinstance(abilities, dict) else []
            for ab in sorted_abilities:
                auth_roles = abilities.get(ab, [])
                if isinstance(auth_roles, list):
                    role_str = ", ".join(f"`{r}`" for r in auth_roles) if auth_roles else "_None_"
                else:
                    role_str = str(auth_roles)
                is_sc = (
                    "Yes"
                    if ownership != "none" and ab in ("view", "update", "delete")
                    else "No"
                )
                lines.append(f"| `{ab}` | {role_str} | {is_sc} |")

            lines.append("")

    return "\n".join(lines)


def _render_filament(spec: dict[str, Any]) -> str:
    filament = spec.get("filament", {})
    panels = filament.get("panels", []) if isinstance(filament, dict) else []

    lines = [
        "# Filament Admin & User Panels",
        "",
        "This document describes Filament panels, panel routes, and registered panel resources.",
        "",
        "## Configured Panels",
        "",
        "| Panel ID | Route Path | Access Roles | Resources Count |",
        "| :--- | :--- | :--- | :--- |",
    ]

    if not panels:
        lines.append("| _None_ | _None_ | None | 0 |")
    else:
        for pan in panels:
            if not isinstance(pan, dict):
                continue
            pid = pan.get("id", "admin")
            path = pan.get("path", "admin")
            roles = pan.get("roles", [])
            role_str = ", ".join(f"`{r}`" for r in roles) if roles else "Public / All"
            rcount = len(pan.get("resources", []))
            lines.append(f"| **{pid}** | `/{path}` | {role_str} | {rcount} |")

    lines.append("")
    lines.append("## Panel Resources & Pages")
    lines.append("")

    if not panels:
        lines.append("_No Filament panels declared in specification._\n")
    else:
        for pan in panels:
            if not isinstance(pan, dict):
                continue
            pid = pan.get("id", "admin")
            path = pan.get("path", "admin")
            resources = pan.get("resources", [])

            lines.append(f"### Panel: `{pid}` (Route: `/{path}`)")
            lines.append("")

            if not resources:
                lines.append("_No resources assigned to this panel._")
            else:
                lines.append(
                    "| Resource Model | Filament Resource Class | Query Scope | Relation Mgrs |"
                )
                lines.append("| :--- | :--- | :--- | :--- |")
                for res in resources:
                    if not isinstance(res, dict):
                        continue
                    rmodel = res.get("model", "")
                    rclass = f"{rmodel}Resource"
                    tbl = res.get("table", {}) if isinstance(res.get("table"), dict) else {}
                    qscope = tbl.get("query_scope", "Default (all records)")
                    rel_mgrs = res.get("relation_managers", [])
                    rel_str = ", ".join(f"`{rm}`" for rm in rel_mgrs) if rel_mgrs else "None"
                    lines.append(f"| **{rmodel}** | `{rclass}` | `{qscope}` | {rel_str} |")

            lines.append("")

    return "\n".join(lines)


def _render_workflows(spec: dict[str, Any]) -> str:
    models = spec.get("models", [])
    models_with_states = [
        m for m in models if isinstance(m, dict) and isinstance(m.get("states"), dict)
    ]

    lines = [
        "# Workflows & Finite State Machines",
        "",
        "This document defines lifecycle states, valid state transitions, and role permissions.",
        "",
    ]

    if not models_with_states:
        lines.append("## State Machines Summary")
        lines.append("")
        lines.append("_No finite state machines defined in this specification._\n")
        return "\n".join(lines)

    lines.append("## State Machines Summary")
    lines.append("")
    lines.append("| Model | State Column | Initial State | Final / Terminal States | Transitions |")
    lines.append("| :--- | :--- | :--- | :--- | :--- |")

    for m in models_with_states:
        mname = m.get("name", "")
        st = m.get("states", {})
        col = st.get("field", "status")
        init = st.get("initial", "pending")
        finals = st.get("final", [])
        final_str = ", ".join(f"`{f}`" for f in finals) if finals else "None"
        tcount = len(st.get("transitions", []))
        lines.append(f"| **{mname}** | `{col}` | `{init}` | {final_str} | {tcount} |")

    lines.append("")
    lines.append("## Transition Rules by Model")
    lines.append("")

    for m in models_with_states:
        mname = m.get("name", "")
        st = m.get("states", {})
        col = st.get("field", "status")
        init = st.get("initial", "pending")
        finals = st.get("final", [])
        transitions = st.get("transitions", [])
        final_str = ", ".join(f"`{f}`" for f in finals) if finals else "None"

        lines.append(f"### `{mname}` Workflow (`{col}`)")
        lines.append(f"- **Initial State**: `{init}`")
        lines.append(f"- **Final States**: {final_str}")
        lines.append("")
        lines.append("| Current State (From) | Next State (To) | Authorized Roles |")
        lines.append("| :--- | :--- | :--- |")

        for tr in transitions:
            if not isinstance(tr, dict):
                continue
            src = tr.get("from", "")
            dst = tr.get("to", "")
            roles = tr.get("roles", [])
            role_str = ", ".join(f"`{r}`" for r in roles) if roles else "Any authenticated role"
            lines.append(f"| `{src}` | `{dst}` | {role_str} |")

        lines.append("")

    return "\n".join(lines)


def _render_integrations(spec: dict[str, Any]) -> str:
    integrations = spec.get("integrations", [])

    lines = [
        "# External Integrations & Services",
        "",
        "This document details external providers, payment gateways, and third-party APIs.",
        "",
        "## Configured Integrations",
        "",
        "| Name | Kind / Category | Provider | Description |",
        "| :--- | :--- | :--- | :--- |",
    ]

    if not integrations:
        lines.append("| _None_ | _None_ | None | No external integrations configured. |")
    else:
        for integ in integrations:
            if not isinstance(integ, dict):
                continue
            name = integ.get("name", "Unknown")
            kind = integ.get("kind", "service")
            provider = integ.get("provider", name)
            desc = integ.get("description", "-")
            lines.append(f"| **{name}** | `{kind}` | `{provider}` | {desc} |")

    lines.append("")
    lines.append("## Configuration & Secrets Guidance")
    lines.append("")

    if not integrations:
        lines.append("_No external integrations configured in this specification._\n")
    else:
        for integ in integrations:
            if not isinstance(integ, dict):
                continue
            name = integ.get("name", "Unknown")
            kind = integ.get("kind", "service")
            provider = integ.get("provider", name)

            lines.append(f"### {name} (`{kind}`)")
            lines.append(f"- **Provider / Package**: `{provider}`")
            lines.append("- **Environment Variables**: Configure in `.env` securely.")
            lines.append("- **Resilience**: Retries with exponential backoff and timeout.")
            lines.append("")

    return "\n".join(lines)


def _render_security(spec: dict[str, Any]) -> str:
    proj = spec.get("project", {})
    models = spec.get("models", [])
    policies = spec.get("policies", [])
    audit_enabled = bool(proj.get("audit_log"))

    pii_entries: list[tuple[str, str, str]] = []
    upload_entries: list[tuple[str, str, str, str]] = []

    for m in models:
        if not isinstance(m, dict):
            continue
        mname = m.get("name", "Unknown")
        for f in m.get("fields", []):
            if not isinstance(f, dict):
                continue
            fname = f.get("name", "")
            ftype = f.get("type", "string")
            if f.get("pii"):
                pii_entries.append((mname, fname, ftype))
            if ftype in ("file", "image"):
                max_size = f"{f.get('max_size_kb', 0)} KB"
                mimes = ", ".join(f.get("allowed_mimes", []))
                upload_entries.append((mname, fname, max_size, mimes))

    lines = [
        "# Security, Compliance & Data Safeguards",
        "",
        "This document outlines PII tracking, audit logging, upload security, and data scoping.",
        "",
        "## Personally Identifiable Information (PII)",
        "",
        "| Model | Field Name | Column Type | Audit Logging Required |",
        "| :--- | :--- | :--- | :--- |",
    ]

    if not pii_entries:
        lines.append("| _None_ | _None_ | - | No PII fields declared. |")
    else:
        for mname, fname, ftype in pii_entries:
            lines.append(f"| **{mname}** | `{fname}` | `{ftype}` | Yes (Monitored) |")

    lines.append("")
    lines.append("## Audit Logging Architecture")
    lines.append("")
    audit_status = "Active & Enforced" if audit_enabled else "Not Enforced"
    lines.append(f"- **Audit Logging Status**: {audit_status}")
    if audit_enabled:
        lines.append("- **Scope**: Modifications to PII fields, finances, and state transitions.")
        lines.append("- **Recommendation**: `spatie/laravel-activitylog` or event listeners.")
    else:
        lines.append("- **Notice**: No global audit logging enabled in project settings.")

    lines.append("")
    lines.append("## File Upload Constraints")
    lines.append("")
    lines.append("| Model | Field | Max Size | Allowed MIME Types |")
    lines.append("| :--- | :--- | :--- | :--- |")

    if not upload_entries:
        lines.append("| _None_ | _None_ | - | No file upload columns defined. |")
    else:
        for mname, fname, max_size, mimes in upload_entries:
            lines.append(f"| **{mname}** | `{fname}` | {max_size} | `{mimes}` |")

    lines.append("")
    lines.append("## Tenant & Ownership Scoping")
    lines.append("")
    lines.append("| Model | Ownership Policy Scoping |")
    lines.append("| :--- | :--- |")

    if not policies:
        lines.append("| _None_ | No policies declared. |")
    else:
        for p in policies:
            if not isinstance(p, dict):
                continue
            mname = p.get("model", "Unknown")
            ownership = p.get("ownership", "none")
            lines.append(f"| **{mname}** | `{ownership}` |")

    lines.append("")
    return "\n".join(lines)


def _render_build_plan(spec: dict[str, Any]) -> str:
    milestones = spec.get("milestones", [])

    lines = [
        "# Implementation Build Plan & Milestone DAG",
        "",
        "This document specifies the resumable build milestones, dependencies, and criteria.",
        "",
        "## Milestones Summary",
        "",
        "| Milestone | Title | Depends On | Model Scope | Acceptance Criteria Count |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]

    if not milestones:
        lines.append("| _None_ | _None_ | None | None | 0 |")
    else:
        for ms in milestones:
            if not isinstance(ms, dict):
                continue
            mid = ms.get("id", "M0")
            title = ms.get("title", "Untitled")
            deps = ms.get("depends_on", [])
            dep_str = ", ".join(f"`{d}`" for d in deps) if deps else "None (Root)"
            scope = ms.get("scope", [])
            scope_str = ", ".join(f"`{s}`" for s in scope) if scope else "Global / Foundation"
            ac_count = len(ms.get("acceptance", []))
            lines.append(f"| **{mid}** | {title} | {dep_str} | {scope_str} | {ac_count} |")

    lines.append("")
    lines.append("## Milestone Details & Verification Criteria")
    lines.append("")

    if not milestones:
        lines.append("_No milestones declared in specification._\n")
    else:
        for ms in milestones:
            if not isinstance(ms, dict):
                continue
            mid = ms.get("id", "M0")
            title = ms.get("title", "Untitled")
            deps = ms.get("depends_on", [])
            scope = ms.get("scope", [])
            acceptance = ms.get("acceptance", [])

            dep_text = ", ".join(f"`{d}`" for d in deps) if deps else "None (Foundation)"
            scope_text = ", ".join(f"`{s}`" for s in scope) if scope else "Initial Setup"

            lines.append(f"### Milestone `{mid}`: {title}")
            lines.append(f"- **Dependencies**: {dep_text}")
            lines.append(f"- **Model Scope**: {scope_text}")
            lines.append("")
            lines.append("#### Acceptance Criteria")
            lines.append("")
            if not acceptance:
                lines.append("- [ ] No specific acceptance criteria declared.")
            else:
                for item in acceptance:
                    lines.append(f"- [ ] {item}")

            lines.append("")

    return "\n".join(lines)


def _render_open_questions(spec: dict[str, Any]) -> str:
    proj = spec.get("project", {})
    open_questions = spec.get("open_questions", [])

    lines = [
        "# Open Questions & Architecture Decisions",
        "",
        "This document tracks architectural inquiries, edge cases, and assumptions.",
        "",
        "## Pending Questions",
        "",
    ]

    if not open_questions:
        lines.append("No open questions remain pending. All specifications are verified.")
        lines.append("")
    else:
        lines.append("| ID | Category | Question | Proposed Resolution | Status |")
        lines.append("| :--- | :--- | :--- | :--- | :--- |")
        for idx, q in enumerate(open_questions, 1):
            if isinstance(q, dict):
                qid = q.get("id", f"Q{idx}")
                cat = q.get("category", "General")
                question = q.get("question", "")
                resolution = q.get("resolution", "Under Review")
                status = q.get("status", "Open")
                lines.append(f"| **{qid}** | `{cat}` | {question} | {resolution} | `{status}` |")
            else:
                lines.append(f"| **Q{idx}** | `General` | {q} | Under Review | `Open` |")
        lines.append("")

    lv = proj.get("laravel_version", "12")
    fv = proj.get("filament_version", "v3")

    lines.append("## Technical Baseline & Assumptions")
    lines.append("")
    lines.append(f"- **Framework Baseline**: Laravel `v{lv}` with PHP 8.3+")
    lines.append(f"- **Admin Panel**: Filament `{fv}`")
    lines.append("- **Test Strategy**: Pest / PHPUnit tests for policy abilities and workflows")
    lines.append("- **Database Engine**: RDBMS with atomic transactions and foreign keys")
    lines.append("")
    return "\n".join(lines)


def render_docs(spec: dict[str, Any]) -> dict[str, str]:
    """Deterministically render all 10 markdown specification documents.

    Args:
        spec: Valid specification dictionary.

    Returns:
        Mapping of document filename to rendered markdown string.
    """
    return {
        "00-overview.md": _render_overview(spec),
        "01-modules.md": _render_modules(spec),
        "02-database.md": _render_database(spec),
        "03-roles-permissions.md": _render_roles_permissions(spec),
        "04-filament.md": _render_filament(spec),
        "05-workflows.md": _render_workflows(spec),
        "06-integrations.md": _render_integrations(spec),
        "07-security.md": _render_security(spec),
        "08-build-plan.md": _render_build_plan(spec),
        "09-open-questions.md": _render_open_questions(spec),
    }


def write_docs(docs: dict[str, str], output_dir: str | Path) -> list[Path]:
    """Write rendered markdown documents to destination directory.

    Args:
        docs: Mapping of filename to markdown content.
        output_dir: Destination directory path.

    Returns:
        List of written file paths.
    """
    out_path = Path(output_dir).resolve()
    out_path.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for filename in DOC_FILENAMES:
        if filename in docs:
            target = out_path / filename
            target.write_text(docs[filename], encoding="utf-8", newline="\n")
            written.append(target)

    return written


def render_docs_from_file(spec_path: str | Path, output_dir: str | Path) -> list[Path]:
    """Load spec.json from disk and render all markdown documentation.

    Args:
        spec_path: Path to spec.json.
        output_dir: Directory where markdown files will be written.

    Returns:
        List of generated documentation file paths.
    """
    path = Path(spec_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"Specification file not found: {path}")

    with open(path, encoding="utf-8") as f:
        spec = json.load(f)

    docs = render_docs(spec)
    return write_docs(docs, output_dir)


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for render_docs."""
    parser = argparse.ArgumentParser(
        description="Render spec.json into 10 deterministic markdown documents."
    )
    parser.add_argument(
        "spec_file",
        nargs="?",
        default="spec/spec.json",
        help="Path to spec.json (default: 'spec/spec.json')",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="docs/spec",
        help="Target output directory (default: 'docs/spec')",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Print all rendered documents to stdout separated by delimiters",
    )

    args = parser.parse_args(argv)

    try:
        spec_file = Path(args.spec_file).resolve()
        if not spec_file.is_file():
            sys.stderr.write(f"Error: Specification file not found at '{spec_file}'\n")
            return 1

        with open(spec_file, encoding="utf-8") as f:
            spec = json.load(f)

        docs = render_docs(spec)

        if args.stdout:
            for fname in DOC_FILENAMES:
                if fname in docs:
                    sys.stdout.write(f"<!-- BEGIN: {fname} -->\n")
                    sys.stdout.write(docs[fname])
                    sys.stdout.write(f"\n<!-- END: {fname} -->\n\n")
            return 0

        written = write_docs(docs, args.output_dir)
        out_resolved = Path(args.output_dir).resolve()
        print(f"Rendered {len(written)} markdown specification files into: {out_resolved}")
        for p in written:
            print(f"  - {p.name}")
        return 0

    except Exception as err:
        sys.stderr.write(f"Documentation rendering failed: {err}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
