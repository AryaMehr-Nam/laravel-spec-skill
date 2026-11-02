# Preset: SMS OTP Authentication (`otp-login`)

The `otp-login` preset provides a production-grade, passwordless authentication pipeline using Short Message Service (SMS) One-Time Passwords (OTP). It specifies strict security constraints: a 120-second code lifespan, single-use cryptographic nonces, granular rate limiting, user enumeration defense, and Filament panel authentication integration.

---

## 1. Security Architecture & Threat Model

1. **Short Expiry Window (120 Seconds)**:
   - Challenge codes expire exactly 120 seconds after dispatch.
   - Database timestamp verification (`expires_at < now()`) prevents replay or delayed brute-force guessing.
2. **Single-Use Cryptographic Nonce**:
   - Every verification attempt is coupled to a unique challenge nonce/token returned in Step 1.
   - The OTP code is either hashed (Bcrypt / HMAC-SHA256) or stored securely and destroyed immediately upon first verification or after reaching max attempt thresholds (3 incorrect guesses).
3. **Multi-Tiered Rate Limiting**:
   - **Per Phone**: 1 SMS dispatch per 60 seconds (resend cooldown); maximum 5 requests per phone number per hour.
   - **Per IP Address**: Maximum 10 OTP requests per 10 minutes to defend against SMS pump fraud and denial-of-wallet attacks.
   - **Verification Attempts**: Maximum 3 code submission attempts per challenge before the challenge is permanently revoked.
4. **User Enumeration Defense**:
   - The API response for requesting an OTP code returns an identical structure and timing signature regardless of whether the mobile number exists in the database.
   - Response message: *"If this mobile number is eligible, a 5-digit verification code has been dispatched."*
5. **Pattern-Based SMS Provider Routing**:
   - Uses approved SMS template patterns (e.g. via Kavenegar, Ghasedak, or FarazSMS) to ensure instant transit past national telecommunication DND (Do-Not-Disturb / Blacklist) filters.

---

## 2. Authentication Flow

```
[Client]                      [Laravel App / Filament]               [SMS Gateway (Kavenegar)]
   |                                     |                                      |
   |-- 1. POST /otp/send (phone) ------->|                                      |
   |                                     |-- Check Rate Limits (Redis/Cache)    |
   |                                     |-- Generate 5-digit code + Nonce      |
   |                                     |-- Store Hashed OTP (TTL: 120s)       |
   |                                     |-- Dispatch Pattern SMS ------------->|
   |<-- 2. Return {nonce, expires_in:120}|                                      |
   |                                                                            |
   |-- 3. POST /otp/verify ------------->|                                      |
   |      (nonce, code)                  |-- Check Nonce & Expiry (<= 120s)     |
   |                                     |-- Constant-Time Hash Check           |
   |                                     |-- Delete / Revoke OTP Challenge      |
   |                                     |-- Login / Issue Session or Sanctum   |
   |<-- 4. Auth Cookie / Token ----------|                                      |
```

---

## 3. Implementation Blueprint

### 3.1 Rate Limiting Service Provider
Configure rate limiters in `app/Providers/AppServiceProvider.php`:

```php
namespace App\Providers;

use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\RateLimiter;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    public function boot(): void
    {
        RateLimiter::for('otp-send', function (Request $request) {
            $phone = preg_replace('/[^0-9]/', '', (string) $request->input('phone'));
            $ip = $request->ip();

            return [
                Limit::perMinute(1)->by("phone:{$phone}")->response(fn () => response()->json([
                    'message' => 'Please wait before requesting another code.',
                    'retry_after' => 60,
                ], 429)),
                Limit::perHour(5)->by("phone_hourly:{$phone}"),
                Limit::perMinutes(10, 10)->by("ip:{$ip}"),
            ];
        });

        RateLimiter::for('otp-verify', function (Request $request) {
            $nonce = (string) $request->input('nonce');
            return Limit::perMinute(5)->by("verify:{$nonce}");
        });
    }
}
```

### 3.2 Challenge Verification Service
Implement `app/Services/OtpService.php`:

