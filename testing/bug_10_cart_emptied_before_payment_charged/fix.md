# Ground truth fix — bug_10_cart_emptied_before_payment_charged

**Not applied to source** — documentation only, so the planted bug stays live for testing.

## Affected file
`src/checkoutservice/src/main/java/hipstershop/CheckoutServiceImpl.java`

## Exact change

```diff
--- a/src/checkoutservice/src/main/java/hipstershop/CheckoutServiceImpl.java
+++ b/src/checkoutservice/src/main/java/hipstershop/CheckoutServiceImpl.java
@@ public void placeOrder(
-      emptyUserCart(req.getUserId());
       String txId = chargeCard(total, req.getCreditCard());
       logger.info("payment went through (transaction_id: {})", txId);

       String shippingTrackingId = shipOrder(req.getAddress(), prep.cartItems);

-
+      emptyUserCart(req.getUserId());
```

(net effect: move the `emptyUserCart(req.getUserId());` call back to after
`shipOrder(...)`, immediately before building `orderResult`.)

## Why this is correct
Charging the card is the step that can fail (declined, expired, unaccepted
card type) and throw an exception that aborts the rest of `PlaceOrder`. By
only emptying the cart after both `chargeCard` and `shipOrder` have
succeeded, a failed charge throws *before* the cart is touched at all, so the
shopper's cart is preserved exactly as before on any checkout failure, and is
only cleared once the order has actually gone through — matching the
"swallow errors, never let emptying the cart break an already-placed order"
intent documented on `emptyUserCart` itself. No other file needs to change.
