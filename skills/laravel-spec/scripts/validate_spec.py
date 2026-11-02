"""Specification validator for Laravel and Filament applications.

Validates spec/spec.json against structural, relational, authorization,
state machine, financial precision, milestone DAG, and security rules.
Standard library only (Python 3.10+).
"""

from __future__ import annotations

import argparse
import json
from collections import deque
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class Severity(str, Enum):
    """Rule violation severity level."""

    ERROR = "error"
    WARNING = "warning"


@dataclass(frozen=True)
class RuleViolation:
    """Represents a single rule violation in a specification."""

    rule_id: str
    severity: Severity
    message: str
    path: str
    fix_hint: str

    def to_dict(self) -> dict[str, Any]:
        """Convert violation to dictionary format."""
        return {
            "rule_id": self.rule_id,
            "severity": self.severity.value,
            "message": self.message,
            "path": self.path,
            "fix_hint": self.fix_hint,
        }


@dataclass
class ValidationResult:
    """Aggregated result of specification validation."""

    is_valid: bool
    violations: list[RuleViolation]
    strict: bool = False

    @property
    def errors(self) -> list[RuleViolation]:
        """List all error-level violations."""
        return [v for v in self.violations if v.severity == Severity.ERROR]

    @property
    def warnings(self) -> list[RuleViolation]:
        """List all warning-level violations."""
        return [v for v in self.violations if v.severity == Severity.WARNING]

    @property
    def error_count(self) -> int:
        """Total number of errors."""
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        """Total number of warnings."""
        return len(self.warnings)

    def to_dict(self) -> dict[str, Any]:
        """Convert result to serializable dictionary."""
        return {
            "valid": self.is_valid,
            "strict": self.strict,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "errors": [v.to_dict() for v in self.errors],
            "warnings": [v.to_dict() for v in self.warnings],
        }


