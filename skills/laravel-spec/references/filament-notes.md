# Filament v3/v4 Architecture & Implementation Guide

This reference outlines production best practices for building enterprise administrative panels, vendor portals, and resource interfaces using **Filament v3 and v4** with Laravel.

---

## 1. Multi-Panel Architecture

Filament employs **Panel Providers** registered as Laravel service providers. Each panel is completely isolated with its own route path prefix, authentication guard, middleware pipeline, navigation tree, and theme styling.

### 1.1 Panel Provider Configuration
Declare distinct panel providers for each administrative boundary (e.g. `AdminPanelProvider`, `VendorPanelProvider`):

```php
namespace App\Providers\Filament;

use Filament\Panel;
use Filament\PanelProvider;
use Filament\Support\Colors\Color;
use Filament\Http\Middleware\Authenticate;
use Illuminate\Session\Middleware\AuthenticateSession;

class AdminPanelProvider extends PanelProvider
{
    public function panel(Panel $panel): Panel
    {
        return $panel
            ->default()
            ->id('admin')
            ->path('admin')
            ->authGuard('web')
            ->colors([
                'primary' => Color::Amber,
            ])
            ->discoverResources(in: app_path('Filament/Resources'), for: 'App\\Filament\\Resources')
            ->discoverPages(in: app_path('Filament/Pages'), for: 'App\\Filament\\Pages')
            ->discoverWidgets(in: app_path('Filament/Widgets'), for: 'App\\Filament\\Widgets')
            ->middleware([
                \Illuminate\Cookie\Middleware\EncryptCookies::class,
                \Illuminate\Session\Middleware\StartSession::class,
                AuthenticateSession::class,
                \Illuminate\View\Middleware\ShareErrorsFromSession::class,
            ])
            ->authMiddleware([
                Authenticate::class,
            ]);
    }
}
```

---

## 2. Resource Architecture

Filament Resources represent Eloquent models within a panel. Each resource coordinates Form Schemas, Table Schemas, Relation Managers, and Authorization Policies.

### 2.1 Form Schemas
Form schemas define interactive inputs for creating and updating records.

```php
namespace App\Filament\Resources;

use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\Resource;

class OrderResource extends Resource
{
    public static function form(Form $form): Form
    {
        return $form
            ->schema([
                Forms\Components\Section::make('Order Details')
                    ->schema([
                        Forms\Components\TextInput::make('order_number')
                            ->required()
                            ->maxLength(32)
                            ->unique(ignoreRecord: true),
                        Forms\Components\Select::make('customer_id')
                            ->relationship('customer', 'name')
                            ->searchable()
                            ->preload()
                            ->required(),
                        Forms\Components\TextInput::make('total_cents')
                            ->numeric()
                            ->required()
                            ->suffix('cents'),
                        Forms\Components\Select::make('status')
                            ->options([
                                'pending' => 'Pending',
                                'paid' => 'Paid',
                                'fulfilled' => 'Fulfilled',
                                'cancelled' => 'Cancelled',
                            ])
                            ->required(),
                    ])->columns(2),
            ]);
    }
}
```

### 2.2 Table Schemas
Tables display paginated, searchable, and filterable data sets. Always declare eager loading on table queries for relationship columns to prevent N+1 query bottlenecks.

```php
public static function table(Table $table): Table
{
    return $table
        ->columns([
            Tables\Columns\TextColumn::make('order_number')
                ->searchable()
                ->sortable(),
            Tables\Columns\TextColumn::make('customer.name')
                ->searchable()
                ->sortable(),
            Tables\Columns\TextColumn::make('total_cents')
                ->money('USD', divideBy: 100)
                ->sortable(),
            Tables\Columns\TextColumn::make('status')
                ->badge()
                ->color(fn (string $state): string => match ($state) {
                    'paid' => 'success',
                    'fulfilled' => 'info',
                    'pending' => 'warning',
                    'cancelled' => 'danger',
                }),
            Tables\Columns\TextColumn::make('created_at')
                ->dateTime()
                ->toggleable(isToggledHiddenByDefault: true),
        ])
        ->filters([
            Tables\Filters\SelectFilter::make('status')
                ->options([
                    'pending' => 'Pending',
                    'paid' => 'Paid',
                    'fulfilled' => 'Fulfilled',
                    'cancelled' => 'Cancelled',
                ]),
        ])
        ->actions([
            Tables\Actions\ViewAction::make(),
            Tables\Actions\EditAction::make(),
        ])
        ->bulkActions([
            Tables\Actions\BulkActionGroup::make([
                Tables\Actions\DeleteBulkAction::make(),
            ]),
        ]);
}
```

