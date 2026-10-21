# Ground truth — bug_09_checkout_crashes_non_usd_currency

## Bug status
**Planted and currently live in source.** File already modified:
`src/checkoutservice/src/main/java/hipstershop/CheckoutServiceImpl.java`, line 231.

## Root cause (plain English)
Any shopper who switches the store to a currency other than US Dollars and
then tries to place an order gets a hard "Something went wrong" error page —
the order never completes. Checkout in USD still works perfectly.

## Root cause (technical)
`shippingservice` always quotes shipping cost in USD (see its own comment:
"GetQuote produces a shipping quote (cost) in USD"), so `checkoutservice`
must convert that quote into the shopper's chosen currency before adding it
to the order total. That conversion call was removed:

```diff
  Money shippingUsd = quoteShipping(address, cartItems);
- out.shippingCostLocalized = shippingUsd;
+ out.shippingCostLocalized = convertCurrency(shippingUsd, userCurrency);
```

`shippingUsd` still carries `currencyCode = "USD"` untouched. Later, in
`PlaceOrder`, the running order total is initialized in the shopper's chosen
currency (`Money total = MoneyUtil.zero(req.getUserCurrency())`, e.g. EUR) and
then summed with this shipping cost: `total = MoneyUtil.sum(total,
prep.shippingCostLocalized)`. `MoneyUtil.sum` explicitly guards against adding
two different currencies together and throws `MismatchingCurrencyException`
the moment the currency codes don't match. For a EUR (or GBP/JPY/TRY) order,
that's exactly what happens — the uncaught exception propagates out of
`PlaceOrder`, gRPC reports it as an `UNKNOWN` error, and the frontend's
generic error page is shown. Because the check only trips when
`userCurrency != "USD"`, USD orders never exercise the bug at all.

## Why this is hard to spot
The deleted line doesn't look like a conversion step was skipped — it just
looks like a straightforward field assignment, and the type still compiles
and runs fine for the most common manual test case (browsing in the default
USD currency). The crash only happens two function calls and one gRPC hop
later, inside `MoneyUtil.sum`, far away from the actual missing conversion in
`prepareOrderItemsAndShippingQuoteFromCart` — tracing the generic "mismatching
currency codes" error back to its source requires following the money through
`quoteShipping` → `shippingCostLocalized` → `PlaceOrder`'s running total.
