# Workflows & Finite State Machines

This document defines lifecycle states, valid state transitions, and role permissions.

## State Machines Summary

| Model | State Column | Initial State | Final / Terminal States | Transitions |
| :--- | :--- | :--- | :--- | :--- |
| **Order** | `status` | `pending` | `delivered`, `cancelled` | 7 |
| **Payment** | `status` | `initiated` | `refunded`, `failed` | 5 |

## Transition Rules by Model

### `Order` Workflow (`status`)
- **Initial State**: `pending`
- **Final States**: `delivered`, `cancelled`

| Current State (From) | Next State (To) | Authorized Roles |
| :--- | :--- | :--- |
| `pending` | `paid` | `customer`, `super-admin` |
| `pending` | `cancelled` | `customer`, `super-admin` |
| `paid` | `processing` | `vendor`, `super-admin` |
| `processing` | `shipped` | `vendor`, `super-admin` |
| `shipped` | `delivered` | `vendor`, `customer`, `super-admin` |
| `paid` | `cancelled` | `super-admin` |
| `processing` | `cancelled` | `super-admin` |

### `Payment` Workflow (`status`)
- **Initial State**: `initiated`
- **Final States**: `refunded`, `failed`

| Current State (From) | Next State (To) | Authorized Roles |
| :--- | :--- | :--- |
| `initiated` | `redirected` | `customer`, `super-admin` |
| `initiated` | `failed` | `customer`, `super-admin` |
| `redirected` | `verified` | `*` |
| `redirected` | `failed` | `*` |
| `verified` | `refunded` | `super-admin` |
