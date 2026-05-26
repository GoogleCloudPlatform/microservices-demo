# Design Doc: Persistent Order History
**Status:** Draft  **Author:** Engineering Team  **Date:** 2026-05-26

## Background

Online Boutique has no order persistence today. The `PlaceOrder` RPC in `checkoutservice` orchestrates a multi-step checkout — get cart, get product details, convert currency, get shipping quote, ship order, charge payment, send email confirmation, empty cart — and returns an `OrderResult` struct containing an order ID and shipping tracking ID. That struct exists only in memory for the lifetime of the gRPC response. Once `frontend` renders the confirmation page, the order is gone.

User identity is similarly ephemeral. There are no user accounts. The session identifier is a UUID stored in the `shop_session-id` cookie. Each new browser session (or cleared cookies) generates a fresh UUID. There is no mechanism to associate a session UUID with a person across time or devices.

This design covers adding persistent order storage, a new `OrderHistoryService`, integration with `checkoutservice`, and a new frontend page. It explicitly does **not** cover the login/account system — that is treated as a hard external dependency.

## Current State

### PlaceOrder execution order (checkoutservice)
1. `CartService.GetCart`
2. `ProductCatalogService.GetProduct` — one call per cart line item
3. `CurrencyService.Convert` — convert each item price to the user's selected currency
4. `ShippingService.GetQuote`
5. `ShippingService.ShipOrder`
6. `PaymentService.Charge` — money moves here; point of no return
7. `EmailService.SendOrderConfirmation` — failure is silently swallowed; no retry
8. `CartService.EmptyCart`

The `PlaceOrderRequest` proto currently carries:
- `user_id` (field 1) — this is the session UUID, not a persistent account ID
- `user_currency` (field 2)
- `address` (field 3)
- field 4 is **reserved** (removed in a past migration; must never be reused)
- `email` (field 5)
- `credit_card` (field 6)

### What does NOT exist today
- No database or persistent store of any kind (Redis is used for cart only, and it is ephemeral by default).
- No user account model. No login. No persistent user identity.
- No order ID that survives beyond the checkout HTTP response.

## Proposed Solution

### 1. New service: OrderHistoryService

A new Go microservice `orderhistoryservice` backed by a PostgreSQL database. It exposes two RPCs:

```protobuf
service OrderHistoryService {
  rpc SaveOrder(SaveOrderRequest) returns (SaveOrderResponse);
  rpc GetOrderHistory(GetOrderHistoryRequest) returns (GetOrderHistoryResponse);
}

message SaveOrderRequest {
  string account_id    = 1;  // persistent account ID, NOT session UUID
  Order  order         = 2;
}

message SaveOrderResponse {
  string order_id = 1;
}

message GetOrderHistoryRequest {
  string account_id = 1;
  int32  page_size  = 2;  // default 20, max 100
  string page_token = 3;  // opaque cursor for pagination
}

message GetOrderHistoryResponse {
  repeated Order orders         = 1;
  string         next_page_token = 2;
}

message Order {
  string          order_id         = 1;
  string          account_id       = 2;
  int64           created_at_unix  = 3;
  repeated OrderItem items         = 4;
  Money           shipping_cost    = 5;
  Address         shipping_address = 6;
  string          payment_last_four = 7;  // masked; last 4 digits only
  string          currency_code    = 8;
  Money           total_amount     = 9;
  string          shipping_tracking_id = 10;
}

message OrderItem {
  string product_id = 1;
  string name       = 2;
  int32  quantity   = 3;
  Money  unit_price = 4;
}
```

`OrderHistoryService` runs on port `6060` and is not exposed externally. It is only reachable from `checkoutservice` (write path) and `frontend` (read path).

### 2. Changes to CheckoutService

After step 7 (`EmailService.SendOrderConfirmation`) and before step 8 (`CartService.EmptyCart`), add:

**Step 7b: `OrderHistoryService.SaveOrder`**

This step requires a persistent `account_id` to be present on the request. The `account_id` is NOT the session UUID. It must come from the caller (frontend) as part of the `PlaceOrderRequest`.

**Proto change to PlaceOrderRequest:**

```protobuf
message PlaceOrderRequest {
  string         user_id      = 1;  // session UUID; retained for backward compat
  string         user_currency = 2;
  Address        address      = 3;
  // field 4 is RESERVED — do not reuse
  string         email        = 5;
  CreditCardInfo credit_card  = 6;
  string         account_id   = 7;  // NEW: persistent account ID; empty string = guest checkout
}
```

Field 7 is new. If `account_id` is empty (guest checkout), `checkoutservice` skips the `SaveOrder` call entirely. Guest checkout behavior is unchanged.

**Error handling:** If `SaveOrder` fails, `checkoutservice` logs the error and continues to step 8 (`CartService.EmptyCart`). It does NOT fail the `PlaceOrder` RPC. The order history write is best-effort for now. This is consistent with how `EmailService` failures are handled today (§8.3) and carries the same risk: a user might complete checkout without a history record being written. This is a known limitation to be addressed in a follow-up (see Risks).

