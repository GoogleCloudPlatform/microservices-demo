# Trainer cheat sheet — currency-converter-mismatch

**Service:** `currencyservice` (Node.js)
**File:** `src/currencyservice/server.js`
**Function:** `convert()`, the EUR → to_currency step (around line 150).

## What the bug is

The conversion is done in two hops: from-currency → EUR → to-currency. The
first hop (FX rate as denominator) is correct. The second hop (rate as
multiplier) was changed from `*` to `/`, so prices in non-USD currencies
come out tiny — and tinier the further the currency is from EUR/USD, which
matches the customer's "JPY and TRY are way off" observation.

## What a good triage ticket looks like

The exercise is for the attendee to write the engineer-ready ticket, not
fix the bug. A good ticket includes:

- **Steps to reproduce:** add any product to cart → switch currency → observe
  total. Worse for currencies with large multipliers (JPY ~150, TRY ~30).
- **Suspected area:** `currencyservice`, specifically the `convert` RPC. The
  ratio of "wrong / right" matches an inverse of the target currency rate,
  which points at the multiplier step.
- **Severity rationale:** revenue-impacting (any non-USD checkout pays
  far less than the listed price), customer-visible, no workaround.
- **Not the fix itself** — the ticket should hand off cleanly to whoever
  picks it up, not pre-empt their judgement.

## The actual fix

Restore `*` in the second `_carry` call.
