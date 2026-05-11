# DOM Interface Contract: Product Search

The search JavaScript (`static/js/search.js`) depends on the following DOM structure
being present in `home.html`. Any change to these elements is a **breaking change**
that requires updating `search.js` in the same commit.

## Elements the JS reads

| Selector | Element | Role |
|----------|---------|------|
| `#product-search-input` | `<input type="text">` | Search box — JS attaches `input` event listener here |
| `#search-clear-btn` | `<button>` | Clear button — JS shows/hides based on input value; click clears input and resets grid |
| `#search-result-count` | any block element | Result count display — JS sets text and shows/hides |
| `#search-no-results` | any block element | "No results" message — JS shows/hides when match count is zero |
| `.hot-product-card` | `<div>` (one per product) | JS shows/hides each card based on name match |
| `.hot-product-card-name` | `<div>` inside `.hot-product-card` | JS reads `.textContent` for name matching |

## Behaviour contract

- **On `input` event** on `#product-search-input`:
  - Trim and lowercase the current value.
  - For each `.hot-product-card`: show if `.hot-product-card-name` textContent (lowercased) includes the term; hide otherwise.
  - If value is empty/whitespace: show all cards, hide `#search-result-count`, hide `#search-no-results`, hide `#search-clear-btn`.
  - If value is non-empty: update `#search-result-count` text to "Showing N of M products" and show it; show `#search-clear-btn`; show `#search-no-results` if N === 0, hide otherwise.

- **On click** on `#search-clear-btn`:
  - Clear `#product-search-input` value.
  - Fire an `input` event on `#product-search-input` to trigger the filter reset.

## Total product count

The JS derives the total product count from `document.querySelectorAll('.hot-product-card').length` at filter time. No hardcoded count is used.
