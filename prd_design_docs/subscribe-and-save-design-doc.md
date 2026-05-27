# Design Doc: Subscribe & Save
**Status:** Draft  **Author:** Engineering Team  **Date:** 2026-05-26

## Background

Online Boutique currently has no concept of a recurring order, a saved payment method, or a persistent user account. Every checkout is a stateless, one-time transaction: `checkoutservice` orchestrates a multi-step flow (cart → catalog → currency → shipping → payment → email → empty cart), returns an `OrderResult` in memory, and discards all state when the response completes. There is no order history, no account ID, and no mechanism to re-charge a user at a future date.

Subscribe & Save requires all three capabilities that the current system deliberately omits: persistent user identity (to associate a subscription with a person across sessions), tokenized payment storage (to charge a card on a future date without re-collecting card details), and a background scheduler (to trigger renewal orders independently of the live checkout path). This design covers the engineering approach for all three, plus the subscription management surface.

## Current State

### What exists today

**Checkout flow (`checkoutservice`, port 5050):**
1. `CartService.GetCart`
2. `ProductCatalogService.GetProduct` (per cart item)
3. `CurrencyService.Convert`
4. `ShippingService.GetQuote` → `ShippingService.ShipOrder`
5. `PaymentService.Charge` — validates card format, returns a mock UUID transaction ID
6. `EmailService.SendOrderConfirmation` — renders a confirmation email template and logs it; nothing is actually sent
7. `CartService.EmptyCart`

**User identity:** The session identifier is a UUID stored in the `shop_session-id` cookie, generated fresh by `frontend` for each visitor. There is no login, no account model, and no mechanism to link two sessions to the same person. The session UUID is passed as `user_id` throughout the gRPC call chain.

**Payment service (`paymentservice`, port 50051):** Accepts a `ChargeRequest` containing the full `CreditCardInfo` (number, CVV, expiration). Validates card format and expiration. Returns a generated transaction UUID. Does not store any card data. Cannot charge a saved card — it has no notion of a saved card.

**Email service (`emailservice`, port 8080 gRPC):** Renders an order confirmation HTML template using Jinja2 and logs the rendered output to stdout. Does not connect to any SMTP server or email delivery provider. Cannot send real email.

**Product catalog:** 9 products defined in `src/productcatalogservice/products.json`, a static file baked into the container image at build time. The `Product` proto message has no `subscription_eligible` field. The category taxonomy is a closed set: `accessories`, `clothing`, `tops`, `footwear`, `hair`, `beauty`, `decor`, `home`, `kitchen`.

**Storage:** The only persistent (optional) store is `redis-cart` (Redis, port 6379), which holds cart state keyed by `user_id`. The default deployment uses an ephemeral in-cluster pod — cart data is lost on pod restart. There is no relational database anywhere in the system.

### What does NOT exist today
- No user accounts, login, or persistent identity
- No stored payment methods or payment tokens
- No subscription records or renewal scheduling
- No background job runner or worker queue
- No real email delivery
- No `subscription_eligible` flag on products
- No discount logic of any kind (prices are fixed at catalog values)

---

## Proposed Solution

### 1. New service: SubscriptionService

A new Go microservice `subscriptionservice` (port `7080`) is the source of truth for all subscription records. It owns the subscription lifecycle: creation, cadence management, skip/pause/cancel, and the renewal event log.

```protobuf
service SubscriptionService {
  rpc CreateSubscription(CreateSubscriptionRequest) returns (CreateSubscriptionResponse);
  rpc GetSubscriptions(GetSubscriptionsRequest) returns (GetSubscriptionsResponse);
  rpc UpdateSubscription(UpdateSubscriptionRequest) returns (UpdateSubscriptionResponse);
  rpc CancelSubscription(CancelSubscriptionRequest) returns (CancelSubscriptionResponse);
  rpc SkipNextDelivery(SkipNextDeliveryRequest) returns (SkipNextDeliveryResponse);
  rpc ListDueRenewals(ListDueRenewalsRequest) returns (ListDueRenewalsResponse);  // called by renewal worker
}

message Subscription {
  string subscription_id  = 1;
  string account_id       = 2;   // persistent account ID — NOT session UUID
  string product_id       = 3;
  int32  quantity         = 4;
  int32  cadence_days     = 5;   // one of: 7, 14, 30, 60, 90, 180
  string status           = 6;   // ACTIVE | PAUSED | SUSPENDED | CANCELLED
  int64  next_renewal_unix = 7;
  int64  price_lock_until_unix = 8;  // price locked until this timestamp (6 months from creation)
  Money  locked_price_usd = 9;   // catalog price at time of subscription, in USD
  string payment_token    = 10;  // opaque token from payment vault; NOT a card number
  Address shipping_address = 11;
  string currency_code    = 12;  // user's display currency at subscription time
  float  discount_pct     = 13;  // e.g. 0.10 for 10% off
}

message CreateSubscriptionRequest {
  string account_id      = 1;
  string product_id      = 2;
  int32  quantity        = 3;
  int32  cadence_days    = 4;
  string payment_token   = 5;
  Address shipping_address = 6;
  string currency_code   = 7;
}

message ListDueRenewalsRequest {
  int64 as_of_unix = 1;  // renewal worker passes current time; service returns subscriptions where next_renewal_unix <= as_of_unix
}
```