class SpecValidator:
    """Rule engine validating Laravel Filament application specifications."""

    CURRENCY_KEYWORDS = (
        "price",
        "amount",
        "cost",
        "balance",
        "fee",
        "salary",
        "total",
        "tax",
        "subtotal",
        "wage",
        "budget",
        "discount",
    )

    STANDARD_ABILITIES = ("viewAny", "view", "create", "update", "delete")

    def __init__(self, spec: dict[str, Any], strict: bool = False) -> None:
        self.spec = spec
        self.strict = strict
        self.violations: list[RuleViolation] = []

    def validate(self) -> ValidationResult:
        """Execute all validation passes and return aggregated result."""
        self.violations.clear()

        # Step 1: Structural check
        if not self._validate_structure():
            return self._build_result()

        # Step 2: Uniqueness checks
        self._validate_uniqueness()

        # Step 3: Relational integrity
        self._validate_relations()

        # Step 4: Authorization and policies
        self._validate_auth()

        # Step 5: State machines
        self._validate_state_machines()

        # Step 6: Numbers and financial precision
        self._validate_numbers_and_currency()

        # Step 7: Milestone acyclic DAG
        self._validate_milestones_dag()

        # Step 8: Security, PII, uploads, and ownership
        self._validate_security()

        return self._build_result()

    def _add_violation(
        self,
        rule_id: str,
        severity: Severity,
        message: str,
        path: str,
        fix_hint: str,
    ) -> None:
        self.violations.append(
            RuleViolation(
                rule_id=rule_id,
                severity=severity,
                message=message,
                path=path,
                fix_hint=fix_hint,
            )
        )

    def _build_result(self) -> ValidationResult:
        error_count = sum(1 for v in self.violations if v.severity == Severity.ERROR)
        warning_count = sum(1 for v in self.violations if v.severity == Severity.WARNING)

        if self.strict:
            is_valid = error_count == 0 and warning_count == 0
        else:
            is_valid = error_count == 0

        return ValidationResult(
            is_valid=is_valid,
            violations=list(self.violations),
            strict=self.strict,
        )

    # -------------------------------------------------------------------------
    # Rule Pass 1: Structure (STRUC_001)
    # -------------------------------------------------------------------------
    def _validate_structure(self) -> bool:
        required_top_level = ["project", "roles", "models", "policies", "filament", "milestones"]
        missing = [key for key in required_top_level if key not in self.spec]
        if missing:
            for key in missing:
                self._add_violation(
                    rule_id="STRUC_001",
                    severity=Severity.ERROR,
                    message=f"Missing required top-level section: '{key}'.",
                    path=f"spec.{key}",
                    fix_hint=f"Define the '{key}' section at the root of spec.json.",
                )
            return False

        project = self.spec.get("project")
        if not isinstance(project, dict):
            self._add_violation(
                rule_id="STRUC_001",
                severity=Severity.ERROR,
                message="Top-level 'project' must be an object.",
                path="spec.project",
                fix_hint="Define 'project' as an object containing project metadata.",
            )
            return False

        proj_required = [
            "name",
            "description",
            "locale",
            "timezone",
            "laravel_version",
            "filament_version",
        ]
        for field in proj_required:
            if field not in project:
                self._add_violation(
                    rule_id="STRUC_001",
                    severity=Severity.ERROR,
                    message=f"Project section missing required property: '{field}'.",
                    path=f"spec.project.{field}",
                    fix_hint=f"Specify '{field}' in project configuration.",
                )

        filament = self.spec.get("filament")
        if not isinstance(filament, dict) or "panels" not in filament:
            self._add_violation(
                rule_id="STRUC_001",
                severity=Severity.ERROR,
                message="Section 'filament' must contain a 'panels' array.",
                path="spec.filament.panels",
                fix_hint="Add 'panels: []' inside the filament section.",
            )
            return False

        return True

    # -------------------------------------------------------------------------
    # Rule Pass 2: Uniqueness (UNIQ_001, UNIQ_002)
    # -------------------------------------------------------------------------
    def _validate_uniqueness(self) -> None:
        seen_roles: set[str] = set()
        for idx, role in enumerate(self.spec.get("roles", [])):
            name = role.get("name")
            if name in seen_roles:
                self._add_violation(
                    rule_id="UNIQ_001",
                    severity=Severity.ERROR,
                    message=f"Duplicate role name '{name}'.",
                    path=f"roles[{idx}].name",
                    fix_hint=f"Rename or remove duplicate role '{name}'.",
                )
            elif name:
                seen_roles.add(name)

        seen_models: set[str] = set()
        seen_tables: dict[str, str] = {}
        for idx, model in enumerate(self.spec.get("models", [])):
            mname = model.get("name")
            if mname in seen_models:
                self._add_violation(
                    rule_id="UNIQ_001",
                    severity=Severity.ERROR,
                    message=f"Duplicate model name '{mname}'.",
                    path=f"models[{idx}].name",
                    fix_hint=f"Rename or remove duplicate model '{mname}'.",
                )
            elif mname:
                seen_models.add(mname)

            table = model.get("table")
            if table:
                if table in seen_tables:
                    self._add_violation(
                        rule_id="UNIQ_002",
                        severity=Severity.ERROR,
                        message=(
                            f"Duplicate database table '{table}' shared by models "
                            f"'{seen_tables[table]}' and '{mname}'."
                        ),
                        path=f"models[{idx}].table",
                        fix_hint=(
                            f"Assign distinct tables to '{seen_tables[table]}' and '{mname}'."
                        ),
                    )
                else:
                    seen_tables[table] = mname or f"models[{idx}]"

            seen_fields: set[str] = set()
            for fidx, field in enumerate(model.get("fields", [])):
                fname = field.get("name")
                if fname in seen_fields:
                    self._add_violation(
                        rule_id="UNIQ_001",
                        severity=Severity.ERROR,
                        message=f"Duplicate field name '{fname}' in model '{mname}'.",
                        path=f"models[{idx}].fields[{fidx}].name",
                        fix_hint=f"Rename or remove duplicate field '{fname}' in model '{mname}'.",
                    )
                elif fname:
                    seen_fields.add(fname)

        seen_panels: set[str] = set()
        for pidx, panel in enumerate(self.spec.get("filament", {}).get("panels", [])):
            pid = panel.get("id")
            if pid in seen_panels:
                self._add_violation(
                    rule_id="UNIQ_001",
                    severity=Severity.ERROR,
                    message=f"Duplicate Filament panel ID '{pid}'.",
                    path=f"filament.panels[{pidx}].id",
                    fix_hint=f"Assign a unique ID to Filament panel '{pid}'.",
                )
            elif pid:
                seen_panels.add(pid)

        seen_milestones: set[str] = set()
        for midx, ms in enumerate(self.spec.get("milestones", [])):
            mid = ms.get("id")
            if mid in seen_milestones:
                self._add_violation(
                    rule_id="UNIQ_001",
                    severity=Severity.ERROR,
                    message=f"Duplicate milestone ID '{mid}'.",
                    path=f"milestones[{midx}].id",
                    fix_hint="Ensure each milestone has a unique ID (e.g. M0, M1, M2).",
                )
            elif mid:
                seen_milestones.add(mid)

    # -------------------------------------------------------------------------
    # Rule Pass 3: Relational Integrity (REL_001, REL_002, REL_003, REL_004)
    # -------------------------------------------------------------------------
    def _validate_relations(self) -> None:
        models = self.spec.get("models", [])
        model_names = {m.get("name") for m in models if m.get("name")}
        model_map = {m.get("name"): m for m in models if m.get("name")}

        for midx, model in enumerate(models):
            mname = model.get("name", f"Model_{midx}")

            for ridx, rel in enumerate(model.get("relations", [])):
                target = rel.get("model")
                rel_name = rel.get("name", f"rel_{ridx}")

                if target not in model_names:
                    self._add_violation(
                        rule_id="REL_001",
                        severity=Severity.ERROR,
                        message=(
                            f"Relation '{rel_name}' on model '{mname}' references "
                            f"non-existent target model '{target}'."
                        ),
                        path=f"models[{midx}].relations[{ridx}].model",
                        fix_hint=(
                            f"Declare model '{target}' in models array or update relation target."
                        ),
                    )
                else:
                    inverse = rel.get("inverse")
                    if inverse:
                        target_model = model_map[target]
                        target_rels = {r.get("name") for r in target_model.get("relations", [])}
                        if inverse not in target_rels:
                            self._add_violation(
                                rule_id="REL_002",
                                severity=Severity.ERROR,
                                message=(
                                    f"Inverse relation '{inverse}' on '{mname}.{rel_name}' "
                                    f"not found on model '{target}'."
                                ),
                                path=f"models[{midx}].relations[{ridx}].inverse",
                                fix_hint=(
                                    f"Define relation '{inverse}' on model '{target}' "
                                    f"targeting '{mname}'."
                                ),
                            )

            for fidx, field in enumerate(model.get("fields", [])):
                fname = field.get("name", f"field_{fidx}")
                foreign = field.get("foreign")

                if isinstance(foreign, dict):
                    f_target = foreign.get("model")
                    if f_target not in model_names:
                        self._add_violation(
                            rule_id="REL_004",
                            severity=Severity.ERROR,
                            message=(
                                f"Foreign key on field '{fname}' in model '{mname}' "
                                f"references non-existent model '{f_target}'."
                            ),
                            path=f"models[{midx}].fields[{fidx}].foreign.model",
                            fix_hint=(
                                f"Declare model '{f_target}' in models or update foreign key model."
                            ),
                        )

                    has_index = field.get("index") is True or field.get("unique") is True
                    if not has_index:
                        self._add_violation(
                            rule_id="REL_003",
                            severity=Severity.WARNING,
                            message=(
                                f"Foreign key field '{fname}' in model '{mname}' lacks an index."
                            ),
                            path=f"models[{midx}].fields[{fidx}]",
                            fix_hint=(
                                f"Add 'index: true' to foreign key field '{fname}' in model "
                                f"'{mname}'."
                            ),
                        )

    # -------------------------------------------------------------------------
    # Rule Pass 4: Authorization and Policies (AUTH_001 .. AUTH_006)
    # -------------------------------------------------------------------------
    def _validate_auth(self) -> None:
        roles = self.spec.get("roles", [])
        declared_roles = {r.get("name") for r in roles if r.get("name")}
        super_admin_roles = {r.get("name") for r in roles if r.get("is_super_admin") is True}

        if not super_admin_roles:
            self._add_violation(
                rule_id="AUTH_004",
                severity=Severity.ERROR,
                message="No super-admin role declared with 'is_super_admin: true'.",
                path="roles",
                fix_hint=(
                    "Declare at least one role with 'is_super_admin: true' to ensure "
                    "administrative system access."
                ),
            )

        referenced_roles: set[str] = set()

        policies = self.spec.get("policies", [])
        policy_models = {p.get("model") for p in policies if p.get("model")}

        for pidx, policy in enumerate(policies):
            pmodel = policy.get("model", f"policy_{pidx}")
            abilities = policy.get("abilities", {})

            for ability in self.STANDARD_ABILITIES:
                if ability not in abilities:
                    self._add_violation(
                        rule_id="AUTH_003",
                        severity=Severity.ERROR,
                        message=(
                            f"Policy for model '{pmodel}' missing standard ability '{ability}'."
                        ),
                        path=f"policies[{pidx}].abilities.{ability}",
                        fix_hint=(
                            f"Add ability '{ability}' to policy for model '{pmodel}' specifying "
                            "authorized roles."
                        ),
                    )

            for ab_name, ab_roles in abilities.items():
                if isinstance(ab_roles, list):
                    for r in ab_roles:
                        referenced_roles.add(r)
                        if r not in declared_roles and r != "*":
                            self._add_violation(
                                rule_id="AUTH_001",
                                severity=Severity.ERROR,
                                message=(
                                    f"Policy for model '{pmodel}' ability '{ab_name}' "
                                    f"references undeclared role '{r}'."
                                ),
                                path=f"policies[{pidx}].abilities.{ab_name}",
                                fix_hint=(
                                    f"Declare role '{r}' in roles array or remove it from "
                                    f"ability '{ab_name}'."
                                ),
                            )

        panels = self.spec.get("filament", {}).get("panels", [])
        for pidx, panel in enumerate(panels):
            pid = panel.get("id", f"panel_{pidx}")

            for r in panel.get("roles", []):
                referenced_roles.add(r)
                if r not in declared_roles and r != "*":
                    self._add_violation(
                        rule_id="AUTH_006",
                        severity=Severity.ERROR,
                        message=(
                            f"Filament panel '{pid}' references undeclared role '{r}'."
                        ),
                        path=f"filament.panels[{pidx}].roles",
                        fix_hint=(
                            f"Declare role '{r}' in roles array or remove it from panel '{pid}'."
                        ),
                    )

            for res_idx, res in enumerate(panel.get("resources", [])):
                rmodel = res.get("model")
                if rmodel and rmodel not in policy_models:
                    self._add_violation(
                        rule_id="AUTH_002",
                        severity=Severity.ERROR,
                        message=(
                            f"Filament resource for model '{rmodel}' in panel '{pid}' has no "
                            "corresponding policy in policies."
                        ),
                        path=f"filament.panels[{pidx}].resources[{res_idx}].model",
                        fix_hint=(
                            f"Define an authorization policy for model '{rmodel}' in policies."
                        ),
                    )

        for model in self.spec.get("models", []):
            states = model.get("states")
            if isinstance(states, dict):
                for t in states.get("transitions", []):
                    for r in t.get("roles", []):
                        referenced_roles.add(r)

        for ridx, role in enumerate(roles):
            rname = role.get("name")
            if rname and not role.get("is_super_admin"):
                if rname not in referenced_roles:
                    self._add_violation(
                        rule_id="AUTH_005",
                        severity=Severity.WARNING,
                        message=(
                            f"Role '{rname}' is declared but never referenced in any policy, "
                            "panel, or state machine transition."
                        ),
                        path=f"roles[{ridx}]",
                        fix_hint=(
                            f"Assign role '{rname}' to policy abilities, panels, or transitions, "
                            "or remove it if unused."
                        ),
                    )

    # -------------------------------------------------------------------------
    # Rule Pass 5: State Machines (SM_001 .. SM_006)
    # -------------------------------------------------------------------------
    def _validate_state_machines(self) -> None:
        declared_roles = {r.get("name") for r in self.spec.get("roles", []) if r.get("name")}

        for midx, model in enumerate(self.spec.get("models", [])):
            mname = model.get("name", f"Model_{midx}")
            states = model.get("states")
            if not isinstance(states, dict):
                continue

            field_name = states.get("field")
            model_fields = {f.get("name") for f in model.get("fields", []) if f.get("name")}

            if field_name not in model_fields:
                self._add_violation(
                    rule_id="SM_001",
                    severity=Severity.ERROR,
                    message=(
                        f"State machine field '{field_name}' not found in model '{mname}'."
                    ),
                    path=f"models[{midx}].states.field",
                    fix_hint=(
                        f"Add field '{field_name}' to fields array of model '{mname}'."
                    ),
                )

            initial = states.get("initial")
            finals = set(states.get("final", []))
            transitions = states.get("transitions", [])

            all_states: set[str] = set()
            if initial:
                all_states.add(initial)
            all_states.update(finals)

            for tidx, trans in enumerate(transitions):
                from_s = trans.get("from")
                to_s = trans.get("to")
                if from_s and from_s != "*":
                    all_states.add(from_s)
                if to_s:
                    all_states.add(to_s)

                for r in trans.get("roles", []):
                    if r not in declared_roles and r != "*":
                        self._add_violation(
                            rule_id="SM_005",
                            severity=Severity.ERROR,
                            message=(
                                f"State transition ({from_s} -> {to_s}) on model '{mname}' "
                                f"references undeclared role '{r}'."
                            ),
                            path=f"models[{midx}].states.transitions[{tidx}].roles",
                            fix_hint=(
                                f"Declare role '{r}' in roles or remove it from transition roles."
                            ),
                        )

            if initial:
                has_initial_outgoing = any(
                    t.get("from") in (initial, "*") for t in transitions
                )
                if not has_initial_outgoing and all_states != {initial}:
                    self._add_violation(
                        rule_id="SM_002",
                        severity=Severity.ERROR,
                        message=(
                            f"Initial state '{initial}' on model '{mname}' has no "
                            "outgoing transitions."
                        ),
                        path=f"models[{midx}].states.initial",
                        fix_hint=(
                            f"Add a transition with 'from: \"{initial}\"' to enable progress "
                            "from initial state."
                        ),
                    )

            if initial:
                reachable: set[str] = {initial}
                changed = True
                while changed:
                    changed = False
                    for trans in transitions:
                        f = trans.get("from")
                        t = trans.get("to")
                        if (f == "*" or f in reachable) and t and t not in reachable:
                            reachable.add(t)
                            changed = True

                unreachable = all_states - reachable
                for u_state in sorted(unreachable):
                    self._add_violation(
                        rule_id="SM_003",
                        severity=Severity.ERROR,
                        message=(
                            f"State '{u_state}' on model '{mname}' is unreachable from initial "
                            f"state '{initial}'."
                        ),
                        path=f"models[{midx}].states",
                        fix_hint=(
                            f"Add a transition leading to state '{u_state}' or remove it."
                        ),
                    )

            for state in sorted(all_states):
                if state not in finals:
                    has_outgoing = any(
                        t.get("from") in (state, "*") for t in transitions
                    )
                    if not has_outgoing:
                        self._add_violation(
                            rule_id="SM_004",
                            severity=Severity.ERROR,
                            message=(
                                f"Non-terminal state '{state}' on model '{mname}' has no outgoing "
                                "transitions."
                            ),
                            path=f"models[{midx}].states",
                            fix_hint=(
                                f"Add outgoing transitions from state '{state}' or add it to "
                                "'states.final' array."
                            ),
                        )

            for final_state in finals:
                for tidx, trans in enumerate(transitions):
                    if trans.get("from") == final_state:
                        self._add_violation(
                            rule_id="SM_006",
                            severity=Severity.ERROR,
                            message=(
                                f"Final state '{final_state}' on model '{mname}' has an outgoing "
                                f"transition to '{trans.get('to')}'."
                            ),
                            path=f"models[{midx}].states.transitions[{tidx}]",
                            fix_hint=(
                                f"Remove outgoing transitions from final state '{final_state}' or "
                                "remove it from 'states.final'."
                            ),
                        )

    # -------------------------------------------------------------------------
    # Rule Pass 6: Numbers and Currency (NUM_001)
    # -------------------------------------------------------------------------
    def _validate_numbers_and_currency(self) -> None:
        for midx, model in enumerate(self.spec.get("models", [])):
            mname = model.get("name", f"Model_{midx}")
            for fidx, field in enumerate(model.get("fields", [])):
                fname = field.get("name", "").lower()
                ftype = field.get("type", "").lower()
                is_monetary = (
                    any(kw in fname for kw in self.CURRENCY_KEYWORDS)
                    or field.get("monetary") is True
                    or field.get("currency") is True
                )

                if is_monetary:
                    if ftype in ("float", "double"):
                        self._add_violation(
                            rule_id="NUM_001",
                            severity=Severity.ERROR,
                            message=(
                                f"Currency field '{field.get('name')}' on model '{mname}' "
                                f"uses forbidden floating-point type '{ftype}'."
                            ),
                            path=f"models[{midx}].fields[{fidx}].type",
                            fix_hint=(
                                f"Change type of '{field.get('name')}' to 'integer' or 'decimal' "
                                "with explicit precision and scale."
                            ),
                        )
                    elif ftype == "decimal":
                        precision = field.get("precision")
                        scale = field.get("scale")
                        if precision is None or scale is None:
                            self._add_violation(
                                rule_id="NUM_001",
                                severity=Severity.ERROR,
                                message=(
                                    f"Decimal currency field '{field.get('name')}' on model "
                                    f"'{mname}' missing explicit precision or scale."
                                ),
                                path=f"models[{midx}].fields[{fidx}]",
                                fix_hint=(
                                    f"Define 'precision' (e.g. 12) and 'scale' (e.g. 2) for "
                                    f"field '{field.get('name')}'."
                                ),
                            )

    # -------------------------------------------------------------------------
    # Rule Pass 7: Milestone Acyclic DAG (DAG_001 .. DAG_004)
    # -------------------------------------------------------------------------
    def _validate_milestones_dag(self) -> None:
        milestones = self.spec.get("milestones", [])
        ms_ids = {m.get("id") for m in milestones if m.get("id")}

        in_degrees: dict[str, int] = {mid: 0 for mid in ms_ids}
        adj: dict[str, list[str]] = {mid: [] for mid in ms_ids}

        for midx, ms in enumerate(milestones):
            mid = ms.get("id", f"MS_{midx}")

            acceptance = ms.get("acceptance", [])
            if not isinstance(acceptance, list) or len(acceptance) < 2:
                count = len(acceptance) if isinstance(acceptance, list) else 0
                self._add_violation(
                    rule_id="DAG_004",
                    severity=Severity.ERROR,
                    message=(
                        f"Milestone '{mid}' specifies {count} acceptance criteria (min 2 required)."
                    ),
                    path=f"milestones[{midx}].acceptance",
                    fix_hint=(
                        f"Define at least 2 observable acceptance criteria for milestone '{mid}'."
                    ),
                )

            for dep in ms.get("depends_on", []):
                if dep not in ms_ids:
                    self._add_violation(
                        rule_id="DAG_002",
                        severity=Severity.ERROR,
                        message=(
                            f"Milestone '{mid}' depends on non-existent milestone '{dep}'."
                        ),
                        path=f"milestones[{midx}].depends_on",
                        fix_hint=(
                            f"Declare milestone '{dep}' in milestones array or remove it from "
                            f"'{mid}.depends_on'."
                        ),
                    )
                else:
                    in_degrees[mid] = in_degrees.get(mid, 0) + 1
                    adj[dep].append(mid)

        queue: deque[str] = deque([mid for mid, deg in in_degrees.items() if deg == 0])
        processed_count = 0

        while queue:
            node = queue.popleft()
            processed_count += 1
            for neighbor in adj.get(node, []):
                in_degrees[neighbor] -= 1
                if in_degrees[neighbor] == 0:
                    queue.append(neighbor)

        if processed_count < len(ms_ids):
            cycle_nodes = [mid for mid, deg in in_degrees.items() if deg > 0]
            self._add_violation(
                rule_id="DAG_001",
                severity=Severity.ERROR,
                message=(
                    f"Circular dependency detected in milestones DAG involving: "
                    f"{', '.join(sorted(cycle_nodes))}."
                ),
                path="milestones",
                fix_hint=(
                    "Restructure milestone depends_on chains to ensure an acyclic graph."
                ),
            )

        scoped_entities: set[str] = set()
        for ms in milestones:
            for s in ms.get("scope", []):
                scoped_entities.add(s)

        for midx, model in enumerate(self.spec.get("models", [])):
            mname = model.get("name")
            if mname and mname not in scoped_entities:
                self._add_violation(
                    rule_id="DAG_003",
                    severity=Severity.WARNING,
                    message=(
                        f"Model '{mname}' is not covered in the scope of any milestone."
                    ),
                    path=f"models[{midx}]",
                    fix_hint=(
                        f"Add model '{mname}' to the 'scope' array of the milestone "
                        "where it is created."
                    ),
                )

    # -------------------------------------------------------------------------
    # Rule Pass 8: Security, PII, Uploads, Ownership (SEC_001 .. SEC_004)
    # -------------------------------------------------------------------------
    def _validate_security(self) -> None:
        models = self.spec.get("models", [])
        model_map = {m.get("name"): m for m in models if m.get("name")}

        audit_log = self.spec.get("project", {}).get("audit_log")
        has_audit_integration = any(
            integ.get("kind") in ("audit", "audit_log")
            or integ.get("name") in ("audit", "audit_log", "activity_log")
            for integ in self.spec.get("integrations", [])
        )
        audit_enabled = bool(audit_log) or has_audit_integration

        pii_fields: list[tuple[str, str]] = []
        for midx, model in enumerate(models):
            mname = model.get("name", f"Model_{midx}")
            for fidx, field in enumerate(model.get("fields", [])):
                fname = field.get("name", f"field_{fidx}")
                if field.get("pii") is True:
                    pii_fields.append((mname, fname))

                ftype = field.get("type")
                if ftype in ("file", "image"):
                    max_size = field.get("max_size_kb")
                    allowed_mimes = field.get("allowed_mimes")
                    is_valid_size = isinstance(max_size, int) and max_size > 0
                    is_valid_mimes = isinstance(allowed_mimes, list) and len(allowed_mimes) > 0

                    if not is_valid_size or not is_valid_mimes:
                        self._add_violation(
                            rule_id="SEC_002",
                            severity=Severity.ERROR,
                            message=(
                                f"Upload column '{fname}' on model '{mname}' missing "
                                "'max_size_kb' (>0) or 'allowed_mimes' list."
                            ),
                            path=f"models[{midx}].fields[{fidx}]",
                            fix_hint=(
                                f"Specify 'max_size_kb: 5120' and "
                                f"'allowed_mimes: [\"image/jpeg\"]' on field '{fname}'."
                            ),
                        )

        if pii_fields and not audit_enabled:
            for mname, fname in pii_fields:
                self._add_violation(
                    rule_id="SEC_001",
                    severity=Severity.ERROR,
                    message=(
                        f"Field '{fname}' on model '{mname}' is marked as PII, but audit logging "
                        "is not enabled."
                    ),
                    path=f"models.{mname}.fields.{fname}",
                    fix_hint=(
                        "Set 'project.audit_log: true' or configure an audit integration in "
                        "the integrations array."
                    ),
                )

        policies = self.spec.get("policies", [])
        panels = self.spec.get("filament", {}).get("panels", [])

        for pidx, policy in enumerate(policies):
            pmodel = policy.get("model")
            ownership = policy.get("ownership", "none")

            if ownership.startswith("owner_field:"):
                owner_field = ownership.split(":", 1)[1]
                target_model = model_map.get(pmodel)
                if target_model:
                    m_fields = {f.get("name") for f in target_model.get("fields", [])}
                    if owner_field not in m_fields:
                        self._add_violation(
                            rule_id="SEC_003",
                            severity=Severity.ERROR,
                            message=(
                                f"Policy for model '{pmodel}' specifies ownership '{ownership}', "
                                f"but field '{owner_field}' does not exist on model '{pmodel}'."
                            ),
                            path=f"policies[{pidx}].ownership",
                            fix_hint=(
                                f"Add field '{owner_field}' to model '{pmodel}' or "
                                "update policy ownership."
                            ),
                        )

            if ownership not in ("none", ""):
                for panel in panels:
                    for res_idx, res in enumerate(panel.get("resources", [])):
                        if res.get("model") == pmodel:
                            table = res.get("table")
                            has_scope = False
                            if isinstance(table, dict):
                                if (
                                    table.get("scope")
                                    or table.get("query_scope")
                                    or table.get("ownership_scope")
                                    or table.get("scoped")
                                ):
                                    has_scope = True
                            if not has_scope:
                                self._add_violation(
                                    rule_id="SEC_004",
                                    severity=Severity.ERROR,
                                    message=(
                                        f"Filament resource for model '{pmodel}' in panel "
                                        f"'{panel.get('id')}' lacks query scoping for "
                                        f"ownership '{ownership}'."
                                    ),
                                    path=f"filament.panels.resources[{res_idx}].table",
                                    fix_hint=(
                                        f"Add query scoping (e.g. 'table.query_scope') "
                                        f"to resource table in panel '{panel.get('id')}'."
                                    ),
                                )


