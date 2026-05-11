# Quickstart: Product Search

## What's changing

Two files are modified, one file is added:

| File | Change |
|------|--------|
| `src/frontend/templates/home.html` | Add search box, clear button, result count, and no-results message above the product grid; add `<script>` tag referencing search.js |
| `src/frontend/static/js/search.js` | New file — browser-side filter logic |

No backend, no new services, no infrastructure changes.

## Running locally

```bash
# From repo root — build and run the frontend only (requires productcatalogservice running)
cd src/frontend
go run .
```

Or use the existing skaffold/docker-compose setup already in the repo.

## Verifying the feature

1. Open the home page in a browser.
2. Type "sun" in the search box — only "Sunglasses" should appear.
3. Type "watch" — only "Watch" should appear.
4. Type "WATCH" (uppercase) — same result as "watch".
5. Paste "tank" into the search box — "Tank Top" should appear.
6. Type a term with no matches (e.g., "zzz") — product grid is empty and "No products found for 'zzz'" is shown.
7. Click the "×" button — all products are restored, count disappears.
8. Clear the search box manually — same as step 7.

## Acceptance checklist

- [ ] FR-001: Search box visible above product grid
- [ ] FR-002: Grid updates on every keystroke from first character
- [ ] FR-002a: Placeholder text present (e.g., "Search products…")
- [ ] FR-003: Case-insensitive matching
- [ ] FR-004: Substring matching
- [ ] FR-005: Empty box shows all products
- [ ] FR-006: No-results message includes search term
- [ ] FR-007: Clearing restores full grid
- [ ] FR-008/009: No network requests or URL changes (verify in DevTools)
- [ ] FR-011: No autofocus on page load
- [ ] FR-012: Clear button appears only when box has text
- [ ] FR-013: No-results message includes the search term
- [ ] FR-014: Search icon visible on or beside the input
- [ ] FR-015: Result count shown while searching, hidden when box is empty
- [ ] Edge: Whitespace-only query shows all products
- [ ] Edge: Paste triggers filtering immediately
- [ ] Edge: Special characters (e.g., "&") match correctly