`SubscriptionService` is backed by a PostgreSQL database (see Data Model). It is reachable from `frontend` (read/write subscription management) and the renewal worker (read due renewals, update after renewal attempt).

---

### 2. Renewal Worker (new background process)

A separate Go process `subscription-renewal-worker` runs as a Kubernetes `CronJob` on a configurable interval (default: every 15 minutes). It does NOT run inside `checkoutservice`.

**Renewal loop:**
1. Call `SubscriptionService.ListDueRenewals(as_of_unix=now)` to get all subscriptions with `next_renewal_unix <= now` and `status=ACTIVE`.
2. For each subscription, acquire a distributed lock (Redis) on `subscription_id` to prevent duplicate processing if two worker pods run simultaneously.
3. Determine the charge amount: if `now < price_lock_until_unix`, use `locked_price_usd`; otherwise fetch current price from `ProductCatalogService.GetProduct` and re-price.
4. Apply `discount_pct` to the charge amount.
5. Call the payment vault API directly (not through `paymentservice`) to charge `payment_token`.
6. On payment success: call `ShippingService.ShipOrder` to generate a tracking ID, call `EmailService.SendOrderConfirmation`, update `next_renewal_unix` in `SubscriptionService`, release lock.
7. On payment failure: record the attempt in `subscription_events`. If this is attempt 1 or 2, schedule retry on day +2. If this is attempt 3 (day 5), set `status=SUSPENDED`, send a failed-payment email, release lock.

Each renewal attempt carries an idempotency key: `sha256(subscription_id + renewal_date)`. The payment vault must reject duplicate charges with the same idempotency key. This prevents double-charges on worker retry.

---

### 3. Changes to `frontend`

**Cart page — subscribe toggle:**
- For each cart item whose product has `subscription_eligible=true`, render a "Subscribe & Save" toggle below the quantity selector.
- When toggled on, show a cadence picker (7 / 14 / 30 / 60 / 90 / 180 days) and the applicable discount percentage for that product's category.
- The selected cadence and opt-in flag are passed to `checkoutservice` as part of the checkout form submission.

**Checkout flow — subscription creation:**
- If the user opted into a subscription for one or more items, `frontend` calls `SubscriptionService.CreateSubscription` after `checkoutservice.PlaceOrder` succeeds. The payment token (returned by the payment vault after the initial checkout charge) is stored with the subscription record at this point.
- Guest users (no `account_id`) cannot subscribe. The subscribe toggle is hidden for non-authenticated users.

**New page: `/subscriptions` — subscription dashboard:**
- Lists all active, paused, and suspended subscriptions for the logged-in user.
- Each subscription card shows: product name, cadence, next renewal date, price (with discount), and action buttons (Skip Next, Change Cadence, Pause, Cancel).
- Cancel flow: one click on "Cancel", one confirmation modal, one final "Confirm Cancel" button. Three interactions total — compliant with FTC click-to-cancel.
- Calls `SubscriptionService.GetSubscriptions`, `SubscriptionService.SkipNextDelivery`, `SubscriptionService.UpdateSubscription`, `SubscriptionService.CancelSubscription`.

---

### 4. Changes to `productcatalogservice`

Add `bool subscription_eligible = 7` and `float subscription_discount_pct = 8` to the `Product` proto message.

```protobuf
message Product {
  string id                      = 1;
  string name                    = 2;
  string description             = 3;
  string picture                 = 4;
  Money  price_usd               = 5;
  repeated string categories     = 6;
  bool   subscription_eligible   = 7;   // NEW
  float  subscription_discount_pct = 8; // NEW: e.g. 0.10 for 10% off
}
```

`products.json` is updated to include these fields per product. The service is rebuilt and redeployed. Existing callers (`frontend`, `checkoutservice`, `recommendationservice`) that do not read fields 7–8 are unaffected (proto3 zero values: `false` and `0.0`).

---

