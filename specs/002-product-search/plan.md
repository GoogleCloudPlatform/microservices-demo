# Implementation Plan: Product Search

**Branch**: `002-product-search` | **Date**: 2026-05-11 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/002-product-search/spec.md`

## Summary

Add a browser-side search box to the Online Boutique home page that filters the already-rendered product grid by name on every keystroke. No backend changes. Implementation touches one Go template and adds one JavaScript file.

## Technical Context

**Language/Version**: Go 1.25.0 (frontend service); vanilla JavaScript (ES6, no build step)  
**Primary Dependencies**: Bootstrap 4.1.1 (already loaded via CDN); Go `html/template`  
**Storage**: N/A — products already rendered into DOM at page load  
**Testing**: `go test` for existing Go code; manual browser testing for the JS feature  
**Target Platform**: Desktop/tablet web browser (Chrome, Firefox, Safari)  
**Project Type**: Server-rendered web application (Go templates + browser JS)  
**Performance Goals**: Filter updates within 100ms of each keystroke  
**Constraints**: No new services, no new infrastructure, no backend API changes, no new JS dependencies  
**Scale/Scope**: ~10–20 products in the catalogue; single-page filter

## Constitution Check

The project constitution file is an unfilled template — no project-specific gates are defined. No violations to check.

## Project Structure

### Documentation (this feature)

```text
specs/002-product-search/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← not created (no new data entities)
├── quickstart.md        ← Phase 1 output
├── contracts/
│   └── dom-contract.md  ← Phase 1 output
└── tasks.md             ← Phase 2 output (/speckit-tasks — not yet created)
```

### Source Code (files changed)

```text
src/frontend/
├── templates/
│   └── home.html            ← modified: add search box UI + <script> tag
└── static/
    └── js/
        └── search.js        ← new: browser-side filter logic
```

No other files are touched.

## Phase 0: Research (complete)

See [research.md](research.md). All decisions resolved — no NEEDS CLARIFICATION items remain.

Key decisions:
- Vanilla JS `input` event listener — no debounce, no framework
- New `static/js/search.js` file — not inline in template
- Target existing `.hot-product-card` / `.hot-product-card-name` CSS classes
- No changes to Go handlers or productView struct

## Phase 1: Design (complete)

### Data Model

No new data entities. The feature reads product names already present in the rendered DOM. No `data-model.md` created.

### DOM Interface Contract

See [contracts/dom-contract.md](contracts/dom-contract.md).

The JS depends on these DOM elements (all added to `home.html`):

| ID / Class | Purpose |
|---|---|
| `#product-search-input` | Text input — filter trigger |
| `#search-clear-btn` | Clear button — shown when input is non-empty |
| `#search-result-count` | "Showing N of M products" — shown during active search |
| `#search-no-results` | "No products found for '…'" — shown when N=0 |
| `.hot-product-card` | Existing — each product card (shown/hidden by filter) |
| `.hot-product-card-name` | Existing — product name text read for matching |

### Quickstart

See [quickstart.md](quickstart.md) for local dev instructions and the full acceptance checklist.

## Complexity Tracking

No constitution violations. No complexity justification required.
