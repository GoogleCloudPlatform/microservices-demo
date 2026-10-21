# Ground truth — bug_02_gbp_exchange_rate_typo

## Bug status
**Planted and currently live in source.** File already modified:
`src/currencyservice/data/currency_conversion.json`, line 8.

## Root cause (plain English)
A customer who switches the shop to British Pounds sees prices that are far
too low — a $109.99 watch shows up as about **£57.37** instead of the correct
**~£83.64**. Every other currency (EUR, USD, JPY, TRY) converts correctly;
only GBP is affected.

## Root cause (technical)
`currencyservice` converts money in two hops: `from_currency → EUR → to_currency`,
using a static table of exchange rates (relative to EUR) loaded from
`src/currencyservice/data/currency_conversion.json`. The conversion *code*
(`server.js`'s `convert()`/`_carry()`) is correct and untouched.

The bug is in the **data**, not the code: the GBP exchange rate entry has two
digits transposed —

```diff
-  "GBP": "0.85970",
+  "GBP": "0.58970",
```

`0.8597` and `0.5897` are both "plausible-looking" decimal numbers, which is
exactly why this kind of fat-finger transposition typo is easy to miss in a
JSON data file during review — nothing about it looks structurally wrong, and
every other currency in the file still converts correctly, so there's no
code-level symptom to grep for.

## Why this is hard to spot
Because the bug lives in a data file rather than in `server.js`, a review that
only reads the conversion function (which is in fact 100% correct) will
conclude there's no bug. The investigation has to follow the number from the
displayed price, through `convertCurrency` in `checkoutservice`'s
`CheckoutServiceImpl.java`, through the `convert()` RPC in `currencyservice`,
and finally into the specific numeric entry in `currency_conversion.json` —
and even then, correctly identifying it requires either computing the expected
rate independently or noticing the transposed digits by inspection.
