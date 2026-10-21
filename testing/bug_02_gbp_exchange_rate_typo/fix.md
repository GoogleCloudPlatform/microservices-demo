# Ground truth fix — bug_02_gbp_exchange_rate_typo

**Not applied to source** — documentation only, so the planted bug stays live for testing.

## Affected file
`src/currencyservice/data/currency_conversion.json`

## Exact change

```diff
--- a/src/currencyservice/data/currency_conversion.json
+++ b/src/currencyservice/data/currency_conversion.json
@@
-  "GBP": "0.58970",
+  "GBP": "0.85970",
```

## Why this is correct
The file stores, for each currency, how many units of that currency equal 1
EUR. `currencyservice`'s `convert()` divides by the `from` currency's rate to
get a EUR amount, then multiplies by the `to` currency's rate to get the
target amount. Restoring `0.85970` for GBP (its correct, published rate
relative to EUR at the time this dataset was captured) makes a $109.99 watch
convert to `109.99 / 1.1305 (USD→EUR) * 0.85970 (EUR→GBP) ≈ £83.64`, matching
the expected assertion. No code changes are needed — the conversion logic in
`server.js` was never wrong.
