# PRD: Subscribe & Save
**Status:** Draft  **Author:** Product Team  **Date:** 2026-05-26

## Problem Statement

Customers who intend to buy the same products repeatedly have no low-friction way to automate those orders on Online Boutique. Every reorder requires the customer to return to the site, re-add items to cart, and complete checkout manually. This creates unnecessary drop-off, increases re-acquisition cost for customers who already intend to buy again, and leaves predictable recurring revenue unrealized. Internal data shows that users who purchase the same SKU two or more times within 180 days represent a high-LTV segment — one that a subscription mechanism is purpose-built to retain.

## Goals

- Let repeat buyers subscribe to a product at checkout with a chosen delivery cadence, replacing manual reorders with automated fulfillment.
- Incentivize subscription opt-in with a configurable per-category discount (5–15%), giving buyers a tangible reason to authorize recurring charges.
- Give subscribers self-service control over their subscriptions (pause, skip, change cadence, swap product, cancel) without contacting support.
- Automate billing and fulfillment on each renewal date with robust failed-payment recovery.
- Comply with FTC click-to-cancel requirements (2024+) from day one: cancellation must be completable in ≤3 taps or clicks.

## Non-Goals

- **No multi-subscription bundle discounts in v1.** Stacking discounts for customers with multiple active subscriptions is deferred.
- **No dynamic pricing based on purchase frequency.** All pricing logic follows the price-lock rule (see Requirements).
- **No gift subscriptions.** Subscriptions are tied to the purchasing account only.
- **No free trial periods.** First charge occurs at the time of initial subscription opt-in.
- **No in-app push notifications.** The failed-payment recovery flow uses email only in v1.

## User Stories

- As a repeat buyer, I want to opt into a subscription at checkout so I don't have to remember to reorder the same item every month.
- As a repeat buyer, I want a discount applied to my subscribed items so I have a clear financial incentive to authorize automatic recurring charges.
- As a subscriber, I want to skip my next scheduled delivery without canceling my subscription so I can manage the inventory I still have at home.
- As a subscriber, I want a dashboard where I can view all my active subscriptions, change cadence, swap a product, pause, or cancel at any time.
- As a subscriber, I want to cancel my subscription in three clicks or fewer, with no hidden steps or penalty.
- As a catalog operator, I want to flag specific products as subscription-eligible so that only appropriate SKUs appear with the subscribe option.
- As a category manager, I want to configure the discount percentage per product category so that subscription margins stay within approved targets.

## Requirements

1. **Subscription eligibility flag.** Any product in the catalog can be individually flagged as subscription-eligible by catalog operations. Non-flagged products do not display the subscribe option. Currently, the product catalog is a static JSON file (`products.json`) baked into the `productcatalogservice` container; adding this flag requires a schema change to the catalog data model and a rebuild of the service image.

2. **Explicit opt-in.** The subscribe option must be presented as an opt-in toggle during the cart or checkout flow. It must not be pre-selected. The user must actively choose subscription and confirm the cadence before checkout completes.

3. **Cadence options.** Users may select one of the following delivery intervals: 7, 14, 30, 60, 90, or 180 days. Cadence is set per subscription item, not per account.

4. **Subscription dashboard.** Subscribers must be able to view all active subscriptions, change cadence, skip the next scheduled delivery, swap the subscribed product for another eligible product in the same category, pause for up to 60 days, and cancel. All of these actions must be reachable within the product UI without contacting support.

5. **Cancellation in ≤3 taps.** To comply with FTC click-to-cancel regulations (effective 2024), a subscriber must be able to cancel from the dashboard in no more than three taps or clicks. No confirmation dialogs beyond one are permitted.

6. **Automated billing and fulfillment.** On each renewal date, the system charges the subscriber's saved payment method and triggers order fulfillment automatically. This renewal process must run independently of the main checkout request path — decoupled via a separate worker queue — so that a renewal job failure does not affect live checkout traffic.

7. **Idempotent renewal jobs.** Each scheduled renewal must carry a unique idempotency key. Retried jobs must not result in duplicate charges or duplicate fulfillment events.

8. **Failed payment recovery.** If a charge fails on the renewal date, the system retries up to 3 times over 5 days (on days 1, 3, and 5 after the initial failure). After the third failed attempt, the subscription is suspended and the subscriber is notified by email. The subscriber can update their payment method and reactivate from the dashboard.

9. **Price lock.** The subscriber pays the price in effect at the time of their initial subscription opt-in for 6 months. After 6 months, the subscription re-prices to the current catalog price. The subscriber is notified by email 14 days before a re-pricing event.

10. **Discount incentive.** A configurable discount percentage (5–15%) is applied to subscribed items at the time of each charge. The discount rate is set per product category by catalog operators and is stored separately from the product price itself.

11. **PCI-DSS compliant payment storage.** The subscriber's payment method is stored as a tokenized reference — the full card number is never stored in Online Boutique's own databases. Payment tokenization is handled by a PCI-compliant payment vault (exact provider TBD).

12. **GDPR/CCPA compliance.** Subscription data (payment tokens, address, order history) must be exportable on user request and permanently deletable on account closure request.

## Success Metrics

| Goal | Metric | Target |
|---|---|---|
| Increase LTV of repeat buyers | Average orders per customer per year | +20% at 12 months post-launch |
| Reduce voluntary churn | 6-month subscription retention rate | ≥65% |
| Grow subscription GMV | % of eligible orders placed on subscription | ≥15% at 6 months post-launch |
| Regulatory compliance | Cancellation completable in ≤3 taps | 100% — measured in usability testing pre-launch |

## Open Questions

1. **Minimum effective discount.** What is the minimum discount percentage that drives meaningful opt-in without unacceptable margin damage? This requires an A/B test of discount tiers (5%, 10%, 15%) pre-launch. The answer may vary by product category.

2. **User identity prerequisite.** Subscribe & Save requires a persistent account identity to associate subscriptions with a customer across sessions. Online Boutique currently has no user accounts — session identity is an ephemeral UUID cookie. Does the account/login system ship before or concurrent with Subscribe & Save? This is a hard launch dependency.

3. **Tokenized payment storage provider.** Which PCI-compliant payment vault will hold card tokens? The current `paymentservice` is a mock that does not store payment methods. A real tokenization provider must be selected, contracted, and integrated before automated billing is possible.

4. **Fulfillment integration.** The current `shippingservice` generates a mock tracking ID. Automated subscription renewal will need to trigger real fulfillment. Is the fulfillment integration in scope for v1, or does v1 operate in a demo/simulation mode?
