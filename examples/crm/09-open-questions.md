# Open Questions & Architecture Decisions

This document tracks architectural inquiries, edge cases, and assumptions.

## Pending Questions

| ID | Category | Question | Proposed Resolution | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Q1** | `Email Sync` | Should inbound customer email replies sync via IMAP polling or webhook forwarders? | Phase 1 will rely on Mailgun inbound route webhooks with HMAC signature validation. | `resolved` |
| **Q2** | `Lead Rotation` | What round-robin algorithm should govern new lead assignment across sales reps? | Weighted round-robin by active deal load per sales representative. | `resolved` |

## Technical Baseline & Assumptions

- **Framework Baseline**: Laravel `v12` with PHP 8.3+
- **Admin Panel**: Filament `v3`
- **Test Strategy**: Pest / PHPUnit tests for policy abilities and workflows
- **Database Engine**: RDBMS with atomic transactions and foreign keys
