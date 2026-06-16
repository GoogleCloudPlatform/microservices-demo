# Quickstart: Verify "Apply a valid promo code at checkout"

## Build / test (frontend service)

```pwsh
cd src/frontend
go build ./...
go test ./...
```

## Manual verification (running app)

1. Add one or more items to the cart and open **`/cart`** (the checkout page).
2. Note the **Total** (items subtotal + shipping).
3. In the **promo code** field, enter `50OFF` and click **Apply**.
   - Expect an inline confirmation: `Promo code 50OFF applied — 50% off your basket.`
   - Expect a **discount** line and the **Total** reduced by 50% of the items subtotal (shipping unchanged).
4. Click **Place Order**.
   - Expect the confirmation page's **Total Paid** to equal the discounted cart Total.
5. Repeat without entering a code:
   - Expect no discount line, no confirmation, no error — identical to today.

## Acceptance checks

- [ ] `50OFF` reduces the items total by exactly 50%; shipping unchanged (SC-001).
- [ ] Cart Total == confirmation Total Paid when a code is applied (SC-002 / FR-004).
- [ ] No-code checkout is unchanged (SC-003 / FR-005).
- [ ] Code matching is case-insensitive (`50off` works).