### 5. Changes to `paymentservice`

`paymentservice` currently accepts full `CreditCardInfo` on every call and does not store card data. For subscriptions, the initial checkout charge must also tokenize the card and return a reusable token for future renewal charges.

Two options are under evaluation:
- **Option A:** Extend `paymentservice` to integrate with a PCI-DSS compliant payment vault (e.g., Stripe, Braintree). The vault stores the card and returns a token. `paymentservice` passes the token to the renewal worker on initial charge.
- **Option B:** The frontend tokenizes the card directly via the vault's client-side SDK before submitting checkout. The token is passed to `checkoutservice` instead of raw card data. This removes raw card data from the gRPC path entirely.

Option B is preferred for PCI scope reduction. Decision pending payment provider selection (see Open Questions).

Under either option, the `ChargeRequest` message gains an optional `payment_token` field for token-based charges (used by the renewal worker), making raw card data optional when a token is available:

```protobuf
message ChargeRequest {
  Money          amount      = 1;
  CreditCardInfo credit_card = 2;   // used for initial checkout (if tokenizing server-side)
  string         payment_token = 3; // NEW: used for renewal charges; mutually exclusive with credit_card
}

message ChargeResponse {
  string transaction_id = 1;
  string payment_token  = 2;  // NEW: returned on initial charge; stored by SubscriptionService
}
```

---

### 6. Changes to `emailservice`

`emailservice` currently renders a Jinja2 template and logs the output. For subscription renewals, it must deliver real email. A transactional email provider (e.g., SendGrid, Amazon SES) must be integrated. The gRPC interface (`SendOrderConfirmation`) remains unchanged. The implementation behind it changes from "log to stdout" to "POST to email provider API."

Two new email templates are added:
- **Failed payment notification:** informs subscriber that their renewal charge failed and provides a link to update their payment method.
- **Price re-pricing notice:** sent 14 days before a price-lock expiry, showing the upcoming new price.

---

## Affected Services

| Service | Change |
|---|---|
| `frontend` | New subscribe toggle on cart page; new `/subscriptions` dashboard page; passes subscription opt-in to checkout; calls `SubscriptionService` after successful `PlaceOrder` |
| `checkoutservice` | Passes `account_id` from request (new field 7 on `PlaceOrderRequest`); otherwise unchanged — subscription creation happens after PlaceOrder returns, not inside it |
| `productcatalogservice` | New fields `subscription_eligible` (field 7) and `subscription_discount_pct` (field 8) on `Product`; `products.json` updated |
| `paymentservice` | New optional `payment_token` field on `ChargeRequest` and `ChargeResponse`; real payment vault integration required |
| `emailservice` | Real transactional email delivery required; new failed-payment and re-pricing templates; gRPC interface unchanged |
| `subscriptionservice` | **New service** — owns subscription records, lifecycle management, renewal scheduling |
| `subscription-renewal-worker` | **New background process** — CronJob; calls SubscriptionService, payment vault, ShippingService, EmailService |
| `cartservice` | No changes |
| `currencyservice` | No changes |
| `shippingservice` | No changes — renewal worker calls `ShipOrder` directly |
| `recommendationservice` | No changes |
| `adservice` | No changes |
| `redis-cart` | Used for distributed locking in renewal worker (separate key namespace); no changes to cart behavior |

---

## API / Proto Changes

1. **`Product` message:** add `bool subscription_eligible = 7` and `float subscription_discount_pct = 8`. Backward compatible (proto3 zero values).
2. **`PlaceOrderRequest`:** add `string account_id = 7` (new field; empty string = guest, skips subscription creation). Field 4 remains reserved and must not be used.
3. **`ChargeRequest`:** add `string payment_token = 3`. Mutually exclusive with `credit_card`; the caller sets one or the other.
4. **`ChargeResponse`:** add `string payment_token = 2`. Populated on initial tokenizing charge; empty for guest checkout.
5. **New file `subscriptionservice.proto`:** defines `SubscriptionService` and all subscription messages listed above.

---

## Data Model

PostgreSQL database `subscriptions` (owned by `subscriptionservice`):

