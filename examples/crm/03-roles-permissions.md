# Roles, Permissions & Authorization Matrix

This document specifies system roles, policy abilities, and ownership scoping rules.

## Defined Roles

| Role | Super Administrator | Description |
| :--- | :--- | :--- |
| **super-admin** | Yes (Full Access) | System administrator with unrestricted configuration and access control privileges |
| **sales-manager** | No | Sales department leader overseeing pipeline health, quotas, and team performance |
| **sales-rep** | No | Individual account executive managing assigned contacts, accounts, and deals |

## Policy Authorization Matrix

### `User` Policy (`UserPolicy`)
- **Ownership Constraint**: `none`

| Ability | Authorized Roles | Ownership Scoped |
| :--- | :--- | :--- |
| `create` | `super-admin` | No |
| `delete` | `super-admin` | No |
| `update` | `super-admin`, `sales-manager` | No |
| `view` | `super-admin`, `sales-manager`, `sales-rep` | No |
| `viewAny` | `super-admin`, `sales-manager` | No |

### `Company` Policy (`CompanyPolicy`)
- **Ownership Constraint**: `owner_field:owner_id`

| Ability | Authorized Roles | Ownership Scoped |
| :--- | :--- | :--- |
| `create` | `sales-rep`, `sales-manager`, `super-admin` | No |
| `delete` | `sales-manager`, `super-admin` | Yes |
| `update` | `sales-rep`, `sales-manager`, `super-admin` | Yes |
| `view` | `sales-rep`, `sales-manager`, `super-admin` | Yes |
| `viewAny` | `sales-rep`, `sales-manager`, `super-admin` | No |

### `Contact` Policy (`ContactPolicy`)
- **Ownership Constraint**: `none`

| Ability | Authorized Roles | Ownership Scoped |
| :--- | :--- | :--- |
| `create` | `sales-rep`, `sales-manager`, `super-admin` | No |
| `delete` | `sales-manager`, `super-admin` | No |
| `update` | `sales-rep`, `sales-manager`, `super-admin` | No |
| `view` | `sales-rep`, `sales-manager`, `super-admin` | No |
| `viewAny` | `sales-rep`, `sales-manager`, `super-admin` | No |

### `Deal` Policy (`DealPolicy`)
- **Ownership Constraint**: `owner_field:owner_id`

| Ability | Authorized Roles | Ownership Scoped |
| :--- | :--- | :--- |
| `create` | `sales-rep`, `sales-manager`, `super-admin` | No |
| `delete` | `sales-manager`, `super-admin` | Yes |
| `update` | `sales-rep`, `sales-manager`, `super-admin` | Yes |
| `view` | `sales-rep`, `sales-manager`, `super-admin` | Yes |
| `viewAny` | `sales-rep`, `sales-manager`, `super-admin` | No |

### `Activity` Policy (`ActivityPolicy`)
- **Ownership Constraint**: `owner_field:assigned_to_id`

| Ability | Authorized Roles | Ownership Scoped |
| :--- | :--- | :--- |
| `create` | `sales-rep`, `sales-manager`, `super-admin` | No |
| `delete` | `sales-rep`, `sales-manager`, `super-admin` | Yes |
| `update` | `sales-rep`, `sales-manager`, `super-admin` | Yes |
| `view` | `sales-rep`, `sales-manager`, `super-admin` | Yes |
| `viewAny` | `sales-rep`, `sales-manager`, `super-admin` | No |

### `Note` Policy (`NotePolicy`)
- **Ownership Constraint**: `owner_field:author_id`

| Ability | Authorized Roles | Ownership Scoped |
| :--- | :--- | :--- |
| `create` | `sales-rep`, `sales-manager`, `super-admin` | No |
| `delete` | `sales-manager`, `super-admin` | Yes |
| `update` | `sales-rep`, `sales-manager`, `super-admin` | Yes |
| `view` | `sales-rep`, `sales-manager`, `super-admin` | Yes |
| `viewAny` | `sales-rep`, `sales-manager`, `super-admin` | No |

### `AuditLog` Policy (`AuditLogPolicy`)
- **Ownership Constraint**: `none`

| Ability | Authorized Roles | Ownership Scoped |
| :--- | :--- | :--- |
| `create` | `*` | No |
| `delete` | `super-admin` | No |
| `update` | `super-admin` | No |
| `view` | `super-admin` | No |
| `viewAny` | `super-admin` | No |
