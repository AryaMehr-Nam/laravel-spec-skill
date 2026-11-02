# Preset: Iranian Payment Gateways (`iran-payments`)

The `iran-payments` preset standardizes multi-gateway payment processing across popular Iranian PSPs and payment aggregators, specifically **Zarinpal**, **Shepa**, and **Saman (SEP / Shaparak)**. It enforces double-spend prevention, strict Rial/Toman conversion rules, idempotent webhook/callback handling, and atomic database state transitions.

---

## 1. Architectural Principles

1. **Strict Currency Normalization (The Toman/Rial Golden Rule)**:
   - Database tables **must** store financial figures in a single canonical unit across the entire system.
   - Recommended standard: Store amounts in **Tomans** (e.g. `decimal(14, 0)` or `bigInteger`) or **Rials** consistently.
   - Bank PSPs (e.g., Saman SEP) operate natively in **Rials**. Fintech aggregators (e.g., Zarinpal REST v4, Shepa) typically expect **Tomans** or accept either with an explicit currency parameter.
   - Normalization occurs exclusively at the gateway adapter boundary.
2. **Double-Spend Prevention via Idempotency & Pessimistic Locks**:
   - Each payment attempt is assigned a client-generated UUID `idempotency_key` indexed uniquely.
   - Payment callback verification routes wrap logic in database transactions with `lockForUpdate()`.
   - Repeated callbacks for an already `verified` transaction return the receipt idempotently without executing downstream fulfillment actions twice.
3. **Audit Trail & State Machine Isolation**:
   - Transitions follow: `initiated` -> `redirected` -> `verified` (terminal) or `failed` (terminal).
   - Masked card PAN (`card_pan_masked`, e.g., `6037-99**-****-1234`) and gateway tracking references (`ref_id`, `authority`, `rrn`) are persisted for reconciliation and fraud investigation.

---

## 2. Currency Conversion Strategy

Create a dedicated currency value object or helper `app/Support/Money.php`:

```php
namespace App\Support;

class Money
{
    /**
     * Convert Tomans to Rials (1 Toman = 10 Rials).
     */
    public static function tomanToRial(int $tomans): int
    {
        return $tomans * 10;
    }

    /**
     * Convert Rials to Tomans.
     */
    public static function rialToToman(int $rials): int
    {
        return (int) intdiv($rials, 10);
    }

    /**
     * Format Tomans for display with Persian separators.
     */
    public static function formatToman(int $tomans): string
    {
        return number_format($tomans) . ' تومان';
    }
}
```

---

## 3. Gateway Adapter Contract

Define a unified gateway interface in `app/Contracts/PaymentGatewayInterface.php`:

```php
namespace App\Contracts;

use App\Models\Payment;
use Illuminate\Http\Request;

interface PaymentGatewayInterface
{
    /**
     * Request a payment token/authority and redirect URL.
     */
    public function requestPayment(Payment $payment, string $callbackUrl): PaymentRedirectResponse;

    /**
     * Verify transaction upon customer callback from Shaparak.
     */
    public function verifyPayment(Payment $payment, Request $request): PaymentVerificationResult;
}
```

### 3.1 Gateway Reference Implementations

- **Zarinpal (REST API v4)**:
  - Request URL: `https://payment.zarinpal.com/pg/v4/payment/request.json`
  - Currency: `IRT` (Tomans) or `IRR` (Rials)
  - Verification URL: `https://payment.zarinpal.com/pg/v4/payment/verify.json`
  - Success Code: `code == 100` (First verification), `code == 101` (Verified previously - idempotent)
- **Shepa**:
  - Request URL: `https://merchant.shepa.com/api/v1/token`
  - Verification URL: `https://merchant.shepa.com/api/v1/verify`
  - Success status: `success == true`
- **Saman Electronic Payment (SEP / Shaparak)**:
  - Gateway Type: Direct Bank PSP
  - Currency: Strictly `IRR` (Rials)
  - Token Endpoint: `https://sep.shaparak.ir/OnlinePG/OnlinePG`
  - Verification SOAP/REST API: `https://sep.shaparak.ir/verifyTxnRandomToken`

---

