# Specification Format Reference (`spec/spec.json`)

The `spec/spec.json` file is the sole canonical source of truth for the entire application specification. All markdown documentation (`spec/00-overview.md` through `spec/09-open-questions.md`) and executable Artisan scaffolding scripts (`spec/commands.sh`) are deterministically derived from this single file.

---

## 1. Top-Level Structure

A valid specification root must be a JSON object containing the seven required top-level keys:

```json
{
  "project": { ... },
  "roles": [ ... ],
  "models": [ ... ],
  "policies": [ ... ],
  "filament": { ... },
  "integrations": [ ... ],
  "milestones": [ ... ]
}
```

---

## 2. Section Specifications

### 2.1 `project` (Object, Required)
Contains global metadata and application configurations.

| Field | Type | Required | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `name` | string | Yes | Human-readable application title | `"Marketplace Pro"` |
| `description` | string | Yes | Summary of business domain and scope | `"Multi-vendor e-commerce platform"` |
| `locale` | string | Yes | Primary ISO locale code | `"en"`, `"fa"` |
| `timezone` | string | Yes | Default PHP/Laravel timezone | `"UTC"`, `"Asia/Tehran"` |
| `laravel_version` | string | Yes | Target major Laravel release | `"11"`, `"12"`, `"13"` |
| `filament_version` | string | Yes | Target Filament version | `"v3"`, `"v4"` |
| `presets` | array[string] | No | Activated architectural preset identifiers | `["rtl-fa", "iran-payments"]` |
| `audit_log` | boolean \| object | No | Global audit logging declaration (required if PII fields exist) | `true` or `{"driver": "spatie"}` |

#### Example:
```json
"project": {
  "name": "Boutique CRM",
  "description": "High-touch customer relationship platform for luxury retail",
  "locale": "en",
  "timezone": "UTC",
  "laravel_version": "12",
  "filament_version": "v3",
  "presets": ["otp-login"],
  "audit_log": true
}
```

---

### 2.2 `roles` (Array, Required)
Declares all user security roles and privilege levels. At least one role MUST have `"is_super_admin": true`.

| Field | Type | Required | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `name` | string | Yes | Unique kebab-case or snake_case role slug | `"super-admin"`, `"sales-agent"` |
| `description` | string | Yes | Narrative description of access scope | `"Unrestricted administrative access"` |
| `is_super_admin` | boolean | No | Identifies the root administrator role (bypasses all policy checks) | `true` |

#### Example:
```json
"roles": [
  {
    "name": "super-admin",
    "description": "Complete system access with policy bypass",
    "is_super_admin": true
  },
  {
    "name": "sales-agent",
    "description": "Manages assigned customer leads and deals",
    "is_super_admin": false
  }
]
```

---

### 2.3 `models` (Array, Required)
Defines Eloquent models, database table schema, fields, relationships, and state machine lifecycles.

#### Model Object
| Field | Type | Required | Description | Example |
| :--- | :--- | :--- | :--- | :--- |
| `name` | string | Yes | Singular PascalCase model identifier | `"Deal"`, `"Lead"`, `"User"` |
| `table` | string | Yes | Snake_case plural database table name | `"deals"`, `"leads"`, `"users"` |
| `fields` | array[object] | Yes | Database columns and field attributes | (See Field Object below) |
| `relations` | array[object] | No | Eloquent relationship definitions | (See Relation Object below) |
| `state_machine` | object | No | Finite state machine specification | (See State Machine below) |

