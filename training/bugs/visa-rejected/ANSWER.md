# Trainer cheat sheet — visa-rejected

**Service:** `paymentservice` (Node.js)
**File:** `src/paymentservice/charge.js`
**Function:** `charge()`, line ~74.

## What the bug is

The card-type allowlist compares against `'Visa'` (capital V), but the
underlying `simple-card-validator` library returns lowercase `'visa'`.
So Visa cards never match and fall through to `UnacceptedCreditCard`.
Mastercard still works because its check still uses lowercase.

The customer's quote of the error message — "we cannot process visa
credit cards" with lowercase visa — is the giveaway: the *displayed*
type is lowercase, while the *check* must be case-sensitive.

## What a good triage ticket looks like

- **Steps to reproduce:** add anything to cart → checkout with any valid
  Visa card (test card `4111111111111111` works) → "we cannot process
  visa credit cards" error. Mastercard test card `5555555555554444`
  succeeds.
- **Suspected area:** `paymentservice`, specifically the card-type allowlist.
  The contrast between the upper-case `VISA` in the error template and
  the lower-case `visa` returned by the validator is the smoking gun.
- **Severity rationale:** Visa is ~50% of consumer card volume — this
  blocks roughly half of all paid checkouts. P0/revenue-blocking.
- **Note for whoever fixes:** check whether other downstream comparisons
  (logs, analytics) also assume a particular casing — it's likely the
  validator library was updated and changed casing.

## The actual fix

Change `'Visa'` to `'visa'` on the same line.
