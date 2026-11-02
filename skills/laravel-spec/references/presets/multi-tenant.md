# Preset: Multi-Tenant Architecture (`multi-tenant`)

The `multi-tenant` preset defines patterns and specifications for SaaS applications serving multiple organizations or tenants. It covers both **Single-Database Row-Level Scoping** (using `tenant_id` and native Filament panel tenancy) and **Multi-Database Isolation** (using `stancl/tenancy`), with strict query boundary enforcement and data leak prevention.

---

## 1. Architectural Strategy Comparison

| Dimension | Pattern A: Single-DB Tenant Scoping (Default) | Pattern B: Multi-DB Tenant Isolation |
| :--- | :--- | :--- |
| **Primary Use Case** | B2B SaaS, shared infrastructure, cost efficiency | Enterprise compliance, strict database isolation, distinct DB credentials |
| **Tooling** | Native Laravel Global Scopes + Filament Tenancy | `stancl/tenancy` v3 |
| **Isolation Boundary** | Row-level `tenant_id` column indexed on all tenant models | Dedicated SQLite/MySQL/Postgres database per tenant |
| **Migration Cost** | Run once across central database | Migrations executed across all tenant databases |
| **Filament Support** | Native: `$panel->tenant(Tenant::class)` | Custom middleware switching tenant connection |

---

## 2. Pattern A: Single-Database Scoping (Recommended)

### 2.1 The `BelongsToTenant` Trait & Global Scope
Every model belonging to a tenant applies a trait that enforces scoping on all SELECT, UPDATE, and DELETE operations, while automatically attaching the active `tenant_id` on model creation.

```php
namespace App\Models\Concerns;

use App\Models\Tenant;
use Filament\Facades\Filament;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

trait BelongsToTenant
{
    public static function bootBelongsToTenant(): void
    {
        static::creating(function (Model $model) {
            if (! $model->tenant_id && Filament::getTenant()) {
                $model->tenant_id = Filament::getTenant()->id;
            }
        });

        static::addGlobalScope('tenant', function (Builder $builder) {
            if ($tenant = Filament::getTenant()) {
                $builder->where($builder->getModel()->getTable() . '.tenant_id', $tenant->id);
            }
        });
    }

    public function tenant(): BelongsTo
    {
        return $this->belongsTo(Tenant::class);
    }
}
```

### 2.2 Filament Panel Configuration
Filament v3 and v4 provide first-class multi-tenancy support. Register the `Tenant` model in your panel provider:

```php
// app/Providers/Filament/AppPanelProvider.php
namespace App\Providers\Filament;

use App\Filament\Pages\Tenancy\EditTenantProfile;
use App\Filament\Pages\Tenancy\RegisterTenant;
use App\Models\Tenant;
use Filament\Panel;
use Filament\PanelProvider;

class AppPanelProvider extends PanelProvider
{
    public function panel(Panel $panel): Panel
    {
        return $panel
            ->id('app')
            ->path('app')
            ->tenant(Tenant::class, slugAttribute: 'slug')
            ->tenantRegistration(RegisterTenant::class)
            ->tenantProfile(EditTenantProfile::class)
            ->resources([
                // All resources here are automatically tenant-scoped by Filament
            ]);
    }
}
```

With `->tenant(Tenant::class, slugAttribute: 'slug')`:
- URLs automatically include the tenant slug: `https://app.domain.com/app/{tenant_slug}/orders`
- Filament automatically verifies that the authenticated user belongs to the requested tenant.
- Filament automatically injects `tenant_id` scoping to resource queries.

---

## 3. Cross-Tenant Leakage Prevention

1. **Route Model Binding Guard**:
   Even with global scopes active, always ensure explicit model-to-tenant verification when resolving route parameters in API controllers or Livewire actions:
   ```php
   abort_unless($order->tenant_id === Filament::getTenant()?->id, 403);
   ```
2. **Background Jobs & Queues**:
   Queued jobs execute outside the HTTP request lifecycle. When dispatching tenant-aware jobs, always pass the tenant ID or implement `TenantAwareJob`:
   ```php
   class ProcessTenantOrder implements ShouldQueue
   {
       public function __construct(public int $tenantId, public int $orderId) {}

       public function handle(): void
       {
           $tenant = Tenant::findOrFail($this->tenantId);
           // Set context or explicitly scope queries
           Order::where('tenant_id', $tenant->id)->findOrFail($this->orderId)->process();
       }
   }
   ```
3. **File Storage Isolation**:
   Store tenant assets in isolated subdirectories:
   ```php
   $path = $file->store("tenants/{$tenant->id}/documents", 'private');
   ```

---

## 4. Specification Schema Integration

Incorporate `multi-tenant` into `spec/spec.json`:

```json
{
  "project": {
    "presets": ["multi-tenant"]
  },
  "roles": [
    {
      "name": "super-admin",
      "description": "System operator with global cross-tenant access",
      "is_super_admin": true
    },
    {
      "name": "tenant-owner",
      "description": "Administrator of a specific tenant workspace"
    },
    {
      "name": "tenant-member",
      "description": "Standard collaborator within a tenant workspace"
    }
  ],
  "models": [
    {
      "name": "Tenant",
      "table": "tenants",
      "fields": [
        { "name": "id", "type": "bigInteger" },
        { "name": "name", "type": "string" },
        { "name": "slug", "type": "string", "unique": true, "index": true }
      ],
      "relations": [
        { "name": "users", "type": "belongsToMany", "model": "User", "inverse": "tenants" },
        { "name": "projects", "type": "hasMany", "model": "Project", "inverse": "tenant" }
      ]
    },
    {
      "name": "Project",
      "table": "projects",
      "fields": [
        { "name": "id", "type": "bigInteger" },
        { "name": "tenant_id", "type": "bigInteger", "index": true, "foreign": { "model": "Tenant" } },
        { "name": "title", "type": "string" }
      ],
      "relations": [
        { "name": "tenant", "type": "belongsTo", "model": "Tenant", "inverse": "projects" }
      ]
    }
  ],
  "policies": [
    {
      "model": "Project",
      "ownership": "owner_field:tenant_id",
      "abilities": {
        "viewAny": ["tenant-owner", "tenant-member", "super-admin"],
        "view": ["tenant-owner", "tenant-member", "super-admin"],
        "create": ["tenant-owner", "tenant-member", "super-admin"],
        "update": ["tenant-owner", "super-admin"],
        "delete": ["tenant-owner", "super-admin"]
      }
    }
  ],
  "filament": {
    "panels": [
      {
        "id": "app",
        "path": "app",
        "roles": ["tenant-owner", "tenant-member", "super-admin"],
        "resources": [
          {
            "model": "Project",
            "table": {
              "query_scope": "scopedToTenant"
            }
          }
        ]
      }
    ]
  }
}
```

---

## 5. Verification Checklist

- [ ] All tenant child tables include an indexed `tenant_id` foreign key referencing `tenants.id`.
- [ ] Spec policy definitions specify `ownership: "tenant"` or `ownership: "owner_field:tenant_id"`.
- [ ] Filament resources configured inside tenant panels declare `table.query_scope`.
- [ ] Queued jobs serialize and restore tenant context before executing business logic.
- [ ] Tenant slug uniqueness is enforced in database indexes and route parameters.
