# Phase 0 Research: Apply a valid promo code at checkout

## Decision 1: Where the discount is applied

- **Decision**: Apply the discount entirely in the `frontend` Go service (display on `/cart` and on the order-confirmation page).
- **Rationale**: The `/cart` page is the checkout page (it holds the address + payment form and the "Place Order" button). The payment service in this demo is a mock that returns a transaction id and does not perform a real charge, so the "amount charged" the shopper sees is the **Total Paid** rendered on the order-confirmation page (`order.html`). Computing the discounted total in the frontend therefore makes the displayed cart total and the confirmation "Total Paid" consistent (FR-004) without changing protos or other services.
- **Alternatives considered**:
  - *Plumb the code through `PlaceOrderRequest` into `checkoutservice`/`paymentservice*: rejected — requires proto changes and edits to multiple services for no visible difference in this mock-payment demo, and widens blast radius against C-001 intent of a minimal change.
  - *Apply discount in `productcatalogservice`*: rejected — would discount prices globally for all shoppers, not per-order at checkout.

## Decision 2: Where the applied code is stored

- **Decision**: Store the applied code in a cookie (`shop_promo`), consistent with how the frontend already stores session id and currency.
- **Rationale**: No new datastore (C-002). Cookies are the existing client-side state mechanism in this service (`shop_session-id`, `shop_currency`). The code→discount mapping itself is a hardcoded in-memory Go map.
- **Alternatives considered**: server-side session store (rejected — introduces state/datastore); query string (rejected — lost on navigation, not carried into the POST checkout).

## Decision 3: The hardcoded code set

- **Decision**: `map[string]float64{"50OFF": 0.50}` in a new `promo.go`, looked up case-insensitively after trimming whitespace.
- **Rationale**: Spec FR-006 — `50OFF` is the only launch code, in a hardcoded set that can be extended later by editing the map. Case-insensitive match is the documented assumption in the spec.
- **Alternatives considered**: config/env-driven set (rejected — out of scope; the epic explicitly says a small hardcoded set is fine).

## Decision 4: Discount math on the `money.Money` type

- **Decision**: Convert `Money` to total nanos (`units*1e9 + nanos`), multiply by the rate, convert back; subtract from the items subtotal via existing `money.Sum`/`money.Negate`; shipping added unchanged.
- **Rationale**: Reuses the existing `money` package and its integer-nanos representation; for a 0.50 rate the halving is exact. Shipping is summed after the discount so it is never discounted (FR-002).
- **Alternatives considered**: floating-point dollars (rejected — currency rounding errors; the codebase deliberately uses units/nanos).

## Decision 5: Invalid-code and replacement behaviour

- **Decision**: Out of scope for this story. An unrecognised, non-empty code leaves the current state unchanged with no error; an empty submission clears any applied code. No error messaging is added.
- **Rationale**: FR-005 keeps the no-code/unchanged path identical to today; invalid-code feedback is AIP-179 and replacement is AIP-180. Not pre-empting them keeps this slice minimal.

## Resolved unknowns

- "Order value" base for the 50% → **basket items total only** (shipping excluded). Resolved with the user; encoded in FR-002 / SC-001.