#### Field Object (`models[].fields[]`)
| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | string | Yes | Column name in snake_case (e.g. `price_cents`, `email`) |
| `type` | string | Yes | Laravel schema data type (`id`, `uuid`, `string`, `text`, `integer`, `bigInteger`, `unsignedBigInteger`, `decimal`, `boolean`, `date`, `dateTime`, `timestamp`, `json`, `enum`) |
| `nullable` | boolean | No | Whether the column accepts null values (default: `false`) |
| `unique` | boolean | No | Generates unique database constraint |
| `default` | any | No | Default column value |
| `index` | boolean | No | Generates database index (mandatory on foreign keys) |
| `currency` | boolean | No | Flags monetary fields. Prohibits float; requires integer minor units or decimal with scale >= 2 |
| `pii` | boolean | No | Flags personally identifiable information. Requires `project.audit_log` enabled |
| `enum_values` | array[string] | Conditional | Mandatory when `type: "enum"`. Non-empty list of string values |
| `max_size_kb` | integer | Conditional | Mandatory on file upload fields. Maximum allowed file size in KB |
| `allowed_mimes` | array[string] | Conditional | Mandatory on file upload fields. Array of allowed MIME types |

#### Relation Object (`models[].relations[]`)
| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | string | Yes | Method name on the Eloquent model (`user`, `deals`, `tags`) |
| `type` | string | Yes | Relationship type: `belongsTo`, `hasMany`, `hasOne`, `belongsToMany`, `morphMany`, `morphTo` |
| `target` | string | Yes | PascalCase name of target model |
| `foreign_key` | string | No | Foreign key column name (e.g. `user_id`) |
| `inverse` | string | No | Reciprocal relationship method name on target model |
| `cascade_delete` | boolean | No | Configures cascading database deletes |

#### State Machine Object (`models[].state_machine`)
| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `field` | string | Yes | Column storing current state (must be declared in `fields`) |
| `states` | object | Yes | Map of state names to transition definitions |
| `states[name].initial` | boolean | Conditional | Exactly one state MUST be marked `initial: true` |
| `states[name].transitions` | array[string] | Yes | Allowed next states. Terminal states MUST have empty `[]` |
| `states[name].roles` | array[string] | No | Roles authorized to execute transitions from this state |
| `final_states` | array[string] | No | Array of terminal state names |

#### Example:
```json
{
  "name": "Order",
  "table": "orders",
  "fields": [
    {"name": "id", "type": "id"},
    {"name": "order_number", "type": "string", "unique": true},
    {"name": "customer_id", "type": "unsignedBigInteger", "index": true},
    {"name": "total_cents", "type": "bigInteger", "currency": true},
    {"name": "status", "type": "enum", "enum_values": ["pending", "paid", "fulfilled", "cancelled"]},
    {"name": "created_at", "type": "timestamp", "nullable": true},
    {"name": "updated_at", "type": "timestamp", "nullable": true}
  ],
  "relations": [
    {
      "name": "customer",
      "type": "belongsTo",
      "target": "Customer",
      "foreign_key": "customer_id",
      "inverse": "orders"
    }
  ],
  "state_machine": {
    "field": "status",
    "states": {
      "pending": {"initial": true, "transitions": ["paid", "cancelled"], "roles": ["super-admin", "vendor"]},
      "paid": {"transitions": ["fulfilled", "cancelled"], "roles": ["super-admin", "vendor"]},
      "fulfilled": {"transitions": []},
      "cancelled": {"transitions": []}
    },
    "final_states": ["fulfilled", "cancelled"]
  }
}
```

---

### 2.4 `policies` (Array, Required)
Defines authorization policies for models. Every Filament resource MUST have a corresponding policy.

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `model` | string | Yes | Model name this policy governs |
| `ownership_field` | string | No | Model column used to filter records to current authenticated user (e.g. `user_id`, `vendor_id`) |
| `abilities` | object | Yes | Map of ability names to authorized role name arrays. Must include standard abilities: `viewAny`, `view`, `create`, `update`, `delete` |

#### Example:
```json
{
  "model": "Order",
  "ownership_field": "vendor_id",
  "abilities": {
    "viewAny": ["super-admin", "vendor"],
    "view": ["super-admin", "vendor"],
    "create": ["super-admin"],
    "update": ["super-admin", "vendor"],
    "delete": ["super-admin"],
    "cancel": ["super-admin", "vendor"]
  }
}
```

---

### 2.5 `filament` (Object, Required)
Configures the Filament panel providers and resources.

