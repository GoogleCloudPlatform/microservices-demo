# Ground truth fix — bug_09_checkout_crashes_non_usd_currency

**Not applied to source** — documentation only, so the planted bug stays live for testing.

## Affected file
`src/checkoutservice/src/main/java/hipstershop/CheckoutServiceImpl.java`

## Exact change

```diff
--- a/src/checkoutservice/src/main/java/hipstershop/CheckoutServiceImpl.java
+++ b/src/checkoutservice/src/main/java/hipstershop/CheckoutServiceImpl.java
@@ private OrderPrep prepareOrderItemsAndShippingQuoteFromCart(
     Money shippingUsd = quoteShipping(address, cartItems);
-    out.shippingCostLocalized = shippingUsd;
+    out.shippingCostLocalized = convertCurrency(shippingUsd, userCurrency);
```

## Why this is correct
`convertCurrency(shippingUsd, userCurrency)` calls `currencyservice` to
convert the USD shipping quote into the shopper's selected currency and
returns a `Money` whose `currencyCode` matches `userCurrency`. With that
restored, `shippingCostLocalized` is always in the same currency as the
running order total (`MoneyUtil.zero(req.getUserCurrency())`), so
`MoneyUtil.sum(total, prep.shippingCostLocalized)` in `PlaceOrder` never hits
the currency-mismatch guard, and checkout completes normally for every
supported currency, not just USD. No other file needs to change — this is
the only place the shipping quote is attached to the order without going
through currency conversion.
