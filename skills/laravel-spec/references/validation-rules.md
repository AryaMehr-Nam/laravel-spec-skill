# Validation Rules Catalog (`scripts/validate_spec.py`)

This document is the comprehensive reference catalog for all 29 machine validation rules enforced by `skills/laravel-spec/scripts/validate_spec.py`. Every rule violation includes an actionable error message, file path pointer, and concrete fix hint.

---

## Rule Summary Matrix

| Rule ID | Severity | Category | Description |
| :--- | :--- | :--- | :--- |
| `STRUC_001` | ERROR | Structural | Root object or required top-level sections missing or malformed |
| `UNIQ_001` | ERROR | Uniqueness | Duplicate entity identifiers (roles, models, fields, panels, milestones) |
| `UNIQ_002` | ERROR | Uniqueness | Duplicate database table names across models |
| `REL_001` | ERROR | Relational | Target model in relationship does not exist in specification |
| `REL_002` | ERROR | Relational | Inverse relationship missing or mismatched on target model |
| `REL_003` | WARNING | Relational | Foreign key column missing `index: true` declaration |
| `REL_004` | ERROR | Relational | Foreign key column references non-existent model |
| `AUTH_001` | ERROR | Authorization | Policy ability grants access to undeclared role |
| `AUTH_002` | ERROR | Authorization | Filament resource model has no defined authorization policy |
| `AUTH_003` | ERROR | Authorization | Policy missing standard CRUD ability (`viewAny`, `view`, `create`, `update`, `delete`) |
| `AUTH_004` | ERROR | Authorization | Specification lacks a super-admin role with `is_super_admin: true` |
| `AUTH_005` | WARNING | Authorization | Declared role is unreferenced across all policies and panels |
| `AUTH_006` | ERROR | Authorization | Filament panel references undeclared role in `roles` array |
| `SM_001` | ERROR | State Machine | State machine field not declared in model's fields |
| `SM_002` | ERROR | State Machine | State machine lacks an initial state declaration |
| `SM_003` | ERROR | State Machine | Unreachable state detected (no incoming transitions and not initial) |
| `SM_004` | ERROR | State Machine | Dead-end state detected (non-terminal state with no outgoing transitions) |
| `SM_005` | ERROR | State Machine | State transition authorizes an undeclared role |
| `SM_006` | ERROR | State Machine | Terminal/final state erroneously defines outgoing transitions |
| `NUM_001` | ERROR | Financial | Prohibited float type on currency field or decimal missing scale >= 2 |
| `ENUM_001` | ERROR | Integrity | Field type `enum` is missing or has empty `enum_values` array |
| `DAG_001` | ERROR | Milestones | Circular dependency detected in milestone graph (Kahn's algorithm) |
| `DAG_002` | ERROR | Milestones | Milestone `depends_on` references a non-existent milestone ID |
| `DAG_003` | WARNING | Milestones | Model is declared but not included in any milestone scope |
| `DAG_004` | ERROR | Milestones | Milestone defines fewer than 2 verifiable acceptance criteria |
| `SEC_001` | ERROR | Security/PII | Field flagged with `pii: true` but `project.audit_log` is disabled |
| `SEC_002` | ERROR | Security | File upload column missing `max_size_kb` or `allowed_mimes` |
| `SEC_003` | ERROR | Security | Policy `ownership_field` does not exist on target model |
| `SEC_004` | ERROR | Security | Model with ownership scoping missing `query_scope` in Filament resource |

---

## Detailed Rule Catalog

### 1. Structural & Uniqueness Rules

#### `STRUC_001`: Root Structure & Required Top-Level Sections
- **Severity**: `ERROR`
- **Trigger**: Root of `spec.json` is not an object, is missing any required section (`project`, `roles`, `models`, `policies`, `filament`, `milestones`), or `project` lacks required properties (`name`, `description`, `locale`, `timezone`, `laravel_version`, `filament_version`).
- **Fix Hint**: Ensure `spec/spec.json` contains all required root keys and metadata fields.

#### `UNIQ_001`: Identifier Uniqueness
- **Severity**: `ERROR`
- **Trigger**: Duplicate names detected for roles, models, fields within a model, Filament panel IDs, or milestone IDs.
- **Fix Hint**: Rename or consolidate duplicate identifiers to ensure global or model-level uniqueness.

#### `UNIQ_002`: Database Table Uniqueness
- **Severity**: `ERROR`
- **Trigger**: Two or more models declare identical database `table` names.
- **Fix Hint**: Assign a unique table name (e.g. `users`, `products`, `orders`) to each model.

---

### 2. Relational Integrity Rules

#### `REL_001`: Target Relation Model Existence
- **Severity**: `ERROR`
- **Trigger**: A model relationship defines a `target` model name that does not exist in `models[]`.
- **Fix Hint**: Declare target model in `models[]` or correct typographical error in `target`.

#### `REL_002`: Inverse Relationship Reciprocity
- **Severity**: `ERROR`
- **Trigger**: A relationship defines an `inverse` relation method name, but the reciprocal relationship does not exist on the target model or points back to an incorrect model.
- **Fix Hint**: Add reciprocal relation on the target model (e.g. `belongsTo` paired with `hasMany`).

#### `REL_003`: Foreign Key Indexing
- **Severity**: `WARNING`
- **Trigger**: A foreign key column (e.g., ending in `_id`) does not have `"index": true`.
- **Fix Hint**: Add `"index": true` to foreign key fields in migration schemas for join performance.

#### `REL_004`: Foreign Key Model Reference
- **Severity**: `ERROR`
- **Trigger**: A foreign key column does not correspond to a valid declared model.
- **Fix Hint**: Verify that the entity referenced by the foreign key is declared in `models[]`.

---

### 3. Authorization & Roles Rules

#### `AUTH_001`: Policy Ability Role Reference
- **Severity**: `ERROR`
- **Trigger**: An ability in `policies[].abilities` permits a role not declared in `roles[]`.
- **Fix Hint**: Declare role in `roles[]` or remove invalid role slug from policy ability.

#### `AUTH_002`: Policy Coverage for Filament Resources
- **Severity**: `ERROR`
- **Trigger**: A Filament resource is declared for a model, but no policy exists for that model in `policies[]`.
- **Fix Hint**: Add authorization policy for the model in `policies[]` defining access rules.

#### `AUTH_003`: Standard CRUD Ability Completeness
- **Severity**: `ERROR`
- **Trigger**: A policy omits one of the standard Laravel abilities: `viewAny`, `view`, `create`, `update`, `delete`.
- **Fix Hint**: Define all 5 standard abilities in the policy dictionary.

#### `AUTH_004`: Super-Admin Role Declaration
- **Severity**: `ERROR`
- **Trigger**: No role in `roles[]` has `"is_super_admin": true`.
- **Fix Hint**: Designate at least one role with `"is_super_admin": true` (e.g. `super-admin`).

#### `AUTH_005`: Unreferenced Role Warning
- **Severity**: `WARNING`
- **Trigger**: A role declared in `roles[]` is never referenced in any policy ability or panel access list.
- **Fix Hint**: Reference role in policies/panels or remove unused role declaration.

#### `AUTH_006`: Filament Panel Role Reference
- **Severity**: `ERROR`
- **Trigger**: A Filament panel's `roles` array references a role not declared in `roles[]`.
- **Fix Hint**: Add missing role to `roles[]` or update panel access list.

---

### 4. State Machine Rules

#### `SM_001`: State Machine Field Existence
- **Severity**: `ERROR`
- **Trigger**: `model.state_machine.field` is not declared in the model's `fields[]`.
- **Fix Hint**: Add the state column (typically type `enum` or `string`) to the model's fields array.

#### `SM_002`: Initial State Declaration
- **Severity**: `ERROR`
- **Trigger**: State machine has no state marked `"initial": true`, or marks multiple initial states.
- **Fix Hint**: Designate exactly one starting state with `"initial": true`.

#### `SM_003`: Unreachable State Detection
- **Severity**: `ERROR`
- **Trigger**: A state is neither `initial: true` nor reachable via incoming transitions from any other state.
- **Fix Hint**: Add a transition leading to the unreachable state or remove the orphaned state.

#### `SM_004`: Dead-End State Detection
- **Severity**: `ERROR`
- **Trigger**: A state has no outgoing transitions (`"transitions": []`) but is not declared in `final_states`.
- **Fix Hint**: Add outgoing transitions or register state in `final_states`.

#### `SM_005`: Transition Role Authorization
- **Severity**: `ERROR`
- **Trigger**: A transition declares authorized `roles` containing an undeclared role.
- **Fix Hint**: Declare role in `roles[]` or correct role name in transition definition.

#### `SM_006`: Final State Outgoing Transitions
- **Severity**: `ERROR`
- **Trigger**: A state listed in `final_states` defines non-empty outgoing transitions.
- **Fix Hint**: Remove outgoing transitions from final terminal state (`"transitions": []`).

---

### 5. Financial & Data Integrity Rules

#### `NUM_001`: Float Currency Prohibition
- **Severity**: `ERROR`
- **Trigger**: A field with `"currency": true` uses type `float`, `double`, or `decimal` without `scale >= 2`.
- **Fix Hint**: Use `integer`/`bigInteger` minor units (e.g., `price_cents`) or `decimal` with explicit `precision` and `scale >= 2`.

```json
// BAD:
{"name": "total_price", "type": "float", "currency": true}

// GOOD:
{"name": "total_cents", "type": "bigInteger", "currency": true}
// OR:
{"name": "amount", "type": "decimal", "precision": 12, "scale": 2, "currency": true}
```

#### `ENUM_001`: Enum Values Declaration
- **Severity**: `ERROR`
- **Trigger**: A field with `"type": "enum"` is missing `enum_values` or defines an empty list.
- **Fix Hint**: Add `"enum_values": ["value1", "value2"]` to the field definition.

---

### 6. Milestone DAG Rules

#### `DAG_001`: Milestone Acyclic Graph Verification
- **Severity**: `ERROR`
- **Trigger**: Circular dependency cycle detected among milestones using Kahn's topological sort algorithm.
- **Fix Hint**: Re-order `depends_on` relationships so milestones form a directed acyclic graph.

#### `DAG_002`: Milestone Dependency Reference
- **Severity**: `ERROR`
- **Trigger**: A milestone's `depends_on` array references a non-existent milestone ID.
- **Fix Hint**: Ensure prerequisite milestone ID is declared in `milestones[]`.

#### `DAG_003`: Model Scope Coverage
- **Severity**: `WARNING`
- **Trigger**: A declared model is not listed in any milestone's `scope` array.
- **Fix Hint**: Assign model to a milestone scope (e.g. `scope: ["User", "Order"]`).

#### `DAG_004`: Milestone Acceptance Criteria Count
- **Severity**: `ERROR`
- **Trigger**: A milestone defines fewer than 2 acceptance criteria.
- **Fix Hint**: Provide at least 2 concrete, verifiable criteria per milestone.

---

### 7. Security, PII & Upload Rules

#### `SEC_001`: PII Audit Logging
- **Severity**: `ERROR`
- **Trigger**: A field has `"pii": true` (e.g. phone, national code, passport) but `project.audit_log` is false/missing.
- **Fix Hint**: Enable audit logging in `project` configuration: `"audit_log": true`.

#### `SEC_002`: File Upload Security Constraints
- **Severity**: `ERROR`
- **Trigger**: A file upload field lacks `"max_size_kb"` or `"allowed_mimes"`.
- **Fix Hint**: Define file safety bounds: `"max_size_kb": 5120` and `"allowed_mimes": ["image/jpeg", "image/png"]`.

#### `SEC_003`: Policy Ownership Field Verification
- **Severity**: `ERROR`
- **Trigger**: Policy declares an `ownership_field` that does not exist in the model's `fields[]`.
- **Fix Hint**: Add column to model `fields[]` (e.g. `user_id`) or remove `ownership_field` from policy.

#### `SEC_004`: Filament Ownership Query Scope
- **Severity**: `ERROR`
- **Trigger**: Model policy defines `ownership_field`, but the Filament resource lacks `"query_scope": true` or custom scope.
- **Fix Hint**: Add `"query_scope": true` to the Filament resource to ensure user/tenant isolation.
