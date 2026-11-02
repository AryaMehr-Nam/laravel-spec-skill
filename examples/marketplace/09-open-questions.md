# Open Questions & Architecture Decisions

This document tracks architectural inquiries, edge cases, and assumptions.

## Pending Questions

| ID | Category | Question | Proposed Resolution | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Q1** | `Payments` | Should vendor payouts execute via automated Sheba API transfers or manual bank export? | Phase 1 will use manual accounting exports; automated payout gateway planned for Phase 2. | `resolved` |
| **Q2** | `Inventory` | Should inventory be reserved upon order placement or after successful payment confirmation? | Inventory is temporarily held for 15 minutes during pending status, released if payment fails. | `resolved` |

## Technical Baseline & Assumptions

- **Framework Baseline**: Laravel `v12` with PHP 8.3+
- **Admin Panel**: Filament `v3`
- **Test Strategy**: Pest / PHPUnit tests for policy abilities and workflows
- **Database Engine**: RDBMS with atomic transactions and foreign keys
