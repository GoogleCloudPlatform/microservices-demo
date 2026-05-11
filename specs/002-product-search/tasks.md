---
description: "Task list for Product Search feature implementation"
---

# Tasks: Product Search

**Input**: Design documents from `specs/002-product-search/`  
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, contracts/dom-contract.md ✓, quickstart.md ✓

**Tests**: Not requested in spec — no test tasks generated.

**Organization**: Tasks grouped by user story. Two files change total:
- `src/frontend/templates/home.html` — DOM scaffold + script tag
- `src/frontend/static/js/search.js` — new file, filter logic

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)

---

## Phase 1: Setup

**Purpose**: Create the directory needed for the new JS file.

- [x] T001 Create directory `src/frontend/static/js/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the search UI scaffold to `home.html` so both user stories have the required DOM elements. The JS in Phase 3 depends on this structure existing.

**⚠️ CRITICAL**: Must be complete before Phase 3 or Phase 4 begin.

- [x] T002 Add search box scaffold to `src/frontend/templates/home.html` — insert above the `.hot-products-row` div: a text input with id `product-search-input` and placeholder "Search products…", a clear button with id `search-clear-btn` (hidden by default), a result count element with id `search-result-count` (hidden by default), and a no-results message element with id `search-no-results` (hidden by default). Follow the DOM contract in `specs/002-product-search/contracts/dom-contract.md`.

**Checkpoint**: Open the home page — search box, hidden clear button, and hidden count/no-results elements are present in the HTML source.

---

## Phase 3: User Story 1 — Filter Products by Name (Priority: P1) 🎯 MVP

**Goal**: Typing in the search box filters the visible product cards to those whose names contain the search term (substring match). Clearing the box restores all products. No-results message, result count, and clear button all work correctly.

**Independent Test**: Open the home page, type "sun" — only Sunglasses appears. Type "zzz" — grid is empty with a "No products found for 'zzz'" message. Clear the box — all products return.

### Implementation for User Story 1

- [x] T003 [US1] Implement `src/frontend/static/js/search.js` — attach an `input` event listener to `#product-search-input`; on each event: trim and lowercase the value; show/hide each `.hot-product-card` based on whether its `.hot-product-card-name` text content (lowercased) includes the term; if value is empty/whitespace show all cards and hide `#search-result-count`, `#search-no-results`, `#search-clear-btn`; if value is non-empty show `#search-clear-btn`, update `#search-result-count` text to "Showing N of M products" and show it, show `#search-no-results` (with search term in message) only when N is 0. Also attach a `click` listener to `#search-clear-btn` that clears the input and fires an `input` event. Derive total product count from `document.querySelectorAll('.hot-product-card').length`. See `specs/002-product-search/contracts/dom-contract.md` for the full behaviour contract.
- [x] T004 [US1] Add `<script src="{{ $.baseUrl }}/static/js/search.js"></script>` to `src/frontend/templates/home.html` just before the closing `</main>` tag (after the product grid, before the footer template call).
- [x] T005 [P] [US1] Add CSS for the search box to `src/frontend/static/styles/styles.css` — style `#product-search-input` to be visually distinct from other inputs (full-width or prominent width, search icon via background-image or adjacent icon element), style `#search-clear-btn` to appear inside or beside the input, style `#search-result-count` and `#search-no-results` with appropriate text size and colour.

**Checkpoint**: User Story 1 fully functional. Typing filters cards, clear button appears/disappears, result count updates, no-results message appears with search term, clearing restores full grid. No network requests fire (verify in DevTools Network tab).

---

## Phase 4: User Story 2 — Case-Insensitive Matching (Priority: P2)

**Goal**: The same filter from US1 works regardless of the capitalisation the shopper uses.

**Independent Test**: With "Sunglasses" in the catalogue, type "SUNGLASSES", "sunglasses", and "SuNgLaSsEs" — all three show the Sunglasses card.

### Implementation for User Story 2

- [x] T006 [US2] Verify `src/frontend/static/js/search.js` already lowercases both the search term and `.hot-product-card-name` text content before comparison (this should be true if T003 was implemented correctly per the contract). If not, update the comparison to use `.toLowerCase()` on both sides.

**Checkpoint**: User Stories 1 and 2 both pass. All three capitalisation variants of a product name return the same result.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and any remaining edge case verification.

- [ ] T007 Run the full acceptance checklist in `specs/002-product-search/quickstart.md` ⬅ requires browser verification — verify every FR item and every edge case (whitespace-only query, paste, special characters, no autofocus on page load).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — **blocks Phase 3 and Phase 4**
- **User Story 1 (Phase 3)**: Depends on Phase 2 — T003 and T005 can run in parallel; T004 depends on T003
- **User Story 2 (Phase 4)**: Depends on Phase 3 (T003 must exist) — single verification task
- **Polish (Phase 5)**: Depends on Phase 3 and Phase 4 complete

### User Story Dependencies

- **US1 (P1)**: Can start after Phase 2 — no dependency on US2
- **US2 (P2)**: Depends on T003 (search.js) existing — verifies/amends the same file

### Within Phase 3

- T003 and T005 touch different files (`search.js` vs `styles.css`) — can run in parallel [P]
- T004 depends on T003 (the script file must exist before referencing it)

---

## Parallel Opportunities

```
# Phase 3 parallel work (different files):
T003: Implement src/frontend/static/js/search.js
T005: Add CSS to src/frontend/static/styles/styles.css
# Then sequentially:
T004: Wire <script> tag in home.html (after T003)
```

---

## Implementation Strategy

### MVP (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: Foundational (T002)
3. Complete Phase 3: User Story 1 (T003 → T004, T005 in parallel)
4. **STOP and VALIDATE**: Substring filter works end-to-end
5. Ship — delivers full core value

### Incremental Delivery

1. T001 → T002 → T003 + T005 → T004: Core filter live (MVP)
2. T006: Case-insensitive matching confirmed
3. T007: Full acceptance checklist passes

---

## Notes

- [P] tasks touch different files and have no blocking dependencies on each other
- [US1]/[US2] labels map tasks to spec.md user stories for traceability
- No new Go code, no new services, no infrastructure changes
- Total tasks: **7** (T001–T007)
- T006 is intentionally minimal — if T003 is written correctly it is a verification step only
