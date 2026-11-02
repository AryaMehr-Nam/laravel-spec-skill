# Roles, Permissions & Authorization Matrix

This document specifies system roles, policy abilities, and ownership scoping rules.

## Defined Roles

| Role | Super Administrator | Description |
| :--- | :--- | :--- |
| **super-admin** | Yes (Full Access) | System administrator with unrestricted platform oversight |
| **vendor** | No | Registered merchant managing catalog, store profile, and order fulfillments |
| **customer** | No | Authenticated buyer purchasing products, tracking orders, and submitting reviews |

## Policy Authorization Matrix

### `User` Policy (`UserPolicy`)
- **Ownership Constraint**: `none`

| Ability | Authorized Roles | Ownership Scoped |
| :--- | :--- | :--- |
| `create` | `*` | No |
| `delete` | `super-admin` | No |
| `update` | `super-admin`, `customer` | No |
| `view` | `super-admin`, `vendor`, `customer` | No |
| `viewAny` | `super-admin` | No |

### `VendorProfile` Policy (`VendorProfilePolicy`)
- **Ownership Constraint**: `owner_field:user_id`

| Ability | Authorized Roles | Ownership Scoped |
| :--- | :--- | :--- |
| `create` | `vendor`, `super-admin` | No |
| `delete` | `super-admin` | Yes |
| `update` | `vendor`, `super-admin` | Yes |
| `view` | `super-admin`, `vendor`, `customer` | Yes |
| `viewAny` | `super-admin`, `vendor` | No |

### `Category` Policy (`CategoryPolicy`)
- **Ownership Constraint**: `none`

| Ability | Authorized Roles | Ownership Scoped |
| :--- | :--- | :--- |
| `create` | `super-admin` | No |
| `delete` | `super-admin` | No |
| `update` | `super-admin` | No |
| `view` | `*` | No |
| `viewAny` | `*` | No |

### `Product` Policy (`ProductPolicy`)
- **Ownership Constraint**: `owner_field:vendor_id`

| Ability | Authorized Roles | Ownership Scoped |
| :--- | :--- | :--- |
| `create` | `vendor`, `super-admin` | No |
| `delete` | `vendor`, `super-admin` | Yes |
| `update` | `vendor`, `super-admin` | Yes |
| `view` | `vendor`, `super-admin`, `customer` | Yes |
| `viewAny` | `vendor`, `super-admin`, `customer` | No |

### `Order` Policy (`OrderPolicy`)
- **Ownership Constraint**: `owner_field:customer_id`

| Ability | Authorized Roles | Ownership Scoped |
| :--- | :--- | :--- |
| `create` | `customer`, `super-admin` | No |
| `delete` | `super-admin` | Yes |
| `update` | `vendor`, `super-admin` | Yes |
| `view` | `customer`, `vendor`, `super-admin` | Yes |
| `viewAny` | `customer`, `vendor`, `super-admin` | No |

### `OrderItem` Policy (`OrderItemPolicy`)
- **Ownership Constraint**: `none`

| Ability | Authorized Roles | Ownership Scoped |
| :--- | :--- | :--- |
| `create` | `customer`, `super-admin` | No |
| `delete` | `super-admin` | No |
| `update` | `super-admin` | No |
| `view` | `vendor`, `customer`, `super-admin` | No |
| `viewAny` | `vendor`, `customer`, `super-admin` | No |

### `Payment` Policy (`PaymentPolicy`)
- **Ownership Constraint**: `owner_field:user_id`

| Ability | Authorized Roles | Ownership Scoped |
| :--- | :--- | :--- |
| `create` | `customer`, `super-admin` | No |
| `delete` | `super-admin` | Yes |
| `update` | `super-admin` | Yes |
| `view` | `customer`, `super-admin` | Yes |
| `viewAny` | `customer`, `super-admin` | No |

### `Review` Policy (`ReviewPolicy`)
- **Ownership Constraint**: `owner_field:customer_id`

| Ability | Authorized Roles | Ownership Scoped |
| :--- | :--- | :--- |
| `create` | `customer` | No |
| `delete` | `super-admin` | Yes |
| `update` | `customer`, `super-admin` | Yes |
| `view` | `*` | Yes |
| `viewAny` | `*` | No |
