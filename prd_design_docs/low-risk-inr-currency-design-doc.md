# Design Doc: Indian Rupee (INR) Display Currency Support
**Status:** Draft  **Author:** Engineering Team  **Date:** 2026-05-26

## Background

`CurrencyService` is a Node.js service running on port 7000. It is the highest-QPS service in the Online Boutique system — every product page render triggers one or more `Convert` RPC calls to translate prices from EUR (the base currency) to the user's selected display currency.

The service reads exchange rates from a static JSON file at startup:
```
src/currencyservice/data/currency_conversion.json
```

The file contains a flat object where each key is a currency code (ISO 4217) and the value is the exchange rate relative to EUR. For example:
```json
{
  "EUR": 1,
  "USD": 1.0960,
  "JPY": 130.16,
  "GBP": 0.8652,
  ...
}
```

Base currency is EUR. All conversions use EUR as a pivot: to convert amount X from currency A to currency B, the service computes `X / rates[A] * rates[B]`. This is standard cross-rate arithmetic.

`GetSupportedCurrencies` returns `Object.keys(currencyData)` — literally the list of all keys in the loaded JSON. There is no separate registry or allow-list. If a key is in the file, the currency is supported. If a key is absent and `Convert` is called with that code, the service returns a gRPC error (`INVALID_ARGUMENT`, per §8.6 of the Product Handbook).

INR is not currently in `currency_conversion.json`, which is why it does not appear in the currency selector dropdown.

## Current State

`currency_conversion.json` contains rates for: EUR, USD, JPY, GBP, CAD, HKD, CHF, SGD, SEK, CZK, DKK, NOK, MYR, BGN, BRL, HRK, HUF, IDR, ILS, ISK, KRW, MXN, NZD, PHP, PLN, RON, RUB, THB, TRY, ZAR.

Indian Rupee (INR) is absent. Attempting to call `Convert` with `to_code = "INR"` would return an error under the current deployment. The frontend's currency selector dropdown renders from `GetSupportedCurrencies`, so INR does not appear as an option today.

## Proposed Solution

### Change 1: Add INR to currency_conversion.json

Add one line to `src/currencyservice/data/currency_conversion.json`:

```json
"INR": 89.47
```

The value `89.47` represents the EUR→INR exchange rate (approximately 1 EUR = 89.47 INR as of the ECB reference rate published 2026-05-23). The exact value should be confirmed against the ECB reference rate at `https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/` on the day the PR is merged, and the chosen value and source date must be noted in the PR description.

**No other changes to `currencyservice` source code.** The rate-loading and conversion logic is fully data-driven. The service reads the JSON file at startup; adding a new key is sufficient.

### Change 2: Rebuild and redeploy currencyservice container

After updating `currency_conversion.json`:
1. Rebuild the `currencyservice` container image with the updated file baked in.
2. Tag the image and update the Kubernetes deployment manifest (or Helm values) to reference the new image tag.
3. Roll out with `kubectl rollout` or equivalent. Because `currencyservice` is stateless, a rolling restart with zero downtime is straightforward.

After the new pods are healthy:
- `GetSupportedCurrencies` will automatically include `"INR"` in its response.
- The `frontend` currency selector dropdown will include INR on the next page render (the frontend calls `GetSupportedCurrencies` dynamically; no frontend rebuild required).
- `Convert` with `to_code = "INR"` will succeed.

### What does NOT change

- `currencyservice` proto definitions: no changes. `GetSupportedCurrenciesRequest`, `GetSupportedCurrenciesResponse`, `ConvertRequest`, `ConvertResponse` — all unchanged.
- `frontend`: no code changes. The currency dropdown is populated at runtime from `GetSupportedCurrencies`.
- `checkoutservice`: passes `user_currency` from the `PlaceOrderRequest` to `CurrencyService.Convert`. INR will work automatically as a valid currency code. No code change needed.
- `productcatalogservice`, `cartservice`, `paymentservice`, `shippingservice`, `emailservice`, `recommendationservice`, `adservice`: no changes, no awareness of the currency change.
- The `Money` proto (`currency_code`, `units`, `nanos`) already supports arbitrary currency codes as strings. INR prices will be represented with `currency_code = "INR"`, `units` holding the whole-rupee amount, and `nanos` holding the sub-rupee fractional component.

## Affected Services

| Service | Change |
|---|---|
| `currencyservice` | `currency_conversion.json` updated with INR rate; container image rebuild and redeploy |
| All other services | No changes |

## Deployment Plan

1. Open a PR that adds `"INR": <rate>` to `currency_conversion.json`. Record the ECB rate value and the date it was sourced in the PR description.
2. CI builds the updated `currencyservice` container image and runs existing unit tests (conversion accuracy tests).
3. Deploy to staging. Manually verify:
   - `GetSupportedCurrencies` response includes `"INR"`.
   - INR appears in the frontend currency dropdown.
   - Select INR; verify product prices render as reasonable INR amounts (e.g., a $10 item ≈ ₹830 at approximate USD/INR cross-rate).
   - Verify existing currencies (USD, EUR, GBP) continue to display correctly (no regression).
4. Deploy to production with a standard rolling update. Monitor error rate on `currencyservice` for 30 minutes post-deploy.
5. Rollback: if errors are observed, roll back to the previous `currencyservice` image tag. The old image does not contain the INR key; users who had INR selected in their session will see a currency conversion error until they select a different currency. Rollback decision window is 30 minutes.

## Risks & Open Questions

**Rate accuracy and staleness.** The rate baked into `currency_conversion.json` is a point-in-time snapshot. All other currencies in the file appear to have been set similarly (static values, not live-fetched). For a demo application this is acceptable, but the INR/EUR rate can move meaningfully over months. If the application is used for demo purposes over a long period without rate updates, INR prices will drift from real-world values. This is consistent with the existing behavior for all other currencies and is not a regression, but worth noting for future maintainers.

**ECB vs RBI rate source.** The ECB EUR/INR reference rate and the RBI EUR/INR fixing rate may differ slightly due to methodology and market timing. The ECB rate is the appropriate choice for consistency with the rest of the table (all other rates are EUR-based, consistent with ECB methodology). Using the RBI rate would require documenting a mixed-source table and could introduce confusion when rates are updated in the future.

**No runtime rate updates.** The rate is loaded once at container startup. Updating the rate requires rebuilding and redeploying the container. There is no hot-reload mechanism. This is a known limitation of the current architecture and is unchanged by this feature.

**Currency selection persistence.** The user's selected currency is stored in the session. If a user selects INR and then `currencyservice` is rolled back (removing INR support), subsequent `Convert` calls for that user will return errors until their session picks a different currency or expires. The rollback runbook should include a note about this session state edge case.

**Sub-rupee display formatting.** INR is typically displayed rounded to 2 decimal places (paise). The `Money` proto stores `nanos` (billionths), which is finer than paise precision. The frontend's existing price formatting logic (which formats all currencies to 2 decimal places) handles this correctly. No special-casing is needed.
