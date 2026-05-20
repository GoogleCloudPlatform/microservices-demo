# Feature Specification: Wishlist — Save a Product for Later and View the Saved List

**Feature Branch**: `006-wishlist-save-view`
**Created**: 2026-05-20
**Status**: Draft
**Input**: AIP-159 — Save a product for later and view the saved list

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Save a product for later (Priority: P1)

A shopper browsing a product detail page finds something they like but aren't ready to buy. They click "Save for later" and receive immediate on-page feedback that the product has been added to their wishlist.

**Why this priority**: This is the core action of the feature. Nothing else in the wishlist flow is meaningful without the ability to save a product first.

**Independent Test**: Can be fully tested by visiting a product detail page, clicking "Save for later", and verifying the confirmation appears and the product appears on the wishlist page.

**Acceptance Scenarios**:

1. **Given** I am on a product detail page, **When** I click "Save for later", **Then** the product is added to my wishlist and I see an inline confirmation message on the page.
2. **Given** a product is already in my wishlist, **When** I visit its product detail page, **Then** the "Save for later" control reflects that it has already been saved (e.g., toggled state or disabled with "Saved" label).
3. **Given** a product is already in my wishlist, **When** I click "Save for later" again, **Then** no duplicate is added and the confirmation reflects the item was already saved.

---

### User Story 2 — View the saved list (Priority: P2)

A shopper who has saved one or more products navigates to their wishlist and sees all saved items displayed with enough information to identify and act on each one.

**Why this priority**: Viewing the saved items is the counterpart to saving — without this, the save action has no value. It is a direct sequel to Story 1 and needed for the feature to be complete.

**Independent Test**: Can be tested by saving at least one product and then navigating to the wishlist view, confirming each saved item shows its name, image, and price.

**Acceptance Scenarios**:

1. **Given** I have one or more saved products, **When** I navigate to my wishlist, **Then** I see each saved product displayed with its name, image, and price.
2. **Given** I have no saved products, **When** I navigate to my wishlist, **Then** I see an empty-state message indicating there are no saved items.
3. **Given** I am viewing my wishlist, **When** I look at the page, **Then** each product entry shows the name, thumbnail image, and formatted price.

---

### User Story 3 — Wishlist does not persist across sessions (Priority: P3)

A shopper who saved items in a previous visit starts a new browser session and finds their wishlist is empty, confirming the feature is session-scoped only.

**Why this priority**: This defines the intentional scope boundary (no accounts, no cross-session persistence) and must be verified to ensure no data leaks between sessions.

**Independent Test**: Can be tested by saving products, closing the browser tab, reopening the store, and confirming the wishlist is empty.

**Acceptance Scenarios**:

1. **Given** I saved products during a browser session, **When** I close the browser tab and open a new session, **Then** my wishlist is empty.
2. **Given** I am in an active session with saved items, **When** I navigate away and return within the same session, **Then** my saved items are still present.

---

### Edge Cases

- What does the user see when navigating to the wishlist with no saved items?
- How does the "Save for later" button look or behave when a product is already saved?
- Can a user save the same product more than once, and if so, how is this handled?
- What happens if the session expires mid-visit (e.g., tab left open for a very long time)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to save a product to their wishlist from the product detail page.
- **FR-002**: The system MUST display an inline confirmation on the product detail page when a product is successfully saved.
- **FR-003**: The wishlist MUST display each saved product with its name, thumbnail image, and price.
- **FR-004**: The wishlist MUST NOT contain duplicate entries for the same product.
- **FR-005**: The "Save for later" control MUST reflect the saved state when a product is already in the wishlist.
- **FR-006**: The wishlist MUST be accessible at any point during the user's browser session.
- **FR-007**: The wishlist MUST be empty at the start of every new browser session — no cross-session persistence.
- **FR-008**: The wishlist MUST be accessible via a list icon in the site header, positioned to the left of the cart icon, visible on all pages at all times.
- **FR-009**: The wishlist MUST display an empty-state message when no products have been saved.

### Key Entities

- **Wishlist**: A session-scoped, ordered collection of saved products. Contains zero or more WishlistItem entries. Exists only for the lifetime of the current browser session.
- **WishlistItem**: A reference to a saved product, carrying the product's identifier, name, image URL, and price. No duplicates within the same wishlist.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A shopper can save a product and see confirmation in under 2 seconds from clicking "Save for later".
- **SC-002**: A shopper can navigate to their wishlist and see all saved products without additional steps or page loads beyond the navigation action.
- **SC-003**: 100% of sessions that save products show an empty wishlist upon starting a new session — no data persists between sessions.
- **SC-004**: The wishlist displays all saved items without truncation or pagination for a reasonable session (up to 50 saved items).
- **SC-005**: The "Save for later" control correctly reflects saved vs. unsaved state on every product detail page visit within a session.

## Assumptions

- The wishlist is session-only: no user accounts, no login, no cross-device or cross-session persistence. A new browser tab or window counts as a new session.
- A product already saved to the wishlist cannot be added again — the system silently deduplicates by product identifier.
- The wishlist is not required to persist if the user navigates away and returns using the browser's back button (back-navigation behavior is implementation-defined).
- Wishlist item count is not capped, but sessions with very large numbers of items (>50) are not a primary design concern for this story.
- The feature covers saving and viewing only. Actions on wishlist items (add to cart, remove, navigate to PDP) are addressed in AIP-160.
- No new backend services or datastores are introduced; session storage is managed within the existing frontend.
- No changes to deployment manifests, infrastructure, or CI configuration are required.
