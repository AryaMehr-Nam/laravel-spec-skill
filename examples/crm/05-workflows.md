# Workflows & Finite State Machines

This document defines lifecycle states, valid state transitions, and role permissions.

## State Machines Summary

| Model | State Column | Initial State | Final / Terminal States | Transitions |
| :--- | :--- | :--- | :--- | :--- |
| **Deal** | `stage` | `lead` | `closed_won`, `closed_lost` | 8 |
| **Activity** | `status` | `scheduled` | `completed`, `cancelled` | 2 |

## Transition Rules by Model

### `Deal` Workflow (`stage`)
- **Initial State**: `lead`
- **Final States**: `closed_won`, `closed_lost`

| Current State (From) | Next State (To) | Authorized Roles |
| :--- | :--- | :--- |
| `lead` | `qualified` | `sales-rep`, `sales-manager`, `super-admin` |
| `lead` | `closed_lost` | `sales-rep`, `sales-manager`, `super-admin` |
| `qualified` | `proposal` | `sales-rep`, `sales-manager`, `super-admin` |
| `qualified` | `closed_lost` | `sales-rep`, `sales-manager`, `super-admin` |
| `proposal` | `negotiation` | `sales-rep`, `sales-manager`, `super-admin` |
| `proposal` | `closed_lost` | `sales-rep`, `sales-manager`, `super-admin` |
| `negotiation` | `closed_won` | `sales-manager`, `super-admin` |
| `negotiation` | `closed_lost` | `sales-rep`, `sales-manager`, `super-admin` |

### `Activity` Workflow (`status`)
- **Initial State**: `scheduled`
- **Final States**: `completed`, `cancelled`

| Current State (From) | Next State (To) | Authorized Roles |
| :--- | :--- | :--- |
| `scheduled` | `completed` | `sales-rep`, `sales-manager`, `super-admin` |
| `scheduled` | `cancelled` | `sales-rep`, `sales-manager`, `super-admin` |
