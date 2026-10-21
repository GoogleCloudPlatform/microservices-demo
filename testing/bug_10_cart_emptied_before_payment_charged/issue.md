# Ground truth — bug_10_cart_emptied_before_payment_charged

## Bug status
**Planted and currently live in source.** File already modified:
`src/checkoutservice/src/main/java/hipstershop/CheckoutServiceImpl.java`, lines 168-173.

## Root cause (plain English)
If a shopper's card is declined at checkout (wrong card type, expired, etc.),
they not only fail to complete the order — they also lose everything that
was in their cart. The cart should stay untouched until the payment actually
succeeds; instead it's cleared no matter what.

## Root cause (technical)
`PlaceOrder` is supposed to charge the card first, and only clear the
shopper's cart *after* the charge succeeds, since `emptyUserCart` swallows
its own errors and should never run until the order is actually committed.
The call to empty the cart was moved to run before the charge instead of
after it:

```diff
- emptyUserCart(req.getUserId());
  String txId = chargeCard(total, req.getCreditCard());
  logger.info("payment went through (transaction_id: {})", txId);
  String shippingTrackingId = shipOrder(req.getAddress(), prep.cartItems);
+ emptyUserCart(req.getUserId());
```

`chargeCard` calls `paymentservice`, which throws a gRPC error (e.g.
`UnacceptedCreditCard`, `ExpiredCreditCard`, `InvalidCreditCard`) for a bad
card. That exception propagates out of `PlaceOrder` and is caught by the
method's own top-level `catch (StatusRuntimeException e)` — but by the time
that happens, `emptyUserCart` has already run and already succeeded, because
it now executes *before* `chargeCard` in program order. The order never
completes, but the cart is already gone.

## Why this is hard to spot
All three lines — empty cart, charge card, ship order — read as a short,
self-contained sequence that's easy to skim past without noticing the order
has changed; there's no obvious syntax or logic error in any single line,
only in the sequence they run in. The bug also only shows up when the charge
step specifically fails (a declined/invalid/expired card), which is the less
common path in both manual exploration and typical "happy path" test
coverage — a successful checkout looks completely correct either way, since
the cart ends up empty in both orderings when the charge succeeds.
