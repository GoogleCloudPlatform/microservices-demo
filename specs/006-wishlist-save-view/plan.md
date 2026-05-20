# Implementation Plan: Wishlist — Save a Product for Later and View the Saved List

**Branch**: `006-wishlist-save-view` | **Date**: 2026-05-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/006-wishlist-save-view/spec.md`

## Summary

Shoppers need a way to save products they like but aren't ready to buy, and return to them at any point in the same browsing session. This feature adds a session-scoped wishlist to the Go frontend service: a "Save for later" button on every product detail page, a list-icon entry point in the site header (left of the cart), and a dedicated wishlist view page. State is stored in a browser cookie (`shop_wishlist`) using the identical pattern already established by the recently-viewed feature. No new services, datastores, or infrastructure changes are required.

## Technical Context

**Language/Version**: Go 1.21 (frontend service — `src/frontend/`)
**Primary Dependencies**: `gorilla/mux` (routing), `html/template` (server-side rendering), `gorilla/sessions` not used — cookie-only state management
**Storage**: Browser cookie `shop_wishlist` — pipe-delimited product IDs; no server-side datastore
**Testing**: Go `testing` package; existing tests in `src/frontend/validator/`
**Target Platform**: Server-rendered web app; Linux container (Docker/Kubernetes)
**Project Type**: Web service (Go HTTP frontend)
**Performance Goals**: Save action completes in under 2 seconds (cookie write + redirect — effectively instant); wishlist page load bounded by product catalogue RPC latency
**Constraints**: No new services; no new datastores; no infra/CI changes; match Go patterns and templates of the existing frontend
**Scale/Scope**: Session-scoped only; single frontend service; change confined to `src/frontend/`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution file is unpopulated (template placeholders only). No project-specific gates apply. General constraints from the epic (AIP-94) are used instead:

| Constraint | Status | Notes |
|------------|--------|-------|
| No new services | PASS | All changes confined to `src/frontend/` |
| No new datastores | PASS | Cookie storage only — no Redis, DB, or in-memory service |
| Match existing language/patterns | PASS | Go + gorilla/mux + html/template; cookie pattern mirrors `shop_recently-viewed` |
| No infra/deployment/CI changes | PASS | No Kubernetes manifests, Dockerfiles, or CI configs touched |

Post-design re-check: **PASS** — Phase 1 design introduces no violations.

## Project Structure

### Documentation (this feature)

```text
specs/006-wishlist-save-view/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
├── contracts/
│   └── http-routes.md   ← Phase 1 output
└── tasks.md             ← Phase 2 output (/speckit-tasks — not yet created)
```

### Source Code (changes confined to frontend service)

```text
src/frontend/
├── main.go                        ← add cookieWishlist constant; register /wishlist routes
├── handlers.go                    ← add saveToWishlistHandler, viewWishlistHandler,
│                                     wishlistFromCookie, updateWishlist helpers;
│                                     update injectCommonTemplateData (wishlist_size);
│                                     update productHandler (in_wishlist, just_saved)
├── templates/
│   ├── header.html                ← add wishlist icon link before cart icon
│   ├── product.html               ← add Save for later form + saved confirmation banner
│   └── wishlist.html              ← NEW — wishlist page template
└── static/
    └── styles/styles.css          ← minor additions only if wishlist needs unique styles
                                      (reuse .cart-size-circle for badge)
```

**Structure Decision**: Single project (the existing frontend service). All changes are additive within the existing file layout — no new packages or directories in the source tree.

## Complexity Tracking

No constitution violations requiring justification.