---

## 3. Relation Managers

Relation Managers embed child collections (e.g., `OrderItem` on `Order`, `Activity` on `Lead`) directly within the edit or view pages of a parent resource.

### 3.1 Defining a Relation Manager
```php
namespace App\Filament\Resources\OrderResource\RelationManagers;

use Filament\Forms;
use Filament\Forms\Form;
use Filament\Resources\RelationManagers\RelationManager;
use Filament\Tables;
use Filament\Tables\Table;

class ItemsRelationManager extends RelationManager
{
    protected static string $relationship = 'items';

    public function form(Form $form): Form
    {
        return $form->schema([
            Forms\Components\Select::make('product_id')
                ->relationship('product', 'name')
                ->required(),
            Forms\Components\TextInput::make('quantity')
                ->numeric()
                ->default(1)
                ->required(),
            Forms\Components\TextInput::make('unit_price_cents')
                ->numeric()
                ->required(),
        ]);
    }

    public function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('product.name'),
                Tables\Columns\TextColumn::make('quantity'),
                Tables\Columns\TextColumn::make('unit_price_cents')->money('USD', divideBy: 100),
            ])
            ->headerActions([
                Tables\Actions\CreateAction::make(),
            ])
            ->actions([
                Tables\Actions\EditAction::make(),
                Tables\Actions\DeleteAction::make(),
            ]);
    }
}
```

Mount relation managers inside the resource:
```php
public static function getRelations(): array
{
    return [
        RelationManagers\ItemsRelationManager::class,
    ];
}
```

---

## 4. Authorization & Ownership Scoping

Filament automatically discovers and invokes Laravel Eloquent Policies.

### 4.1 Eloquent Policy Discovery
For model `Order`, Filament checks `OrderPolicy` methods:
- `viewAny(User $user)`: Controls visibility in navigation and access to list page.
- `view(User $user, Order $order)`: Controls view page and view action.
- `create(User $user)`: Controls create button and create page.
- `update(User $user, Order $order)`: Controls edit action and edit page.
- `delete(User $user, Order $order)`: Controls delete action.

### 4.2 Record Ownership Query Scoping
To prevent tenants or vendors from accessing other users' records, override `getEloquentQuery()` in the Resource class:

```php
use Illuminate\Database\Eloquent\Builder;

public static function getEloquentQuery(): Builder
{
    $query = parent::getEloquentQuery();
    $user = auth()->user();

    // Super-admin bypasses ownership scoping
    if ($user && $user->is_super_admin) {
        return $query;
    }

    // Tenant / vendor scope constraint
    return $query->where('vendor_id', $user->id);
}
```

---

## 5. Filament v3 vs. v4 Differences

| Feature | Filament v3 | Filament v4 |
| :--- | :--- | :--- |
| **Foundation** | Livewire v3, Tailwind CSS v3 | Livewire v3+, Tailwind CSS v4 |
| **PHP Requirements** | PHP 8.1+ | PHP 8.2+ / PHP 8.3 / PHP 8.4 |
| **Panel Registration** | Panel Provider architecture | Enhanced Panel Provider with native Sub-navigation |
| **Form Components** | Classic typed components | Stricter native PHP property typing, instant live hydration |
| **Table Actions** | Synchronous and modal actions | Streamlined slide-over drawer and async actions |
| **Asset Pipeline** | Standard Vite bundle compilation | Zero-configuration theme compilation |

---

## 6. Persian RTL & Localization (`rtl-fa`)

When implementing Persian or Arabic panels:
1. Set `$panel->locale('fa')` and register RTL direction.
2. Register local typography (e.g. Vazirmatn font) via local Vite assets without external CDN dependencies.
3. Replace standard date pickers with Jalali date components (using `morilog/jalali` for backend conversion).
4. Normalise currency displays to Toman or Rial with localized Persian digits.