```php
namespace App\Services;

use App\Models\User;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Str;
use Symfony\Component\HttpKernel\Exception\BadRequestHttpException;

class OtpService
{
    const EXPIRY_SECONDS = 120;
    const MAX_ATTEMPTS = 3;

    public function createChallenge(string $phone): string
    {
        $nonce = Str::random(40);
        $code = (string) random_int(10000, 99999);

        Cache::put("otp:{$nonce}", [
            'phone' => $phone,
            'code_hash' => hash('sha256', $code),
            'attempts' => 0,
            'expires_at' => now()->addSeconds(self::EXPIRY_SECONDS)->timestamp,
        ], self::EXPIRY_SECONDS);

        // Dispatch via SMS integration driver (e.g. Kavenegar pattern)
        app(SmsGatewayContract::class)->sendPattern($phone, 'login_template', ['code' => $code]);

        return $nonce;
    }

    public function verify(string $nonce, string $code): User
    {
        $data = Cache::get("otp:{$nonce}");
        if (! $data) {
            throw new BadRequestHttpException('Verification code has expired or is invalid.');
        }

        if (now()->timestamp > $data['expires_at']) {
            Cache::forget("otp:{$nonce}");
            throw new BadRequestHttpException('Verification code has expired.');
        }

        // Check attempts
        if ($data['attempts'] >= self::MAX_ATTEMPTS) {
            Cache::forget("otp:{$nonce}");
            throw new BadRequestHttpException('Too many invalid attempts. Request a new code.');
        }

        $inputHash = hash('sha256', $code);
        if (! hash_equals($data['code_hash'], $inputHash)) {
            $data['attempts']++;
            Cache::put("otp:{$nonce}", $data, self::EXPIRY_SECONDS);
            throw new BadRequestHttpException('Invalid verification code.');
        }

        // Invalidate challenge immediately (single-use)
        Cache::forget("otp:{$nonce}");

        // Find or provision user
        return User::firstOrCreate(
            ['phone' => $data['phone']],
            ['name' => 'User ' . substr($data['phone'], -4)]
        );
    }
}
```

---

## 4. Filament Custom Login Page Integration

Configure your Filament panel provider to use an OTP-enabled login page:

```php
// app/Providers/Filament/AppPanelProvider.php
use App\Filament\Pages\Auth\OtpLogin;

public function panel(Panel $panel): Panel
{
    return $panel
        ->id('app')
        ->path('app')
        ->login(OtpLogin::class);
}
```

---

## 5. Specification Schema Integration

Incorporate `otp-login` into `spec/spec.json`:

```json
{
  "project": {
    "presets": ["otp-login"],
    "audit_log": true
  },
  "models": [
    {
      "name": "User",
      "table": "users",
      "fields": [
        { "name": "id", "type": "bigInteger" },
        { "name": "name", "type": "string" },
        { "name": "phone", "type": "string", "unique": true, "pii": true },
        { "name": "phone_verified_at", "type": "datetime", "nullable": true }
      ]
    },
    {
      "name": "OtpChallenge",
      "table": "otp_challenges",
      "fields": [
        { "name": "id", "type": "bigInteger" },
        { "name": "nonce", "type": "string", "unique": true },
        { "name": "phone", "type": "string", "index": true, "pii": true },
        { "name": "code_hash", "type": "string" },
        { "name": "attempts", "type": "integer", "default": 0 },
        { "name": "expires_at", "type": "datetime", "index": true }
      ]
    }
  ],
  "integrations": [
    {
      "name": "kavenegar",
      "kind": "sms",
      "config_notes": "KAVENEGAR_API_KEY, KAVENEGAR_VERIFY_TEMPLATE"
    },
    {
      "name": "activity_log",
      "kind": "audit_log"
    }
  ]
}
```

---

## 6. Verification Checklist

- [ ] Challenge lifetime strictly limited to 120 seconds.
- [ ] Challenge nonce immediately deleted upon verification success or threshold exhaustion.
- [ ] Constant-time comparison (`hash_equals`) utilized during verification.
- [ ] Rate limiters active on both `/otp/send` and `/otp/verify`.
- [ ] Response body for phone lookup is indistinguishable between existing and non-existing accounts.
- [ ] Phone numbers marked `pii: true` with audit logging enabled.
