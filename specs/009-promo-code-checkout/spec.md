# Feature Specification: Apply a valid promo code at checkout

**Feature Branch**: `009-promo-code-checkout`

**Created**: 2026-06-16

**Status**: Draft

**Input**: Jira story [AIP-178](https://odevo.atlassian.net/browse/AIP-178) "Apply a valid promo code at checkout" (Story 1), under epic [AIP-96](https://odevo.atlassian.net/browse/AIP-96) "Promo codes at checkout".

**Source description**: "A shopper who has a discount code can enter it on the checkout page and see the discount applied to their order total before paying, with clear confirmation the code was accepted. This is the first usable slice: the code entry field plus the one launch code, `50OFF`, giving 50% off the order value."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Apply a valid promo code at checkout (Priority: P1)

A shopper who has a discount code can enter it on the checkout page and see the discount applied to their order total before paying, with clear confirmation the code was accepted. At launch there is a single hardcoded code, `50OFF`, which takes 50% off the order value.

**Why this priority**: This is the first independently shippable, customer-visible slice of the promo-code feature — the entry field plus one working code. It delivers value on its own without depending on any other story.

**Independent Test**: On the checkout page, enter `50OFF`, apply it, and confirm the order total drops by 50% and an inline confirmation shows the code was accepted; separately, proceed with no code and confirm checkout is unchanged.

**Acceptance Scenarios**:

1. **Given** I'm on the checkout page, **When** I enter `50OFF` and apply it, **Then** 50% is deducted from my order total and an inline confirmation tells me the code was accepted.
2. **Given** a code is applied, **When** I look at the order summary, **Then** the discounted total is the one shown and is the one I'll be charged.
3. **Given** I'm on the checkout page, **When** I proceed without entering any code, **Then** checkout behaves exactly as today with no discount and no error.

---

### Edge Cases

- **Order value base**: The 50% discount applies to the **total value of the basket** — the sum of all cart item prices (unit price × quantity) across the cart. Shipping is not discounted.
- **Unrecognised / mistyped codes**: Out of scope for this story — covered by sibling story [AIP-179](https://odevo.atlassian.net/browse/AIP-179) "See a clear error for an unrecognised promo code".
- **Entering a second code / replacing an applied code**: Out of scope for this story — covered by sibling story [AIP-180](https://odevo.atlassian.net/browse/AIP-180) "Replace an applied code by entering another".

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The checkout page MUST provide a field where a shopper can enter a promo code and apply it.
- **FR-002**: When the shopper applies the code `50OFF`, the system MUST reduce the order by 50% of the total value of the basket (the sum of all cart item prices, unit price × quantity). Shipping is not discounted.
- **FR-003**: When a valid code is applied, the system MUST show an inline confirmation that the code was accepted.
- **FR-004**: The order summary MUST display the discounted total, and that displayed discounted total MUST be the amount the shopper is charged.
- **FR-005**: When no code is entered, checkout MUST behave exactly as it does today — no discount applied and no error shown.
- **FR-006**: `50OFF` MUST be the only valid code at launch, held in a hardcoded set; further codes can be added later by editing that set (adding more codes is out of scope for this story).

### Constraints *(hard — from epic AIP-96 technical constraints)*

These are stated by the epic as hard constraints and bound any implementation of this story:

- **C-001**: Use only the services that already exist in the repo. Do not add new services.
- **C-002**: Do not introduce any new datastore (no database, cache, or search engine). Work in memory over the existing product catalogue in `productcatalogservice/products.json`.
- **C-003**: Match the language and patterns of the service being changed. The frontend and the product catalogue service are written in Go.
- **C-004**: Do not change infrastructure, deployment manifests, or CI configuration. The change must ship through the existing pipeline unmodified.

### Key Entities *(include if feature involves data)*

- **Promo code**: A short code (e.g., `50OFF`) belonging to a small hardcoded set, each associated with a discount (for `50OFF`, 50% of the order value).
- **Order total**: The amount the shopper will be charged; reduced when a valid code is applied, and shown in the order summary.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Applying `50OFF` reduces the basket (items) total by exactly 50%, with shipping unchanged.
- **SC-002**: In 100% of orders where a code is applied, the discounted total shown in the order summary equals the amount charged.
- **SC-003**: A shopper who enters no code completes checkout with the same steps and outcome as today — no added friction and no error shown.

## Assumptions

- Code entry is treated case-insensitively (e.g., `50off` and `50OFF` are equivalent). Not specified by the story; reasonable default.
- Only one code is active on an order at a time; the behaviour of replacing an already-applied code is specified separately in [AIP-180](https://odevo.atlassian.net/browse/AIP-180) and is not covered here.
- Feedback for unrecognised codes is specified separately in [AIP-179](https://odevo.atlassian.net/browse/AIP-179) and is not covered here; this story covers only the valid-code (happy) path plus the no-code path.
- The promo-code field is added to the existing checkout experience in the existing frontend service, consistent with constraints C-001 to C-004.
- The hardcoded code set is editable in source; codes remain active until removed from that set (no expiry), consistent with the parent PRD.

## Dependencies

- **Depends on**: none (per AIP-178). This story is independently shippable.
- **Builds on**: the existing checkout flow and the existing product catalogue (`productcatalogservice/products.json`).
- **Sibling stories** (not dependencies of this story): [AIP-179](https://odevo.atlassian.net/browse/AIP-179) and [AIP-180](https://odevo.atlassian.net/browse/AIP-180) build on this story.
