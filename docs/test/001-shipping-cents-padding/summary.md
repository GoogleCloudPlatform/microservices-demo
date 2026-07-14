# Live smoke — unit 001-shipping-cents-padding — frontend + checkoutservice

**Verdict: PASS**

## Scope and what this smoke proves (read this first)
This unit fixed `Quote.String()` in `shippingservice` to zero-pad cents (`%d` -> `%02d`). That
method is **not** on any live request path -- `GetQuote` returns a proto `Money{Units, Nanos}`
built from struct fields, and the frontend renders the shipping cost with its own formatter -- so
the fix itself is not observable in this smoke. **This is a regression smoke**: it proves that,
with our branch's `shippingservice` image (`shippingservice:work-001`) now deployed, the
browse -> cart -> checkout flow still works end-to-end and a correct shipping cost renders. It
does **not** validate the cents-padding fix directly.

## Method
No browser automation tool was available in this environment, so the flow was driven **over
HTTP with `curl`** against the port-forwarded frontend (`kubectl port-forward deployment/frontend
8080:8080` -> `http://localhost:8080`), following the same request sequence a browser would issue
(GET home -> GET product -> POST add-to-cart -> GET cart -> POST checkout), using the session
cookie (`shop_session-id`) the frontend itself sets. Evidence below is captured HTTP
request/response transcripts and container logs (`kubectl logs`) rather than screenshots.

## Environment
- Cluster: `kind-boutique` (context confirmed via `kubectl config current-context`).
- All 12 deployments `Available`/`Running` (`kubectl get pods` / `kubectl get deployments`).
- `shippingservice` confirmed running our branch build:
  `kubectl get deployment shippingservice -o jsonpath='{.spec.template.spec.containers[0].image}'`
  -> `shippingservice:work-001`, freshly rolled out (pod age 32s at test start, 0 restarts
  throughout).
- No redeploy performed by this smoke -- the environment was already up per the dispatch.

---

## Step 1 -- Home page loads (frontend runbook step 1)
**PASS.** `GET http://localhost:8080/` -> `HTTP/1.1 200 OK`, `Set-Cookie: shop_session-id=...`.
Product grid rendered with prices (`$19.99`, `$18.99`, `$109.99`, `$89.99`, `$24.99`, `$18.49`,
`$5.49`, `$8.99`, ...).

Evidence: [01-home.txt](./01-home.txt)

---

## Step 2 -- Open product, add to cart, view cart (frontend runbook step 2)
**PASS.**
- `GET /product/0PUK6V6EV0` (cookie: session from step 1) -> `HTTP_STATUS:200`, product "Candle
  Holder" $18.99 rendered.
- `POST /cart` with `product_id=0PUK6V6EV0&quantity=1` (same session cookie) -> `HTTP/1.1 302
  Found`, `Location: /cart` (standard add-to-cart redirect).
- `GET /cart` (same session) -> `HTTP/1.1 200 OK`, cart shows item **"Candle Holder"**,
  **Quantity: 1**, and line items **Item $18.99 / Shipping $8.99 / Tax $1.43 / Total $29.41**.

Evidence: [02-cart.txt](./02-cart.txt)

---

## Step 3 -- Place Order with pre-filled demo card (frontend runbook step 3)
**PASS.** `POST /cart/checkout` with the cart page's pre-filled demo values (email
`someone@example.com`, address `1600 Amphitheatre Parkway, Mountain View, CA, United States`,
card `4432801561520454` exp `1/2027` CVV `672` -- all synthetic demo data baked into the app) ->
`HTTP/1.1 200 OK`, order-confirmation page rendered:
- **Confirmation #** `a3f2a395-7f6f-11f1-af7a-daa790f68b9a`
- **Tracking #** `LJ-44162-224626967`
- **Tax** `$1.43`
- **Total Paid** `$29.41`

Shipping cost is the delta baked into Total Paid ($29.41 - $18.99 item - $1.43 tax = **$8.99
shipping**), matching the `$8.99` shipping line already shown explicitly on the cart page in
step 2 -- the shipping cost renders correctly (no missing/garbled digits, no un-padded cents),
i.e. no regression from the `shippingservice:work-001` build.

Evidence: [03-order-confirmed.txt](./03-order-confirmed.txt)

---

## Step 4 -- shippingservice logs during/after checkout
**PASS.** `kubectl logs deployment/shippingservice --tail=50` shows the service started cleanly
on `shippingservice:work-001` and served two `GetQuote` calls (cart view + checkout) and one
`ShipOrder` call, all `received request` -> `completed request` with no errors:

```
{"message":"Shipping Service listening on port :50051", ...}
{"message":"[GetQuote] received request", ...}
{"message":"[GetQuote] completed request", ...}
{"message":"[GetQuote] received request", ...}
{"message":"[GetQuote] completed request", ...}
{"message":"[ShipOrder] received request", ...}
{"message":"[ShipOrder] completed request", ...}
```

Evidence: [04-shipping-logs.txt](./04-shipping-logs.txt)

## Step 4b -- checkoutservice logs (checkoutservice runbook step 1)
**PASS.** `kubectl logs deployment/checkoutservice --tail=50` shows `PlaceOrder` orchestrated the
full dependency chain (cart -> shipping quote -> payment -> email) without error:

```
{"message":"[PlaceOrder] user_id=\"8d2e386b-...\" user_currency=\"USD\"", ...}
{"message":"payment went through (transaction_id: f69d650b-b8dd-43f5-9d8e-32bae9af3997)", ...}
{"message":"order confirmation email sent to \"someone@example.com\"", ...}
```

Evidence: [05-checkoutservice-logs.txt](./05-checkoutservice-logs.txt)

---

## Step 5 -- Negative: empty-cart checkout (checkoutservice runbook step 2)
**PASS (handled gracefully, no 5xx/crash).** A fresh session (no add-to-cart) was posted directly
to `/cart/checkout` with the same demo shipping/payment fields. Result: `HTTP/1.1 200 OK`, an
order-confirmation page still rendered (Confirmation # `bbb4961c-...`, Tax `$0.00`, an
all-zero-priced order since the cart was empty) -- no 500, no exception, no crash.
`checkoutservice` logs show `PlaceOrder` -> `payment went through` -> `confirmation email sent`
cleanly for this request too. This is the app's pre-existing behavior for an empty cart (it
still "completes" a $0 order rather than rejecting it) -- no regression introduced by this unit,
and critically **no 5xx / crash**, which is the runbook's negative-case bar.

Evidence: [06-negative-empty-cart.txt](./06-negative-empty-cart.txt)

---

## Pod health check (no crash introduced)
`kubectl get pods` after the full flow: `shippingservice` `Running`, **0 restarts** (fresh
rollout of `work-001`, pod age ~3m at check time). `checkoutservice` and `frontend` each show
`Running` with 1 restart that occurred ~8-9 minutes **before** this smoke's first request
(consistent with a pre-existing kind-cluster node event, not something caused by our checkout
flow) -- no new restarts were observed on any of the three services during or after the browse ->
cart -> checkout -> negative-checkout sequence run here.

## Overall verdict
**PASS** -- browse -> add to cart -> checkout completes with a correct, correctly-rendered
shipping cost, `shippingservice` and `checkoutservice` served every call without error on the
`shippingservice:work-001` build, and the empty-cart negative case is handled without a 5xx or
crash. This confirms **no regression** in the shipping/checkout flow from the `Quote.String()`
cents-padding fix; it does not directly exercise `Quote.String()` itself, since that method is not
on the live request path (see Scope above).
