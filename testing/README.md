# Debugging benchmark — planted bugs

This folder contains 10 deliberately planted bugs in the `microservices-demo` source tree
(under `../src/...`), used as a benchmark for testing whether an AI debugging agent
(OpenHands + ESIP) can correctly root-cause and fix real cross-service defects.

Each `bug_NN_*` folder contains three files:

- **prompt.md** — the exact QA/automation-style bug report to hand to the agent (same
  format as the real `CC_twoproducts_EUR_SAVE10DiscountCoupon` failure report this
  benchmark is modeled on). This is the ONLY file the agent should be given.
- **issue.md** — the ground-truth root cause (for grading the agent's diagnosis against).
- **fix.md** — the ground-truth fix (file(s) + exact change), for grading the agent's
  proposed/applied fix against. **This fix is documented only — it has NOT been applied
  to the source tree.** The bug itself IS applied (see "Bug status" in each issue.md).

## Bugs

| # | Folder | Service(s) | Symptom |
|---|--------|-----------|---------|
| 1 | `bug_01_shipping_cost_nanos_truncation` | shippingservice | Shipping cost shown as $8.10 instead of $8.99 |
| 2 | `bug_02_gbp_exchange_rate_typo` | currencyservice | GBP prices come out far too low (transposed digits in exchange rate) |
| 3 | `bug_03_recommendations_always_empty` | recommendationservice | "Other products you might like" is always empty |
| 4 | `bug_04_payment_rejects_current_month_expiry` | paymentservice | A card expiring this month is wrongly rejected as "expired" |
| 5 | `bug_05_adservice_category_mismatch` | adservice | Footwear product page shows a clothing ad, and vice versa |
| 6 | `bug_06_cart_quantity_overwritten` | cartservice | Adding a product already in the cart resets its quantity instead of adding to it |
| 7 | `bug_07_multiplyslow_undercounts_quantity` | frontend | Line-item/order totals for quantity ≥ 2 are short by exactly one unit price |
| 8 | `bug_08_productsearch_case_sensitive` | productcatalogservice | Searching with a capitalized/mixed-case query returns no results |
| 9 | `bug_09_checkout_crashes_non_usd_currency` | checkoutservice | Placing an order in any non-USD currency fails outright |
| 10 | `bug_10_cart_emptied_before_payment_charged` | checkoutservice | A declined/invalid card still empties the shopper's cart |

All bugs are single, self-contained logic defects (one or two lines each), consistent
with the "report exactly ONE core defect" rule used in the prompts.