#### Panels (`filament.panels[]`)
| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `id` | string | Yes | Unique panel identifier (e.g. `admin`, `vendor`) |
| `path` | string | Yes | Route path prefix (e.g. `admin`, `portal`) |
| `auth_guard` | string | Yes | Laravel authentication guard (e.g. `web`) |
| `roles` | array[string] | Yes | Roles permitted to access this panel |
| `resources` | array[object] | Yes | Filament resource configurations |

#### Resources (`filament.panels[].resources[]`)
| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `model` | string | Yes | Associated model name |
| `navigation_group` | string | No | Sidebar navigation group heading |
| `navigation_sort` | integer | No | Sort order in navigation group |
| `pages` | array[string] | Yes | Standard resource pages (`ListRecords`, `CreateRecord`, `EditRecord`, `ViewRecord`) |
| `relation_managers` | array[string] | No | Filament relation managers mounted on edit page |
| `widgets` | array[string] | No | Resource-specific dashboard widgets |
| `filters` | array[object] | No | Table filter declarations |
| `actions` | array[object] | No | Table and page action declarations |
| `query_scope` | boolean \| string | Conditional | Mandatory when policy declares `ownership_field`. Enforces tenant/owner record isolation |

#### Example:
```json
"filament": {
  "panels": [
    {
      "id": "admin",
      "path": "admin",
      "auth_guard": "web",
      "roles": ["super-admin"],
      "resources": [
        {
          "model": "Order",
          "navigation_group": "Sales",
          "navigation_sort": 1,
          "pages": ["ListRecords", "ViewRecord", "EditRecord"],
          "relation_managers": ["ItemsRelationManager"],
          "query_scope": true
        }
      ]
    }
  ]
}
```

---

### 2.6 `integrations` (Array, Required)
Catalogs external services, SDKs, and third-party APIs.

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `name` | string | Yes | Unique service identifier (e.g. `zarinpal`, `kavenegar`) |
| `type` | string | Yes | Integration category (`payment_gateway`, `sms_gateway`, `storage`, `mail`, `search`, `webhook`) |
| `description` | string | Yes | Summary of functionality and usage |
| `config_keys` | array[string] | Yes | Required environment variables / config keys |
| `events_handled` | array[string] | No | Dispatched or consumed Laravel events |

#### Example:
```json
{
  "name": "kavenegar_sms",
  "type": "sms_gateway",
  "description": "Transactional SMS OTP verification and order status alerts",
  "config_keys": ["KAVENEGAR_API_KEY", "KAVENEGAR_SENDER_LINE"],
  "events_handled": ["UserRegistered", "OrderDispatched"]
}
```

---

### 2.7 `milestones` (Array, Required)
Defines an acyclic directed graph (DAG) of implementation milestones.

| Field | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `id` | string | Yes | Unique milestone identifier (`M0`, `M1`, `M2`, ...) |
| `title` | string | Yes | Descriptive milestone title |
| `depends_on` | array[string] | Yes | Array of prerequisite milestone IDs (must be acyclic) |
| `scope` | array[string] | Yes | Array of model names covered in this milestone |
| `acceptance` | array[string] | Yes | Concrete verifiable acceptance criteria (minimum 2 criteria required) |

#### Example:
```json
"milestones": [
  {
    "id": "M0",
    "title": "Foundation & Authentication",
    "depends_on": [],
    "scope": ["User"],
    "acceptance": [
      "User authentication and role assignment tests pass",
      "Admin panel login is verified for super-admin role"
    ]
  },
  {
    "id": "M1",
    "title": "Order Management & Escrow",
    "depends_on": ["M0"],
    "scope": ["Order", "OrderItem"],
    "acceptance": [
      "Order state machine enforces transition rules from pending to paid",
      "Vendor panel isolates orders via ownership query scope"
    ]
  }
]
```

---

## 3. Schema Validation & Tooling

To validate any `spec/spec.json` against the formal JSON Schema:
```bash
# Execute standard Python validator
python skills/laravel-spec/scripts/validate_spec.py spec/spec.json --strict
```
The formal schema definition is maintained in `schemas/spec.schema.json`.
