# Security, Compliance & Data Safeguards

This document outlines PII tracking, audit logging, upload security, and data scoping.

## Personally Identifiable Information (PII)

| Model | Field Name | Column Type | Audit Logging Required |
| :--- | :--- | :--- | :--- |
| **User** | `email` | `string` | Yes (Monitored) |
| **User** | `phone` | `string` | Yes (Monitored) |

## Audit Logging Architecture

- **Audit Logging Status**: Active & Enforced
- **Scope**: Modifications to PII fields, finances, and state transitions.
- **Recommendation**: `spatie/laravel-activitylog` or event listeners.

## File Upload Constraints

| Model | Field | Max Size | Allowed MIME Types |
| :--- | :--- | :--- | :--- |
| **User** | `avatar` | 2048 KB | `image/jpeg, image/png, image/webp` |
| **VendorProfile** | `logo` | 4096 KB | `image/jpeg, image/png, image/webp` |
| **Product** | `cover_image` | 5120 KB | `image/jpeg, image/png, image/webp` |

## Tenant & Ownership Scoping

| Model | Ownership Policy Scoping |
| :--- | :--- |
| **User** | `none` |
| **VendorProfile** | `owner_field:user_id` |
| **Category** | `none` |
| **Product** | `owner_field:vendor_id` |
| **Order** | `owner_field:customer_id` |
| **OrderItem** | `none` |
| **Payment** | `owner_field:user_id` |
| **Review** | `owner_field:customer_id` |