## 4. Atomic Callback Controller with Lock

Implement callback handling with concurrency protection:

```php
namespace App\Http\Controllers;

use App\Models\Payment;
use App\Services\PaymentManager;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Symfony\Component\HttpKernel\Exception\ConflictHttpException;

class PaymentCallbackController extends Controller
{
    public function handle(string $authority, Request $request, PaymentManager $manager)
    {
        return DB::transaction(function () use ($authority, $request, $manager) {
            /** @var Payment $payment */
            $payment = Payment::where('authority', $authority)
                ->lockForUpdate()
                ->firstOrFail();

            // Idempotent return if already processed
            if ($payment->status === 'verified') {
                return redirect()->route('orders.receipt', [
                    'order' => $payment->order_id,
                    'status' => 'already_verified',
                ]);
            }

            if ($payment->status !== 'redirected') {
                throw new ConflictHttpException('Invalid payment state for verification.');
            }

            $driver = $manager->driver($payment->gateway);
            $result = $driver->verifyPayment($payment, $request);

            if ($result->isSuccessful()) {
                $payment->update([
                    'status' => 'verified',
                    'ref_id' => $result->getRefId(),
                    'tracking_code' => $result->getTrackingCode(),
                    'card_pan_masked' => $result->getMaskedCard(),
                    'verified_at' => now(),
                ]);

                // Fulfill order
                $payment->order->update(['status' => 'paid']);

                return redirect()->route('orders.receipt', ['order' => $payment->order_id]);
            }

            $payment->update([
                'status' => 'failed',
                'failure_reason' => $result->getErrorMessage(),
            ]);

            return redirect()->route('orders.failed', ['order' => $payment->order_id]);
        });
    }
}
```

---

## 5. Specification Schema Integration

Incorporate `iran-payments` into `spec/spec.json`:

```json
{
  "project": {
    "presets": ["iran-payments"]
  },
  "models": [
    {
      "name": "Payment",
      "table": "payments",
      "fields": [
        { "name": "id", "type": "bigInteger" },
        { "name": "order_id", "type": "bigInteger", "index": true, "foreign": { "model": "Order" } },
        { "name": "user_id", "type": "bigInteger", "index": true, "foreign": { "model": "User" } },
        { "name": "gateway", "type": "string" },
        { "name": "amount", "type": "decimal", "precision": 14, "scale": 0 },
        { "name": "authority", "type": "string", "index": true },
        { "name": "ref_id", "type": "string", "nullable": true },
        { "name": "tracking_code", "type": "string", "nullable": true },
        { "name": "card_pan_masked", "type": "string", "nullable": true },
        { "name": "idempotency_key", "type": "string", "unique": true },
        { "name": "status", "type": "string" }
      ],
      "states": {
        "field": "status",
        "initial": "initiated",
        "final": ["reversed", "failed"],
        "transitions": [
          { "from": "initiated", "to": "redirected", "roles": ["customer", "super-admin"] },
          { "from": "redirected", "to": "verified", "roles": ["*"] },
          { "from": "redirected", "to": "failed", "roles": ["*"] },
          { "from": "verified", "to": "reversed", "roles": ["super-admin"] }
        ]
      }
    }
  ],
  "integrations": [
    {
      "name": "zarinpal",
      "kind": "payments",
      "config_notes": "ZARINPAL_MERCHANT_ID, ZARINPAL_SANDBOX=false, ZARINPAL_CURRENCY=IRT"
    },
    {
      "name": "saman",
      "kind": "payments",
      "config_notes": "SEP_TERMINAL_ID, SEP_PASSWORD, SEP_BASE_URL"
    }
  ]
}
```

---

## 6. Verification Checklist

- [ ] Financial column `amount` uses `decimal` with explicit precision/scale or `bigInteger` (never `float`).
- [ ] `idempotency_key` column is indexed with `unique: true`.
- [ ] Callback processing executes inside a database transaction with `lockForUpdate()`.
- [ ] Gateway response codes `100` and `101` (Zarinpal) are handled distinctly without double fulfillment.
- [ ] Conversion between Rials and Tomans occurs solely within gateway driver adapters.
