# Ground truth — bug_04_payment_rejects_current_month_expiry

## Bug status
**Planted and currently live in source.** File already modified:
`src/paymentservice/charge.js`, line 80.

## Root cause (plain English)
A shopper paying with a credit card that is still valid through the end of
the current month gets their order declined with "Your credit card expired",
even though the card hasn't actually expired yet. The card is rejected one
month too early, every month, for every customer.

## Root cause (technical)
`charge.js` checks expiration by comparing "months since year 0" for today vs.
the card's expiry: `(currentYear*12 + currentMonth) > (year*12 + month)`
throws if today is strictly after the expiry month — which is correct, a card
should still work during its expiry month. The comparison operator was
changed from `>` to `>=`:

```diff
- if ((currentYear * 12 + currentMonth) > (year * 12 + month)) { throw new ExpiredCreditCard(...); }
+ if ((currentYear * 12 + currentMonth) >= (year * 12 + month)) { throw new ExpiredCreditCard(...); }
```

With `>=`, a card expiring in the *same* month as today's charge now satisfies
the "expired" condition (today's month-index equals the expiry month-index),
so it's wrongly rejected a full month before it should be. Cards expiring in
any future month are unaffected, which is why this only shows up for orders
placed in a card's actual expiry month — a narrow, easy-to-miss window in
manual testing.

## Why this is hard to spot
It's a single comparison-operator character (`>` → `>=`) in a formula that
otherwise reads as obviously correct, and the bug is date-dependent: a test
run on any day that isn't within a test card's expiry month will pass
without issue, so the defect is invisible unless the test specifically uses a
card whose expiration matches "this month."
