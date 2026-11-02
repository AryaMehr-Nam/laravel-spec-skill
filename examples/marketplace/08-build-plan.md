# Implementation Build Plan & Milestone DAG

This document specifies the resumable build milestones, dependencies, and criteria.

## Milestones Summary

| Milestone | Title | Depends On | Model Scope | Acceptance Criteria Count |
| :--- | :--- | :--- | :--- | :--- |
| **M0** | Foundation, Authentication & Users | None (Root) | `User`, `VendorProfile` | 2 |
| **M1** | Product Catalog & Categories | `M0` | `Category`, `Product` | 2 |
| **M2** | Orders & Cart Items | `M1` | `Order`, `OrderItem` | 2 |
| **M3** | Payments, Reviews & Seller Settlements | `M2` | `Payment`, `Review` | 2 |

## Milestone Details & Verification Criteria

### Milestone `M0`: Foundation, Authentication & Users
- **Dependencies**: None (Foundation)
- **Model Scope**: `User`, `VendorProfile`

#### Acceptance Criteria

- [ ] User registration, authentication, and role authorization policies pass automated tests
- [ ] Vendor profile creation and relationship to user account pass integration tests

### Milestone `M1`: Product Catalog & Categories
- **Dependencies**: `M0`
- **Model Scope**: `Category`, `Product`

#### Acceptance Criteria

- [ ] Hierarchical category management and slug generation pass tests
- [ ] Vendor product CRUD, price decimal validation, and cover image upload constraints pass tests

### Milestone `M2`: Orders & Cart Items
- **Dependencies**: `M1`
- **Model Scope**: `Order`, `OrderItem`

#### Acceptance Criteria

- [ ] Order lifecycle state machine transitions from pending through delivered or cancelled
- [ ] Order item subtotal calculation and inventory deduction pass concurrency tests

### Milestone `M3`: Payments, Reviews & Seller Settlements
- **Dependencies**: `M2`
- **Model Scope**: `Payment`, `Review`

#### Acceptance Criteria

- [ ] Payment gateway callback verification with idempotency and double-spend locking passes tests
- [ ] Product reviews and ratings calculation pass authorization checks
