# Implementation Build Plan & Milestone DAG

This document specifies the resumable build milestones, dependencies, and criteria.

## Milestones Summary

| Milestone | Title | Depends On | Model Scope | Acceptance Criteria Count |
| :--- | :--- | :--- | :--- | :--- |
| **M0** | Core Identity & Account Foundation | None (Root) | `User`, `AuditLog` | 2 |
| **M1** | Account & Contact Directory | `M0` | `Company`, `Contact` | 2 |
| **M2** | Sales Pipeline & Deal Governance | `M1` | `Deal` | 2 |
| **M3** | Collaboration & Activity Tracking | `M2` | `Activity`, `Note` | 2 |

## Milestone Details & Verification Criteria

### Milestone `M0`: Core Identity & Account Foundation
- **Dependencies**: None (Foundation)
- **Model Scope**: `User`, `AuditLog`

#### Acceptance Criteria

- [ ] User authentication, role assignment, and PII audit log events pass tests
- [ ] Baseline database migrations and seeders execute cleanly

### Milestone `M1`: Account & Contact Directory
- **Dependencies**: `M0`
- **Model Scope**: `Company`, `Contact`

#### Acceptance Criteria

- [ ] Company domain uniqueness and annual revenue decimal precision pass tests
- [ ] Contact profile avatar upload constraints (2MB max) pass validation

### Milestone `M2`: Sales Pipeline & Deal Governance
- **Dependencies**: `M1`
- **Model Scope**: `Deal`

#### Acceptance Criteria

- [ ] Deal stage state machine transitions from lead through closed_won or closed_lost
- [ ] Deal ownership scoping restricts sales reps to assigned accounts and deals

### Milestone `M3`: Collaboration & Activity Tracking
- **Dependencies**: `M2`
- **Model Scope**: `Activity`, `Note`

#### Acceptance Criteria

- [ ] Activity lifecycle transition from scheduled to completed or cancelled passes tests
- [ ] Deal notes with PDF/image attachments enforce 10MB limits and proper authorization
