# UI / Route Contract: Promo code at checkout

The frontend exposes server-rendered pages and form routes. This feature adds one route and extends two pages.

## New route: `POST /cart/promo`

Applies or clears a promo code, then redirects back to the cart/checkout page.

- **Form field**: `promo_code` (string)
- **Behaviour**:
  | Input | Effect | Response |
  |-------|--------|----------|
  | Recognised code (e.g. `50OFF`, any case) | Set `shop_promo` cookie to normalised code | `302` → `/cart` |
  | Empty | Clear `shop_promo` cookie | `302` → `/cart` |
  | Unrecognised, non-empty | No change (no error — out of scope, AIP-179) | `302` → `/cart` |
- **Methods**: `POST` only (mirrors `/cart`, `/cart/empty`, `/cart/checkout`).

## Extended page: `GET /cart` (checkout page)

- Renders a promo-code input + "Apply" button (its own form posting to `/cart/promo`, outside the checkout form).
- When `shop_promo` holds a valid code:
  - Shows an inline confirmation, e.g. `Promo code 50OFF applied — 50% off your basket.`
  - Shows a discount line (negative amount).
  - The **Total** equals `itemsSubtotal − discount + shipping`.
- When no valid code: page is identical to today (no discount line, no confirmation, no error).

## Extended page: order confirmation (after `POST /cart/checkout`)

- When a valid code was applied at the time of ordering:
  - **Total Paid** equals the discounted total (`itemsSubtotal − discount + shipping`).
  - Optionally shows the applied code / discount line.
- The `shop_promo` cookie is cleared after the order is placed.
- When no code: confirmation is identical to today.

## Acceptance mapping

- FR-001/FR-002/FR-003 → `GET /cart` input + confirmation + discounted Total.
- FR-004 → discounted **Total Paid** on the confirmation page equals the cart Total.
- FR-005 → no-code path unchanged on both pages.
- FR-006 → recognised set is the `promoCodes` map (`50OFF` only at launch).
