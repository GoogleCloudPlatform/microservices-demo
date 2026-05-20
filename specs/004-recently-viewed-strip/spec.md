# Feature Specification: Recently Viewed Strip on Product Detail Page

**Feature Branch**: `004-recently-viewed-strip`
**Created**: 2026-05-20
**Status**: Draft
**Source**: [AIP-156](https://odevo.atlassian.net/browse/AIP-156) (Story) / [AIP-97](https://odevo.atlassian.net/browse/AIP-97) (Epic)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Return to Previously Viewed Product (Priority: P1)

A shopper browsing Online Boutique has already viewed one or more products during their current visit. When they land on any product detail page they see a "Recently viewed" strip showing those earlier products, so they can compare or jump back to an item without retracing their steps through the catalogue.

**Why this priority**: This is the core value of the feature. All other behaviour is secondary to this being in place.

**Independent Test**: Visit two or more product pages in sequence; verify the strip appears on the third page listing the products viewed so far.

**Acceptance Scenarios**:

1. **Given** I have viewed at least one other product earlier in my session, **When** I land on any product detail page, **Then** a "Recently viewed" strip is visible and shows all products I have looked at during this visit.

---

### User Story 2 - Navigate from Strip to Product (Priority: P1)

A shopper who can see the "Recently viewed" strip clicks one of the products shown in it.

**Why this priority**: Without navigation the strip is decorative only; clicking through is what gives the feature its value.

**Independent Test**: Click a product in the strip; verify the resulting page is that product's detail page.

**Acceptance Scenarios**:

1. **Given** the "Recently viewed" strip is visible, **When** I select a product from the strip, **Then** I am on that product's detail page.

---

### User Story 3 - No Strip When No History Exists (Priority: P2)

A shopper who has not yet viewed any other product during their current session arrives on a product detail page.

**Why this priority**: An empty strip creates visual noise; hiding it when there is nothing to show keeps the page clean.

**Independent Test**: Open the shop fresh (no prior navigation this session) and land on a product page; verify no strip is rendered.

**Acceptance Scenarios**:

1. **Given** I have not viewed any other products this session, **When** I land on a product detail page, **Then** no "Recently viewed" strip is shown.

---

### Edge Cases

- What happens when a shopper views the same product more than once — does it appear once or twice in the strip?
- How does the strip behave when the number of viewed products exceeds 5 — it shows the 5 most recently viewed and older items are dropped from the strip.
- What happens if a shopper views a product that is already in the strip — it moves to the most-recent position (no duplicate entry).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST display a "Recently viewed" strip on every product detail page when the shopper has viewed at least one other product in the current session.
- **FR-002**: The strip MUST list only products viewed during the current browser session; no history from previous visits is included.
- **FR-003**: Each item in the strip MUST be a navigable link that takes the shopper to that product's detail page.
- **FR-004**: The strip MUST NOT be rendered when the shopper has not yet viewed any other product in the current session.
- **FR-005**: The product currently being viewed MUST NOT appear in the strip.
- **FR-006**: The strip MUST display a maximum of 5 products. When more than 5 products have been viewed, only the 5 most recently viewed are shown.
- **FR-007**: The same product MUST NOT appear more than once in the strip, regardless of how many times it was visited.
- **FR-008**: Cross-device synchronisation of session history is explicitly out of scope.

### Hard Constraints *(from Epic AIP-97 — non-negotiable)*

- **HC-001**: Only existing services in the repository may be modified. No new services may be introduced.
- **HC-002**: No new datastore, database, cache, or search engine may be added. Viewed-product history must be maintained entirely in memory within the existing request lifecycle.
- **HC-003**: Infrastructure, deployment manifests, and CI configuration must remain unchanged. The feature must ship through the existing pipeline unmodified.

### Key Entities

- **Session**: A shopper's continuous visit within a single browser session. Bounded by the browser tab lifetime or explicit session termination.
- **Viewed Product**: A product whose detail page the shopper has navigated to at least once in the current session. Carries enough information to render its strip entry (name, image, price, and link).
- **Recently Viewed Strip**: A UI element on the product detail page that surfaces Viewed Products from the current Session, excluding the product currently on screen, ordered most-recently-viewed first.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Shoppers who have viewed two or more products can return to any previously viewed product in a single click, with no search or back-navigation required.
- **SC-002**: The strip appears on page load with no perceptible delay beyond the existing page render time.
- **SC-003**: Every product viewed earlier in the session (up to the agreed display cap) is present in the strip exactly once, in reverse-chronological order.
- **SC-004**: Shoppers who have viewed no other products in the current session see no strip — the product detail page layout is unchanged for first-time visitors.

## Assumptions

- "Session" is scoped to a single browser tab/window visit. Cross-device and cross-tab sync are out of scope (explicitly excluded by AIP-97).
- Products appear in the strip in reverse-chronological order (most recently viewed first) unless stakeholders specify otherwise.
- The feature applies to all shoppers regardless of login state.
- The strip displays a maximum of 5 products (most recently viewed first). When a shopper views more than 5 products, older entries are dropped. This cap was agreed from AIP-156's open question.
