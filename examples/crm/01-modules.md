# Functional Modules & Domain Entities

This document details the functional domains and entity boundaries.

## Domain Entities Summary

| Model | Table | Fields | Relations | State Machine |
| :--- | :--- | :--- | :--- | :--- |
| **User** | `users` | 5 | 5 | No |
| **Company** | `companies` | 6 | 3 | No |
| **Contact** | `contacts` | 8 | 3 | No |
| **Deal** | `deals` | 9 | 5 | Yes |
| **Activity** | `activities` | 8 | 3 | Yes |
| **Note** | `notes` | 5 | 2 | No |
| **AuditLog** | `audit_logs` | 6 | 1 | No |

## Module Structure

### User Module
- **Database Table**: `users`
- **Purpose**: Encapsulates domain logic for `User` entities.
- **Key Attributes**: `id`, `name`, `email`, `phone`, `role`
- **Associated Relations**: `companies`, `deals`, `activities`, `notes`, `audit_logs`

### Company Module
- **Database Table**: `companies`
- **Purpose**: Encapsulates domain logic for `Company` entities.
- **Key Attributes**: `id`, `owner_id`, `name`, `domain`, `annual_revenue`
- **Associated Relations**: `account_owner`, `contacts`, `deals`

### Contact Module
- **Database Table**: `contacts`
- **Purpose**: Encapsulates domain logic for `Contact` entities.
- **Key Attributes**: `id`, `company_id`, `first_name`, `last_name`, `email`
- **Associated Relations**: `company`, `deals`, `activities`

### Deal Module
- **Database Table**: `deals`
- **Purpose**: Encapsulates domain logic for `Deal` entities.
- **Key Attributes**: `id`, `company_id`, `contact_id`, `owner_id`, `title`
- **Associated Relations**: `company`, `primary_contact`, `owner`, `activities`, `notes`

### Activity Module
- **Database Table**: `activities`
- **Purpose**: Encapsulates domain logic for `Activity` entities.
- **Key Attributes**: `id`, `deal_id`, `contact_id`, `assigned_to_id`, `type`
- **Associated Relations**: `deal`, `contact`, `assigned_to`

### Note Module
- **Database Table**: `notes`
- **Purpose**: Encapsulates domain logic for `Note` entities.
- **Key Attributes**: `id`, `deal_id`, `author_id`, `content`, `attachment`
- **Associated Relations**: `deal`, `author`

### AuditLog Module
- **Database Table**: `audit_logs`
- **Purpose**: Encapsulates domain logic for `AuditLog` entities.
- **Key Attributes**: `id`, `user_id`, `action`, `auditable_type`, `auditable_id`
- **Associated Relations**: `user`
