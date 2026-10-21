# Ground truth fix — bug_04_payment_rejects_current_month_expiry

**Not applied to source** — documentation only, so the planted bug stays live for testing.

## Affected file
`src/paymentservice/charge.js`

## Exact change

```diff
--- a/src/paymentservice/charge.js
+++ b/src/paymentservice/charge.js
@@ module.exports = function charge (request) {
   // Also validate expiration is > today.
   const currentMonth = new Date().getMonth() + 1;
   const currentYear = new Date().getFullYear();
   const { credit_card_expiration_year: year, credit_card_expiration_month: month } = creditCard;
-  if ((currentYear * 12 + currentMonth) >= (year * 12 + month)) { throw new ExpiredCreditCard(cardNumber.replace('-', ''), month, year); }
+  if ((currentYear * 12 + currentMonth) > (year * 12 + month)) { throw new ExpiredCreditCard(cardNumber.replace('-', ''), month, year); }
```

## Why this is correct
A card is valid through the *end* of its printed expiration month, so it
should only be rejected once the current month-index is strictly greater than
the expiry month-index. Restoring `>` means a card expiring in the current
month (month-indices equal) correctly passes, while a card whose expiry month
has already passed (current strictly greater) is still correctly rejected.
No other file needs to change — this is the only place expiration is checked.
