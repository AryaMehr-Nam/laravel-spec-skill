# Preset: Persian RTL & Localization (`rtl-fa`)

The `rtl-fa` preset configures Laravel and Filament v3/v4 applications for complete Persian (Farsi) Right-to-Left (RTL) layout, Solar Hijri (Jalali) date handling, localized number formatting, and 100% self-hosted typography with zero third-party CDN dependencies.

---

## 1. Architectural Principles

1. **Zero External CDN Dependencies**: All assets (Vazirmatn webfonts, icons, stylesheets) are self-hosted within the application repository or bundled via Vite. No requests to `fonts.googleapis.com`, `cdnjs.cloudflare.com`, or other external services are permitted, guaranteeing offline development capability, consistent latency, and immunity to regional connectivity drops or DNS filtering.
2. **Canonical Data Normalization**: Store data canonically in standard formats (Gregorian UTC timestamps in database datetime/timestamp columns, ASCII Latin numerals `0-9` in numeric columns). Localize strictly at the presentation layer (Filament tables, forms, notification toasts, PDF exports).
3. **Bi-directional Input Sanitization**: Automatically normalize Eastern Arabic (`٠١٢٣٤٥٦٧٨٩`) and Persian (`۰۱۲۳۴۵۶۷۸۹`) numerals to Latin digits on request entry to prevent validation, cast, or query failures in database engines.

---

## 2. Self-Hosted Typography & Styling

### 2.1 Font Installation via npm & Vite
Install the official Vazirmatn font package:

```bash
npm install vazirmatn --save
```

Import Vazirmatn in `resources/css/filament/admin/theme.css`:

```css
@import 'vazirmatn/misc/UI/Vazirmatn-UI-font-face.css';

:root {
    --font-family: 'Vazirmatn UI', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

body, html, .fi-body {
    font-family: var(--font-family);
    direction: rtl;
    text-align: right;
}

/* Persian digit styling for tabular data */
.font-tabular-nums {
    font-feature-settings: 'ss01';
}
```

Register the custom Vite theme in your panel provider:

```php
// app/Providers/Filament/AdminPanelProvider.php
namespace App\Providers\Filament;

use Filament\Panel;
use Filament\PanelProvider;
use Filament\Support\Colors\Color;

class AdminPanelProvider extends PanelProvider
{
    public function panel(Panel $panel): Panel
    {
        // NOTE: Do NOT call ->font('Vazirmatn UI') without a local provider, as Filament
        // defaults to querying Google Fonts CDN for unconfigured fonts.
        // The self-hosted Vazirmatn font is loaded exclusively via Vite theme.css below.
        return $panel
            ->default()
            ->id('admin')
            ->path('admin')
            ->viteTheme('resources/css/filament/admin/theme.css')
            ->colors([
                'primary' => Color::Amber,
            ]);
    }
}
```

---

## 3. Jalali (Shamsi) Date Handling

### 3.1 Recommended Package
Install `morilog/jalali` for high-performance Solar Hijri conversion:

```bash
composer require morilog/jalali:^3.4
```

### 3.2 Eloquent Cast & Model Formatting
Keep database columns as standard SQL `timestamp` or `date` columns (e.g. `created_at`, `published_at`). Expose Jalali accessors or custom casts for display:

```php
namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Morilog\Jalali\Jalalian;

class Order extends Model
{
    /**
     * Get Jalali representation of order creation time safely handling null dates.
     */
    public function getCreatedAtShamsiAttribute(): ?string
    {
        return $this->created_at ? Jalalian::fromDateTime($this->created_at)->format('Y/m/d H:i') : null;
    }
}
```

### 3.3 Filament Table Column Integration
Format table timestamps into Jalali dates without altering the underlying SQL sorting:

```php
use Filament\Tables\Columns\TextColumn;
use Morilog\Jalali\Jalalian;

TextColumn::make('created_at')
    ->label('تاریخ ثبت')
    ->formatStateUsing(fn ($state) => $state ? Jalalian::fromDateTime($state)->format('Y/m/d H:i') : '-')
    ->sortable();
```

---

## 4. Numeral Conversion & Input Normalization

### 4.1 Numeral Translation Helper
Create `app/Support/PersianNumber.php`:

```php
namespace App\Support;

class PersianNumber
{
    protected static array $eastern = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹'];
    protected static array $arabic  = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩'];
    protected static array $latin   = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'];

    /**
     * Convert Latin digits to Persian digits for display.
     */
    public static function toPersian(string|int|float|null $value): string
    {
        if ($value === null) {
            return '';
        }
        return str_replace(static::$latin, static::$eastern, (string) $value);
    }

    /**
     * Normalize Persian and Eastern-Arabic digits to standard Latin digits for storage/querying.
     */
    public static function toLatin(string|int|float|null $value): string
    {
        if ($value === null) {
            return '';
        }
        $str = str_replace(static::$eastern, static::$latin, (string) $value);
        return str_replace(static::$arabic, static::$latin, $str);
    }
}
```

### 4.2 Global Request Normalization Middleware
Normalize all incoming request payloads (phones, prices, National IDs) to Latin digits before running validation rules, protecting sensitive password fields from character mutation:

```php
namespace App\Http\Middleware;

use App\Support\PersianNumber;
use Closure;
use Illuminate\Http\Request;

class NormalizePersianNumbers
{
    /**
     * Input fields excluded from numeral normalization.
     */
    protected array $except = [
        'password',
        'password_confirmation',
        'current_password',
    ];

    public function handle(Request $request, Closure $next)
    {
        $input = $request->all();
        array_walk_recursive($input, function (&$item, $key) {
            if (is_string($item) && ! in_array($key, $this->except, true)) {
                $item = PersianNumber::toLatin($item);
            }
        });
        $request->merge($input);

        return $next($request);
    }
}
```

---

## 5. Specification Schema Integration

Incorporate `rtl-fa` in your `spec/spec.json`:

```json
{
  "project": {
    "name": "فروشگاه آنلاین",
    "description": "پلتفرم مدیریت سفارشات و محصولات با پشتیبانی کامل از زبان فارسی",
    "locale": "fa",
    "timezone": "Asia/Tehran",
    "laravel_version": "12",
    "filament_version": "v3",
    "presets": [
      "rtl-fa"
    ]
  }
}
```

## 6. Verification Checklist

- [ ] All Filament views render with HTML attribute `<html dir="rtl" lang="fa">`.
- [ ] No outbound requests to external CDNs (`fonts.googleapis.com`, `cdn.jsdelivr.net`, etc.) in network tab.
- [ ] Dates render as Solar Hijri (e.g. `۱۴۰۳/۰۸/۱۲`) in Filament resource tables.
- [ ] Form submission containing Persian digits (e.g., `۰۹۱۲۱۲۳۴۵۶۷`) converts cleanly to ASCII (`09121234567`) without validation failure.
