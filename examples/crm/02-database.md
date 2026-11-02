# Database Schema & Data Models

This document details the database schema, column types, and relationships.

## Tables Overview

| Model | Table | Primary Key | Foreign References |
| :--- | :--- | :--- | :--- |
| **User** | `users` | `id` (bigInteger) | None |
| **Company** | `companies` | `id` (bigInteger) | `owner_id -> User` |
| **Contact** | `contacts` | `id` (bigInteger) | `company_id -> Company` |
| **Deal** | `deals` | `id` (bigInteger) | `company_id -> Company`, `contact_id -> Contact`, `owner_id -> User` |
| **Activity** | `activities` | `id` (bigInteger) | `deal_id -> Deal`, `contact_id -> Contact`, `assigned_to_id -> User` |
| **Note** | `notes` | `id` (bigInteger) | `deal_id -> Deal`, `author_id -> User` |
| **AuditLog** | `audit_logs` | `id` (bigInteger) | `user_id -> User` |

## Detailed Schema Definitions

### `User` (`users`)

#### Columns

| Column | Type | Nullable | Index / Unique | Constraints & Details |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `bigInteger` | No | - | - |
| `name` | `string` | No | - | - |
| `email` | `string` | No | UNIQUE | PII: Encrypted/Audited |
| `phone` | `string` | No | UNIQUE | PII: Encrypted/Audited |
| `role` | `enum` | No | - | Values: [admin, manager, rep] |

#### Eloquent Relationships

| Method | Type | Related Model | Foreign Key | Inverse Method |
| :--- | :--- | :--- | :--- | :--- |
| `companies()` | `hasMany` | `Company` | `companies_id` | `account_owner` |
| `deals()` | `hasMany` | `Deal` | `deals_id` | `owner` |
| `activities()` | `hasMany` | `Activity` | `activities_id` | `assigned_to` |
| `notes()` | `hasMany` | `Note` | `notes_id` | `author` |
| `audit_logs()` | `hasMany` | `AuditLog` | `audit_logs_id` | `user` |

### `Company` (`companies`)

#### Columns

| Column | Type | Nullable | Index / Unique | Constraints & Details |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `bigInteger` | No | - | - |
| `owner_id` | `bigInteger` | No | INDEX | FK -> User |
| `name` | `string` | No | - | - |
| `domain` | `string` | No | UNIQUE, INDEX | - |
| `annual_revenue` | `decimal` | Yes | - | Decimal(14, 2) |
| `employee_count` | `integer` | Yes | - | - |

#### Eloquent Relationships

| Method | Type | Related Model | Foreign Key | Inverse Method |
| :--- | :--- | :--- | :--- | :--- |
| `account_owner()` | `belongsTo` | `User` | `account_owner_id` | `companies` |
| `contacts()` | `hasMany` | `Contact` | `contacts_id` | `company` |
| `deals()` | `hasMany` | `Deal` | `deals_id` | `company` |

### `Contact` (`contacts`)

#### Columns

| Column | Type | Nullable | Index / Unique | Constraints & Details |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `bigInteger` | No | - | - |
| `company_id` | `bigInteger` | No | INDEX | FK -> Company |
| `first_name` | `string` | No | - | - |
| `last_name` | `string` | No | - | - |
| `email` | `string` | No | UNIQUE | PII: Encrypted/Audited |
| `phone` | `string` | No | - | PII: Encrypted/Audited |
| `position` | `string` | Yes | - | - |
| `avatar` | `image` | Yes | - | Max: 2048KB, Mimes: image/jpeg, image/png |

#### Eloquent Relationships

| Method | Type | Related Model | Foreign Key | Inverse Method |
| :--- | :--- | :--- | :--- | :--- |
| `company()` | `belongsTo` | `Company` | `company_id` | `contacts` |
| `deals()` | `hasMany` | `Deal` | `deals_id` | `primary_contact` |
| `activities()` | `hasMany` | `Activity` | `activities_id` | `contact` |