### 3. New frontend page: /orders

The `/orders` handler in `frontend` calls `OrderHistoryService.GetOrderHistory(account_id, page_size=20)` and renders a list of past orders. The page is only accessible to logged-in users (the auth system gates this route). If the user is not logged in, redirect to login.

The frontend already has a gRPC client pool for downstream services. A new `OrderHistoryServiceClient` is added following the same pattern as existing clients (`checkoutservice`, `productcatalogservice`, etc.).

A link to `/orders` is added to the navigation header, visible only when a user is authenticated.

### 4. User identity dependency

This design introduces `account_id` as a string field passed from the auth system through the frontend to `checkoutservice`. The auth system is out of scope for this document. The contract expected:
- Frontend can read `account_id` from a session token issued after login.
- `account_id` is stable across sessions, devices, and password changes.
- Guest users have an empty `account_id`.

If the auth system is delayed, this feature cannot ship to production. There is no workaround that avoids this dependency.

## Affected Services

| Service | Change |
|---|---|
| `checkoutservice` | New step 7b in PlaceOrder; new `account_id` field on `PlaceOrderRequest` (field 7); new gRPC client for `OrderHistoryService` |
| `frontend` | New `/orders` page handler; passes `account_id` on PlaceOrder call; new `OrderHistoryServiceClient`; nav header update |
| `orderhistoryservice` | New service — full implementation |
| `emailservice` | No changes |
| `cartservice` | No changes |
| `paymentservice` | No changes |
| `productcatalogservice` | No changes |
| `currencyservice` | No changes |
| `shippingservice` | No changes |
| `recommendationservice` | No changes |
| `adservice` | No changes |

## API / Proto Changes

1. `PlaceOrderRequest` gains field `string account_id = 7`. Field 4 remains reserved. All existing callers that omit field 7 will continue to work (guest checkout path).
2. New proto file `orderhistoryservice.proto` defining the service and messages listed above.
3. No changes to any other existing proto definitions.

## Data Model

PostgreSQL database `orderhistory`:

```sql
CREATE TABLE orders (
  order_id            TEXT PRIMARY KEY,         -- UUID generated by checkoutservice
  account_id          TEXT NOT NULL,
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  currency_code       TEXT NOT NULL,
  total_units         BIGINT NOT NULL,
  total_nanos         INT NOT NULL,
  shipping_cost_units BIGINT NOT NULL,
  shipping_cost_nanos INT NOT NULL,
  shipping_tracking_id TEXT,
  payment_last_four   TEXT NOT NULL,
  shipping_address    JSONB NOT NULL,           -- serialized Address proto
  items               JSONB NOT NULL            -- serialized []OrderItem
);

CREATE INDEX idx_orders_account_id_created_at ON orders (account_id, created_at DESC);
```

The `items` and `shipping_address` fields are stored as JSONB for flexibility. Product names are captured at order time (denormalized) so that catalog changes do not alter historical order display.

## Deployment Plan

1. Deploy `orderhistoryservice` with its Postgres instance. Verify liveness and readiness probes pass.
2. Deploy updated `checkoutservice` binary with `account_id` field 7 added and `SaveOrder` call in place (behind empty-string guard — no functional change until auth ships).
3. Deploy updated `frontend` binary with `/orders` route and nav link hidden behind auth guard (no visible change until auth ships).
4. When auth system ships: enable account_id propagation end-to-end and open the `/orders` route to logged-in users.

Rollback: steps 2 and 3 are backward compatible. Rolling back `checkoutservice` to a binary that does not know about `OrderHistoryService` simply means no writes occur — no data is lost. Rolling back `frontend` hides the `/orders` page.

## Risks & Open Questions

**Order write is best-effort.** Placing `SaveOrder` after `PaymentService.Charge` and after `EmailService.SendOrderConfirmation` means that if the order history write fails, payment has already gone through and the user will have no history record. This is the same drop risk documented in §8.3 and §10.8 of the Product Handbook. A transactional outbox pattern or a retry queue would address this but is not in scope for v1.

**No transactional checkout.** `PlaceOrder` is not atomic. If `checkoutservice` crashes between steps 7 and 7b, the order history is never written even if payment succeeded. Addressing true atomicity requires a larger checkout refactor.

**Auth system dependency is a launch blocker.** Without `account_id` being populated, the entire history feature is inert. The deployment plan above is designed to allow code to ship safely before auth is ready, but the feature is only useful after auth is live.

**Postgres availability.** Introducing Postgres adds an operational dependency that does not exist today. The team needs runbooks for backup, restore, failover, and schema migrations before this goes to production.

**`account_id` field 7 on `PlaceOrderRequest`.** All existing callers that do not send field 7 are unaffected (proto3 zero-value for string is empty string, which triggers the guest path). However, any load-testing or integration harness that generates `PlaceOrderRequest` messages should be verified to not accidentally send stale serialized protos with unexpected bytes at field 7.

**Data retention and GDPR.** Users have a right to deletion under GDPR. The `OrderHistoryService` must implement a `DeleteOrderHistory(account_id)` RPC before the feature is available to EU users.
