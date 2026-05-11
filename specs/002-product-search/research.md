# Research: Product Search

**Feature**: 002-product-search  
**Date**: 2026-05-11

## Decisions

### 1. Filtering approach: browser-side JavaScript, no backend change

**Decision**: Pure browser-side filtering using vanilla JavaScript listening to the `input` event on the search box.

**Rationale**: The spec explicitly mandates no backend change and no new services. All products are already rendered into the DOM by the Go template on page load. A plain `input` event listener on the search box is sufficient to cover both typing and paste (FR-002, paste edge case).

**Alternatives considered**:
- Debounced filtering: rejected — spec explicitly states no debounce is needed and the catalogue is small (~10–20 items).
- `keyup` event only: rejected — does not fire on paste; `input` event covers all mutations including paste, cut, and autocomplete.
- Form submission / server-side filtering: rejected — spec prohibits network requests or page navigation.

---

### 2. JS delivery: new static file vs. inline in template

**Decision**: New static file at `src/frontend/static/styles/` … wait — JS files belong in a dedicated location. Since there is no existing `static/js/` directory, create `src/frontend/static/js/search.js` and reference it from `home.html`.

**Rationale**: Keeps `home.html` readable, keeps JS separately cacheable, and follows the existing pattern of separate CSS files per feature (styles.css, cart.css, order.css). Inline JS in a Go template would make the template harder to maintain.

**Alternatives considered**:
- Inline `<script>` in `home.html`: rejected — harder to test, harder to read, inconsistent with project CSS patterns.

---

### 3. DOM targeting strategy: CSS class selectors

**Decision**: Target `.hot-product-card` divs and read the `.hot-product-card-name` text content for matching.

**Rationale**: These classes already exist on every product card in `home.html`. No new data attributes need to be added to the Go template. The name is already the visible text node inside `.hot-product-card-name`.

**Alternatives considered**:
- `data-product-name` attribute on each card: would require modifying the Go template but would be more robust to future DOM changes. Rejected for now to minimise the diff — the existing class is sufficient for this feature.

---

### 4. No new Go template data needed

**Decision**: No changes to the `homeHandler` in `handlers.go` or the `productView` struct.

**Rationale**: All product names are already rendered into the DOM. The search feature reads them from the DOM at filter time; it does not need the Go backend to pass additional data.

---

### 5. Testing approach

**Decision**: Manual browser testing against the running service; no automated JS test suite.

**Rationale**: The project has no existing JS test infrastructure (no Jest, Mocha, or similar). Adding a test framework for a single ~50-line script would violate the constraint of not introducing new infrastructure. The existing Go tests (`validator_test.go`, `money_test.go`) use `go test` and are unaffected.

**Alternatives considered**:
- Adding Jest: rejected — out of scope per constraints.
- Playwright/Cypress end-to-end test: rejected — no existing E2E infrastructure in this repo.
