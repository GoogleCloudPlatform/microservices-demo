# PRD: Product Category Filtering
**Status:** Draft  **Author:** Product Team  **Date:** 2026-05-26

## Problem Statement

Online Boutique currently supports a single product discovery mechanism: free-text search. The `SearchProducts` call on `ProductCatalogService` accepts only a text query string and returns products whose name or description contains a substring match. There is no way for a user to browse by category.

This is a problem because the catalog has a well-defined, stable taxonomy of 9 categories — accessories, clothing, tops, footwear, hair, beauty, decor, home, kitchen — and users frequently arrive at the site with a category intent ("I want to buy something for the kitchen") rather than a product intent ("I want to buy a spatula"). Without category filtering, these users must either scroll the full product grid or guess text terms that happen to match catalog descriptions.

Analytics data shows that the home page has a high exit rate from users who do not enter a search query, suggesting they could not find an entry point for browsing. Adding category filters is expected to improve product discovery and reduce early exits.

## Goals

- Allow users to filter the product grid by one or more product categories.
- Category filter UI should be available on the home page and on the search results page.
- Filtering must work with or without a text search query (category-only filter, text-only search, and combined text+category search should all be supported).
- The category taxonomy displayed in the UI must reflect the actual categories present in the product catalog.

## Non-Goals

- Dynamic or user-defined categories. The category set is a closed, hardcoded list managed by the catalog team. Adding a new category requires a catalog rebuild and is out of scope for this feature.
- Category hierarchy or subcategories — the taxonomy is flat.
- Filtering by attributes other than category (price range, availability, etc.) — those are separate roadmap items.
- Search relevance ranking changes — the underlying text match logic in `ProductCatalogService` is not being modified.
- Any change to the checkout flow, cart, or payment services.

## User Stories

**US-1:** As a shopper with a general intent, I want to click a category chip on the home page (e.g., "Kitchen") and see only products in that category, so that I can browse a focused set of items without needing to know exact product names.

**US-2:** As a shopper using the search bar, I want to narrow my results to a specific category alongside my text query, so that searching "green" in "Clothing" does not also show green home decor items.

**US-3:** As a shopper, I want to select multiple categories at once (e.g., "Home" and "Decor") to browse a combined view.

**US-4:** As a shopper, I want the category filter to be easy to clear so I can return to the full product grid without reloading the page.

## Category Taxonomy

The categories available today are a closed, hardcoded set:

`accessories`, `clothing`, `tops`, `footwear`, `hair`, `beauty`, `decor`, `home`, `kitchen`

These are defined in the `products.json` file loaded by `ProductCatalogService` at startup. They are not stored in a database. Adding a new category requires adding products tagged with that category to `products.json` and rebuilding the `productcatalogservice` container image. This constraint applies to this feature as well — the UI must only ever display categories that actually exist in the catalog.

## Requirements

**R-1 — Backend filter support:** `ProductCatalogService` must support filtering products by one or more category values. A product is included in the result if it belongs to at least one of the requested categories.

**R-2 — Proto change:** The `SearchProductsRequest` message currently only has a `query` field. A `categories` field must be added to support category-based filtering. The change must be backward compatible — callers that do not send `categories` get the current full/unfiltered behavior.

**R-3 — Frontend UI:** Category filter controls (chips or checkboxes, per design system) must appear above the product grid on the home page and search results page. The set of categories displayed must be derived from the catalog (not hardcoded in the UI).

**R-4 — URL-reflected state:** Active category filters should be reflected in the page URL (e.g., `?category=clothing&category=tops`) so that filtered views can be bookmarked and shared.

**R-5 — Combined filter:** Text search and category filter must be composable — a request can carry both a query string and a category list simultaneously.

**R-6 — Backward compatibility:** Any service that currently calls `SearchProducts` or `ListProducts` and does not pass a category filter must continue to receive full results with no behavior change.

## Success Metrics

- Conversion rate (add-to-cart events per session) increases by at least 8% for sessions that use the category filter within 30 days of launch.
- Home page exit rate (sessions with only one page view) decreases by 10% within 30 days.
- Zero regressions in checkout flow — no increase in checkout errors or failed `PlaceOrder` calls post-deploy.
- Category filter UI renders correctly on mobile viewport (375px minimum width).

## Open Questions

1. **Multi-select UX:** Should selecting multiple categories be an OR (show products in any of the selected categories) or AND (show products that belong to all selected categories) operation? Most products will only have one category, so AND would return very few results for most combinations. The requirements above assume OR.
2. **"All" / clear state:** When no category is selected, do we show all products (current behavior) or require the user to explicitly select at least one category? The current intent is to show all products when no filter is active.
3. **Category display names:** The catalog uses lowercase slug-style values (`hair`, `decor`). Should the UI display these as-is, or apply title-case formatting (`Hair`, `Decor`)?
4. **Empty results state:** If a text search + category combination returns zero products, what message do we show?