### `Deal` (`deals`)

#### Columns

| Column | Type | Nullable | Index / Unique | Constraints & Details |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `bigInteger` | No | - | - |
| `company_id` | `bigInteger` | No | INDEX | FK -> Company |
| `contact_id` | `bigInteger` | Yes | INDEX | FK -> Contact |
| `owner_id` | `bigInteger` | No | INDEX | FK -> User |
| `title` | `string` | No | - | - |
| `deal_amount` | `decimal` | No | - | Decimal(12, 2) |
| `stage` | `string` | No | - | - |
| `probability` | `integer` | No | - | - |
| `expected_close_date` | `date` | Yes | - | - |

#### Eloquent Relationships

| Method | Type | Related Model | Foreign Key | Inverse Method |
| :--- | :--- | :--- | :--- | :--- |
| `company()` | `belongsTo` | `Company` | `company_id` | `deals` |
| `primary_contact()` | `belongsTo` | `Contact` | `primary_contact_id` | `deals` |
| `owner()` | `belongsTo` | `User` | `owner_id` | `deals` |
| `activities()` | `hasMany` | `Activity` | `activities_id` | `deal` |
| `notes()` | `hasMany` | `Note` | `notes_id` | `deal` |

### `Activity` (`activities`)

#### Columns

| Column | Type | Nullable | Index / Unique | Constraints & Details |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `bigInteger` | No | - | - |
| `deal_id` | `bigInteger` | Yes | INDEX | FK -> Deal |
| `contact_id` | `bigInteger` | Yes | INDEX | FK -> Contact |
| `assigned_to_id` | `bigInteger` | No | INDEX | FK -> User |
| `type` | `enum` | No | - | Values: [call, meeting, email, task] |
| `subject` | `string` | No | - | - |
| `status` | `string` | No | - | - |
| `due_at` | `datetime` | Yes | - | - |

#### Eloquent Relationships

| Method | Type | Related Model | Foreign Key | Inverse Method |
| :--- | :--- | :--- | :--- | :--- |
| `deal()` | `belongsTo` | `Deal` | `deal_id` | `activities` |
| `contact()` | `belongsTo` | `Contact` | `contact_id` | `activities` |
| `assigned_to()` | `belongsTo` | `User` | `assigned_to_id` | `activities` |

### `Note` (`notes`)

#### Columns

| Column | Type | Nullable | Index / Unique | Constraints & Details |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `bigInteger` | No | - | - |
| `deal_id` | `bigInteger` | No | INDEX | FK -> Deal |
| `author_id` | `bigInteger` | No | INDEX | FK -> User |
| `content` | `text` | No | - | - |
| `attachment` | `file` | Yes | - | Max: 10240KB, Mimes: application/pdf, image/png, image/jpeg |

#### Eloquent Relationships

| Method | Type | Related Model | Foreign Key | Inverse Method |
| :--- | :--- | :--- | :--- | :--- |
| `deal()` | `belongsTo` | `Deal` | `deal_id` | `notes` |
| `author()` | `belongsTo` | `User` | `author_id` | `notes` |

### `AuditLog` (`audit_logs`)

#### Columns

| Column | Type | Nullable | Index / Unique | Constraints & Details |
| :--- | :--- | :--- | :--- | :--- |
| `id` | `bigInteger` | No | - | - |
| `user_id` | `bigInteger` | Yes | INDEX | FK -> User |
| `action` | `string` | No | - | - |
| `auditable_type` | `string` | No | - | - |
| `auditable_id` | `bigInteger` | No | INDEX | - |
| `ip_address` | `string` | No | - | PII: Encrypted/Audited |

#### Eloquent Relationships

| Method | Type | Related Model | Foreign Key | Inverse Method |
| :--- | :--- | :--- | :--- | :--- |
| `user()` | `belongsTo` | `User` | `user_id` | `audit_logs` |
