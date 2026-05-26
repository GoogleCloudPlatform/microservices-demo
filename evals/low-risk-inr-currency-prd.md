# PRD: Indian Rupee (INR) Display Currency Support
**Status:** Draft  **Author:** Product Team  **Date:** 2026-05-26

## Problem Statement

Online Boutique does not currently support Indian Rupee (INR) as a selectable display currency. Users in India browsing the site see prices in one of the currently supported currencies (EUR, USD, JPY, GBP, CAD, etc.), which creates friction for the growing segment of Indian users. Price comprehension is a known factor in purchase intent, and requiring users to mentally convert from a foreign currency adds unnecessary cognitive load.

The currency display system is already extensible. `CurrencyService` reads exchange rates from a configurable rates table at startup and exposes `GetSupportedCurrencies` which returns whatever is in that table. Adding INR support is primarily a data change, not an architecture change.

## Goals

- INR (Indian Rupee, symbol ₹) appears as a selectable option in the currency dropdown on all product pages.
- Product prices are displayed in INR when the user selects it, using the same conversion logic that all other currencies use.
- The INR exchange rate is sourced from a reputable financial data source and is accurate to within standard rounding tolerance.
- INR is treated identically to all other supported currencies — no special-casing in any service.

## Non-Goals

- Localization of the site to Indian users (language, date formats, address formats for Indian addresses) — this is a separate initiative.
- Payment processing in INR — the payment system is a mock and does not actually process charges; display currency and charge currency are independent in this system.
- Real-time or live exchange rate updates — rates are static in the current architecture. This feature does not change that.
- INR-specific tax calculations or GST handling.
- Any change to how `CurrencyService` works architecturally (no code changes, no proto changes, no new endpoints).

## User Stories

**US-1:** As an Indian user browsing Online Boutique, I want to select INR from the currency dropdown so that I can see product prices in a currency I understand without doing mental conversion.

**US-2:** As an Indian user, after selecting INR, I want all product prices on the home page, product detail pages, and the checkout summary to display in ₹ so that my entire browsing experience uses a consistent currency.

**US-3:** As a user who selected INR in a previous session, I want my currency preference to persist for the duration of my session so that I do not have to re-select it on every page.

## Background: How CurrencyService Works

`CurrencyService` (Node.js, port 7000) is the highest-QPS service in the system — it is called on every page render to convert prices. It reads exchange rates from `src/currencyservice/data/currency_conversion.json` at startup. All rates are stored relative to EUR as the base currency. A conversion from currency A to currency B is computed by first converting A→EUR and then EUR→B.

`GetSupportedCurrencies` returns all keys present in `currency_conversion.json`. There is no hardcoded currency allow-list anywhere else in the system — if a currency code appears in the JSON file, it will appear in the dropdown. Conversely, if `Convert` is called with a currency code that does not appear in the JSON file, the service returns an error (§8.6).

The currency selector in the frontend stores the user's selected currency in the session and passes it on every price conversion call. No changes to the frontend are required beyond what will happen automatically once INR is in the supported currencies list.

## Requirements

**R-1 — Rate entry:** Add an `"INR"` key to `currency_conversion.json` with an accurate EUR-based exchange rate. The rate should be sourced from the European Central Bank (ECB) reference rates or the Reserve Bank of India (RBI) reference rate and should be documented in a comment or adjacent note for future maintainers.

**R-2 — Automatic currency selector update:** Once the rate is present in the JSON file and the `currencyservice` container is rebuilt and deployed, `GetSupportedCurrencies` will automatically include `"INR"` with no additional code changes required.

**R-3 — Correct conversion:** `CurrencyService.Convert` must produce correct INR amounts for all existing product prices. Manual spot-check of at least 3 product prices in INR against a reference calculator should be performed before launch.

**R-4 — No changes to other services:** No other service should need modification. In particular, `frontend`, `checkoutservice`, `productcatalogservice`, `paymentservice`, `cartservice`, and all other services are untouched.

**R-5 — Rate documentation:** The chosen rate value and its source must be noted in a brief comment in `currency_conversion.json` or in the associated PR description, so that the next engineer who needs to update rates knows where the original value came from.

## Success Metrics

- INR appears in the currency dropdown in production within one sprint of this PRD being approved.
- Zero error rate increase on `CurrencyService.Convert` calls after INR is deployed (no `unknown currency` errors).
- Spot-check: 3 product prices verified against a reference INR conversion rate before deployment.
- No regression in conversion accuracy for any existing currency (USD, EUR, JPY, GBP, etc.).

## Open Questions

1. **Rate source:** Should we use the ECB reference rate (EUR-based, updated daily) or the RBI reference rate? The ECB rate is already the implicit source for other currencies in the table. Using ECB keeps the methodology consistent. The RBI rate may be more accurate for Indian users but introduces a second data source.
2. **Rate update cadence:** The current rates are static — they were presumably set once and have not been updated. This is fine for a demo application, but if the team ever wants to formalize a rate-update process, INR is a good candidate given INR/EUR volatility. Is there appetite to define a rate-update SOP as part of this work?
3. **Rounding:** INR amounts for sub-rupee prices should display as ₹0.xx or be rounded to the nearest rupee? The `Money` proto carries both `units` (int64) and `nanos` (int32), so sub-rupee precision is representable, but the display formatting in the frontend may round to 2 decimal places.
