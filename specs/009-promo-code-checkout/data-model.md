# Phase 1 Data Model: Apply a valid promo code at checkout

No persistent data is added. The "entities" below are in-memory/transport-only.

## Promo code (in-memory)

- **Representation**: entry in `map[string]float64` (`promoCodes`) in `src/frontend/promo.go`.
- **Key**: the code string, normalised to upper-case, whitespace-trimmed (e.g. `50OFF`).
- **Value**: discount rate as a fraction in `(0,1]` (e.g. `0.50` = 50% off).
- **Lifecycle**: defined in source; a code is "active" while present in the map (no expiry). Adding/removing codes = editing the map.
- **Validation**: a submitted code is valid iff its normalised form is a key in the map.

## Applied code (per shopper, transient)

- **Representation**: cookie `shop_promo` holding the normalised applied code; absent when no code is applied.
- **Lifecycle**: set when a valid code is applied; cleared on empty submission and after an order is placed.
- **Scope**: only one code at a time (a single cookie value). Replacement semantics are AIP-180.

## Derived values (computed per request, not stored)

- **Items subtotal** (`Money`): sum of `unitPrice × quantity` over cart items, in the shopper's currency. Already computed in `viewCartHandler`; captured before shipping is added.
- **Discount amount** (`Money`): `rate × itemsSubtotal`, currency-matched. Zero/absent when no valid code applied.
- **Discounted total** (`Money`): `itemsSubtotal − discount + shipping`.

## Template data added

`cart` template:
- `promo_applied` (bool)
- `promo_code` (string, normalised) — for the confirmation text
- `promo_discount` (`*Money`) — discount amount, shown as a negative line
- `total_cost` (`Money`) — now the discounted total when a code is applied

`order` template:
- `promo_applied` (bool), `promo_code` (string), `promo_discount` (`*Money`)
- `total_paid` (`*Money`) — now the discounted amount when a code was applied
