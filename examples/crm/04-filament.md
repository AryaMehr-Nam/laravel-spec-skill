# Filament Admin & User Panels

This document describes Filament panels, panel routes, and registered panel resources.

## Configured Panels

| Panel ID | Route Path | Access Roles | Resources Count |
| :--- | :--- | :--- | :--- |
| **admin** | `/admin` | `super-admin` | 7 |
| **sales** | `/sales` | `sales-manager`, `sales-rep`, `super-admin` | 5 |

## Panel Resources & Pages

### Panel: `admin` (Route: `/admin`)

| Resource Model | Filament Resource Class | Query Scope | Relation Mgrs |
| :--- | :--- | :--- | :--- |
| **User** | `UserResource` | `Default (all records)` | None |
| **Company** | `CompanyResource` | `scopedToAdmin` | None |
| **Contact** | `ContactResource` | `Default (all records)` | None |
| **Deal** | `DealResource` | `scopedToAdmin` | None |
| **Activity** | `ActivityResource` | `scopedToAdmin` | None |
| **Note** | `NoteResource` | `scopedToAdmin` | None |
| **AuditLog** | `AuditLogResource` | `Default (all records)` | None |

### Panel: `sales` (Route: `/sales`)

| Resource Model | Filament Resource Class | Query Scope | Relation Mgrs |
| :--- | :--- | :--- | :--- |
| **Company** | `CompanyResource` | `scopedToRepOrTeam` | None |
| **Contact** | `ContactResource` | `Default (all records)` | None |
| **Deal** | `DealResource` | `scopedToRepDeals` | None |
| **Activity** | `ActivityResource` | `scopedToRepActivities` | None |
| **Note** | `NoteResource` | `scopedToRepNotes` | None |
