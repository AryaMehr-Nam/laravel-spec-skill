# Filament Admin & User Panels

This document describes Filament panels, panel routes, and registered panel resources.

## Configured Panels

| Panel ID | Route Path | Access Roles | Resources Count |
| :--- | :--- | :--- | :--- |
| **admin** | `/admin` | `super-admin` | 7 |
| **vendor** | `/vendor` | `vendor`, `super-admin` | 3 |

## Panel Resources & Pages

### Panel: `admin` (Route: `/admin`)

| Resource Model | Filament Resource Class | Query Scope | Relation Mgrs |
| :--- | :--- | :--- | :--- |
| **User** | `UserResource` | `Default (all records)` | None |
| **VendorProfile** | `VendorProfileResource` | `scopedToAdmin` | None |
| **Category** | `CategoryResource` | `Default (all records)` | None |
| **Product** | `ProductResource` | `scopedToAdmin` | None |
| **Order** | `OrderResource` | `scopedToAdmin` | None |
| **Payment** | `PaymentResource` | `scopedToAdmin` | None |
| **Review** | `ReviewResource` | `scopedToAdmin` | None |

### Panel: `vendor` (Route: `/vendor`)

| Resource Model | Filament Resource Class | Query Scope | Relation Mgrs |
| :--- | :--- | :--- | :--- |
| **VendorProfile** | `VendorProfileResource` | `scopedToCurrentVendor` | None |
| **Product** | `ProductResource` | `scopedToVendorProducts` | None |
| **Order** | `OrderResource` | `scopedToVendorOrders` | None |
