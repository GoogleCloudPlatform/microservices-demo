# PRD: Persistent Order History
**Status:** Draft  **Author:** Product Team  **Date:** 2026-05-26

## Problem Statement

Online Boutique currently has no way for users to view their past purchases. After a checkout completes, the order result exists only in memory for the duration of the HTTP response — once the page is served, all order data is gone. There is no persistent store, no order ID that can be retrieved later, and no user account to associate orders with.

This creates a poor post-purchase experience. Users cannot confirm that an order went through, cannot reference an order number for support, and cannot track what they have purchased in the past. Support volume related to "did my order go through?" complaints is growing, and there is no internal tooling to look up order state either.

Additionally, the system currently relies entirely on email confirmation for post-purchase acknowledgment. If the email step fails (which happens silently per current behavior), users have zero record of their purchase anywhere.

## Goals

- Give users a dedicated page where they can view a list of their completed orders.
- Each order entry should show: order ID, date placed, items purchased (product names and quantities), total amount charged, shipping address, and payment method (masked card number only).
- Orders must persist across browser sessions and device changes.
- The solution must work within the existing checkout flow without degrading checkout latency for users who do not view order history.

## Non-Goals

- Order cancellation or modification — read-only history only in this release.
- Real-time order status tracking or shipping updates.
- Order history for guest users who have not created an account (this feature requires a logged-in user identity; guest checkout remains available but will not generate history).
- Admin or support tooling for looking up orders by user — that is a separate internal tooling initiative.
- Email resend from the order history page.
- Any changes to the payment processing flow or PaymentService.

## User Stories

**US-1:** As a returning customer, I want to see a list of all my past orders so that I can confirm my purchases went through without relying on email.

**US-2:** As a customer, I want to click into a specific past order and see the full order details — items, quantities, shipping address, and the amount charged — so that I have a record I can reference for returns or support inquiries.

**US-3:** As a customer who placed an order on my phone, I want to see that same order when I log in from my laptop, so that my purchase history is not tied to a single device or browser session.

**US-4:** As a customer, I want the order history page to load quickly (under 2 seconds) even if I have placed many orders in the past.

## Requirements

**R-1 — Persistent Order Store:** Orders must be written to a durable data store at the time of checkout. In-memory storage or Redis with default ephemeral configuration is not acceptable for this data. The store must survive pod restarts and deployments.

**R-2 — User Identity Across Sessions:** The current session model assigns a UUID cookie (`shop_session-id`) per browser session, but this identity is not persistent and is not linked to a real user account. To associate orders with a specific person across sessions and devices, users must have a persistent account identity. This feature requires a logged-in user model; the authentication/account system is a dependency.

**R-3 — Order Write at Checkout:** The checkout flow must write a complete order record to the persistent store before or as part of the checkout response. The write must include all line items, pricing in the currency the user selected, shipping address, and a masked payment reference.

**R-4 — Order History API:** A new API endpoint must be available for the frontend to retrieve a user's order history, paginated, sorted by date descending.

**R-5 — Frontend Page:** A new `/orders` page must be added to the frontend, accessible to logged-in users from a persistent navigation element (e.g., header link).

**R-6 — Backward Compatibility:** Users who do not have accounts and continue to use the site as guests must experience no change in checkout behavior.

## Success Metrics

- 30 days post-launch: at least 40% of logged-in users who complete a checkout visit the `/orders` page within 7 days of their purchase.
- Support ticket volume tagged "order confirmation / did my order go through" decreases by at least 50% within 60 days of launch.
- Order history page p95 load time is under 2 seconds at steady-state traffic.
- Zero incidents of order records being lost or mismatched to the wrong user account within the first 90 days.

## Open Questions

1. **Auth dependency timeline:** This feature is gated on a login/account system that does not exist today. Is that system being built in parallel, and what is the expected delivery date? Without it, this feature cannot launch.
2. **Historical backfill:** Users who have placed orders before this feature launches will have no history. Do we display an empty state with an explanation, or do we attempt a partial backfill from email logs?
3. **Data retention policy:** How long do we retain order records? Are there regulatory considerations (GDPR right-to-deletion) that apply?
4. **Currency display:** Orders are placed in the user's selected display currency, but underlying charges are processed differently. Do we display the currency the user saw at checkout, or normalize to a base currency?
5. **What constitutes a "successful" order write?** If the order history write fails after payment succeeds, do we fail the checkout response or silently drop the history record?