def validate_spec(spec: dict[str, Any], strict: bool = False) -> ValidationResult:
    """Validate specification dictionary."""
    validator = SpecValidator(spec, strict=strict)
    return validator.validate()


def validate_spec_file(path: str | Path, strict: bool = False) -> ValidationResult:
    """Load specification file and validate."""
    file_path = Path(path)
    if not file_path.exists():
        violation = RuleViolation(
            rule_id="STRUC_001",
            severity=Severity.ERROR,
            message=f"Specification file not found: {file_path}",
            path=str(file_path),
            fix_hint="Provide a valid path to an existing spec.json file.",
        )
        return ValidationResult(is_valid=False, violations=[violation], strict=strict)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        violation = RuleViolation(
            rule_id="STRUC_001",
            severity=Severity.ERROR,
            message=f"Malformed JSON in specification: {e}",
            path=str(file_path),
            fix_hint="Ensure the specification file is valid JSON syntax.",
        )
        return ValidationResult(is_valid=False, violations=[violation], strict=strict)

    return validate_spec(data, strict=strict)


def format_cli_output(result: ValidationResult) -> str:
    """Format human-readable CLI report."""
    lines: list[str] = []

    if result.is_valid:
        lines.append("PASS: Specification is valid and adheres to all architecture rules.")
        if result.warning_count > 0:
            lines.append(f"\nNotice: {result.warning_count} warning(s) observed:")
            for w in result.warnings:
                lines.append(f"  [{w.rule_id}] {w.message} (path: {w.path})")
                lines.append(f"    Fix: {w.fix_hint}")
        return "\n".join(lines)

    lines.append("FAIL: Specification validation failed.")
    lines.append(
        f"Summary: {result.error_count} error(s), {result.warning_count} warning(s) found."
    )

    if result.errors:
        lines.append("\nErrors:")
        for err in result.errors:
            lines.append(f"  [{err.rule_id}] {err.message}")
            lines.append(f"    Path: {err.path}")
            lines.append(f"    Fix:  {err.fix_hint}")

    if result.warnings:
        lines.append("\nWarnings:")
        for warn in result.warnings:
            lines.append(f"  [{warn.rule_id}] {warn.message}")
            lines.append(f"    Path: {warn.path}")
            lines.append(f"    Fix:  {warn.fix_hint}")

    return "\n".join(lines)


def main() -> int:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(
        description="Validate Laravel Filament specification (spec.json)."
    )
    parser.add_argument("spec", help="Path to spec.json file")
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Output validation results as JSON",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (fail on any warning)",
    )

    args = parser.parse_args()

    result = validate_spec_file(args.spec, strict=args.strict)

    if args.json_output:
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print(format_cli_output(result))

    return 0 if result.is_valid else 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