```sql
CREATE TABLE subscriptions (
  subscription_id       TEXT PRIMARY KEY,
  account_id            TEXT NOT NULL,
  product_id            TEXT NOT NULL,
  quantity              INT NOT NULL DEFAULT 1,
  cadence_days          INT NOT NULL,
  status                TEXT NOT NULL DEFAULT 'ACTIVE',  -- ACTIVE | PAUSED | SUSPENDED | CANCELLED
  next_renewal_unix     BIGINT NOT NULL,
  price_lock_until_unix BIGINT NOT NULL,
  locked_price_units    BIGINT NOT NULL,
  locked_price_nanos    INT NOT NULL,
  locked_price_currency TEXT NOT NULL DEFAULT 'USD',
  payment_token         TEXT NOT NULL,   -- opaque vault token; NOT a card number
  shipping_address      JSONB NOT NULL,
  currency_code         TEXT NOT NULL,
  discount_pct          NUMERIC(5,4) NOT NULL DEFAULT 0,
  created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sub_account    ON subscriptions (account_id);
CREATE INDEX idx_sub_renewals   ON subscriptions (next_renewal_unix) WHERE status = 'ACTIVE';

CREATE TABLE subscription_events (
  event_id          TEXT PRIMARY KEY,
  subscription_id   TEXT NOT NULL REFERENCES subscriptions(subscription_id),
  event_type        TEXT NOT NULL,  -- RENEWAL_SUCCESS | RENEWAL_FAILURE | SKIPPED | PAUSED | CANCELLED | REPRICED
  occurred_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  attempt_number    INT,            -- for RENEWAL_FAILURE
  charge_amount_units BIGINT,
  charge_amount_nanos INT,
  idempotency_key   TEXT UNIQUE,    -- sha256(subscription_id + renewal_date)
  notes             TEXT
);

CREATE INDEX idx_events_sub ON subscription_events (subscription_id, occurred_at DESC);
```

---

## Deployment Plan

1. **Deploy `subscriptionservice`** with its Postgres instance. No traffic yet. Verify health probes.
2. **Deploy updated `productcatalogservice`** with fields 7–8 on `Product`. All existing callers unaffected (zero values). Catalog ops team updates `products.json` to flag subscription-eligible products.
3. **Deploy updated `paymentservice`** with payment vault integration and new `payment_token` fields. Guest checkout path unchanged.
4. **Deploy updated `emailservice`** with transactional email provider integration. Verify delivery with staging email addresses.
5. **Deploy updated `frontend`** with subscribe toggle (hidden behind feature flag) and `/subscriptions` dashboard (auth-gated). No visible change until auth ships.
6. **Deploy updated `checkoutservice`** with `account_id` field 7 on `PlaceOrderRequest`. Guest checkout path unchanged.
7. **Ship auth/account system** (external dependency). Enable `account_id` propagation end-to-end.
8. **Enable subscribe toggle** via feature flag. Begin A/B test of discount tiers.
9. **Deploy `subscription-renewal-worker`** CronJob. Monitor first renewal cycle closely.
10. **Rollback:** Steps 2–6 are all backward compatible. Rolling back any individual service does not break others. The renewal worker can be disabled by deleting the CronJob without affecting live checkout.

---

## Risks & Open Questions

**No user account system exists today.** Subscribe & Save requires a persistent `account_id` to associate subscriptions with a customer across sessions. The current session model (ephemeral UUID cookie) cannot support this. The auth/account system is an external hard dependency — this feature cannot reach production without it. Steps 1–6 of the deployment plan can proceed safely, but the feature is inert until auth ships.

**Payment vault selection is unresolved.** The renewal worker charges cards using a stored token. `paymentservice` today is a mock with no vault integration and no token storage. Selecting, contracting, and integrating a PCI-DSS compliant vault (Stripe, Braintree, Adyen, or equivalent) is a significant engineering effort with its own timeline. Until a vault is selected, automated billing cannot be built or tested.

**`emailservice` sends no real email today.** The subscription failed-payment recovery flow and price re-pricing notice depend on email delivery. Integrating a transactional email provider into `emailservice` changes it from a stateless logger to a service with an external network dependency, adding a new failure mode to the renewal path.

**Renewal worker idempotency depends on vault-side enforcement.** The worker issues charges with an idempotency key, but the guarantee that a duplicate charge does not occur rests on the payment vault correctly honoring that key. If the vault does not support idempotency keys (or enforces them with a short TTL), duplicate charges are possible on worker retry. This must be verified during vault selection.

**`PlaceOrderRequest` field 7 for `account_id`.** Field 4 on `PlaceOrderRequest` is reserved from a past removal and must never be reused. Field 7 is the next available number and is used here for `account_id`. All existing callers that do not send field 7 will receive `account_id=""` (proto3 zero value), which routes to the guest checkout path with no behavior change.

**Price re-pricing notification.** The 14-day re-pricing notice is sent by the renewal worker via `emailservice`. If `emailservice` is unavailable on the day the notice is due, the notice is not sent and there is no retry. Subscribers subject to re-pricing may be charged a new price without advance notice. A retry mechanism for notification events is deferred to v2.
