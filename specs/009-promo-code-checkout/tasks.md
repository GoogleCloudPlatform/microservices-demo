# Tasks: Apply a valid promo code at checkout

**Feature**: 009-promo-code-checkout | **Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

**Scope**: Frontend-only Go change in `src/frontend`. Honors epic AIP-96 constraints C-001..C-004 (existing services only, no new datastore, match Go patterns, no infra/manifest/CI changes).

One user story (US1 = AIP-178). MVP = US1.

## Phase 1: Setup

- [ ] T001 Confirm frontend builds before changes: run `go build ./...` in `src/frontend` and note baseline. *(NOT RUN — no Go toolchain on this machine; build occurs in the Docker pipeline.)*

## Phase 2: Foundational

- [X] T002 Add promo cookie constant `cookiePromoCode = cookiePrefix + "promo"` in `src/frontend/main.go` (near `cookieCurrency`).

## Phase 3: User Story 1 — Apply a valid promo code at checkout (P1)

**Story goal**: A shopper enters `50OFF` on the checkout (cart) page and sees 50% off the basket items total with an inline confirmation; the discounted total is what the confirmation reports as paid; the no-code path is unchanged.

**Independent test**: Add items, open `/cart`, apply `50OFF` → items total halved (shipping unchanged) + confirmation shown; place order → Total Paid equals discounted cart total; with no code, checkout is identical to today.

- [X] T003 [P] [US1] Create `src/frontend/promo.go`: hardcoded `promoCodes = map[string]float64{"50OFF": 0.50}`, `promoDiscountRate(code string) (float64, bool)` (upper-case + trim before lookup), and `discountAmount(m pb.Money, rate float64) pb.Money` (units/nanos math reusing the `money` package representation).
- [X] T004 [P] [US1] Create `src/frontend/promo_test.go`: unit tests for `promoDiscountRate` (valid `50OFF`/`50off`, unknown, empty) and `discountAmount` (50% of a known basket total = exact half; shipping not involved).
- [X] T005 [US1] Add `applyPromoHandler` in `src/frontend/handlers.go`: read `promo_code` form value; if recognised set `shop_promo` cookie (normalised), if empty clear it, if unrecognised leave unchanged (no error — out of scope); redirect `302` to `/cart`.
- [X] T006 [US1] Register route `POST /cart/promo` → `applyPromoHandler` in `src/frontend/main.go`.
- [X] T007 [US1] Update `viewCartHandler` in `src/frontend/handlers.go`: capture items subtotal before adding shipping; read `shop_promo` cookie; if a valid code, compute discount, set `total_cost = subtotal − discount + shipping`, and pass `promo_applied`, `promo_code`, `promo_discount` template vars.
- [X] T008 [US1] Update `placeOrderHandler` in `src/frontend/handlers.go`: read `shop_promo` cookie; compute items subtotal from order items; if a valid code, reduce `total_paid` by the discount and pass `promo_applied`/`promo_code`/`promo_discount` to the order template; clear the `shop_promo` cookie after placing the order.
- [X] T009 [US1] Update `src/frontend/templates/cart.html`: add a promo-code form (own form, posting to `/cart/promo`, outside the checkout form) with input + Apply button; show inline confirmation and a discount line when `promo_applied`.
- [X] T010 [US1] Update `src/frontend/templates/order.html`: show a discount line when `promo_applied` (Total Paid already reflects the discount).

## Phase 4: Polish & Validation

- [ ] T011 Run `go build ./...` and `go test ./...` in `src/frontend`; fix any compile/test failures. *(NOT RUN — no Go toolchain / Docker daemon available locally; relies on the Docker build in the deploy pipeline.)*
- [ ] T012 Manual check against [quickstart.md](./quickstart.md): valid-code path, confirmation Total Paid == cart Total, and unchanged no-code path.

## Dependencies

- T001 → T002 → (T003, T004 in parallel) → T005 → T006 → T007 → T008 → (T009, T010) → T011 → T012.
- T003/T004 are `[P]` (new file, independent). T005–T008 edit `handlers.go` sequentially (same file). Templates T009/T010 can follow once handler vars exist.

## Parallel example

```
# After T002:
Run T003 (create promo.go) and T004 (create promo_test.go) together — separate new files.
```

## Implementation strategy

MVP is the whole of US1 (this is Story 1, the minimal shippable slice). Deliver T001–T012 in order; the feature is demonstrable after T011 builds clean and the quickstart checks pass.
