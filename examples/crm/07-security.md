# Security, Compliance & Data Safeguards

This document outlines PII tracking, audit logging, upload security, and data scoping.

## Personally Identifiable Information (PII)

| Model | Field Name | Column Type | Audit Logging Required |
| :--- | :--- | :--- | :--- |
| **User** | `email` | `string` | Yes (Monitored) |
| **User** | `phone` | `string` | Yes (Monitored) |
| **Contact** | `email` | `string` | Yes (Monitored) |
| **Contact** | `phone` | `string` | Yes (Monitored) |
| **AuditLog** | `ip_address` | `string` | Yes (Monitored) |

## Audit Logging Architecture

- **Audit Logging Status**: Active & Enforced
- **Scope**: Modifications to PII fields, finances, and state transitions.
- **Recommendation**: `spatie/laravel-activitylog` or event listeners.

## File Upload Constraints

| Model | Field | Max Size | Allowed MIME Types |
| :--- | :--- | :--- | :--- |
| **Contact** | `avatar` | 2048 KB | `image/jpeg, image/png` |
| **Note** | `attachment` | 10240 KB | `application/pdf, image/png, image/jpeg` |

## Tenant & Ownership Scoping

| Model | Ownership Policy Scoping |
| :--- | :--- |
| **User** | `none` |
| **Company** | `owner_field:owner_id` |
| **Contact** | `none` |
| **Deal** | `owner_field:owner_id` |
| **Activity** | `owner_field:assigned_to_id` |
| **Note** | `owner_field:author_id` |
| **AuditLog** | `none` |
