# Implementation Plan: Apply a valid promo code at checkout

**Branch**: `009-promo-code-checkout` | **Date**: 2026-06-16 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/009-promo-code-checkout/spec.md`

## Summary

Add a promo-code entry to the existing checkout (cart) page in the **frontend** Go service. When a shopper enters the hardcoded code `50OFF` and applies it, the basket items total is discounted by 50% (shipping excluded), an inline confirmation is shown, and the discounted total is what the order confirmation reports as paid. With no code entered, checkout is byte-for-byte identical to today. The valid-code set is a hardcoded in-memory map; invalid-code feedback and code-replacement are sibling stories (AIP-179/AIP-180) and out of scope here.

## Technical Context

**Language/Version**: Go (frontend service — `src/frontend`, module `go 1.x` per `go.mod`)

**Primary Dependencies**: `gorilla/mux` (routing), `html/template` (server-rendered pages), existing `money` helper package, gRPC clients to cart/product/currency/shipping/checkout services.

**Storage**: None added. Applied code is held client-side in a cookie (`shop_promo`); the code→discount set is an in-memory Go map. No database/cache/search engine (constraint C-002).

**Testing**: `go test ./...` in `src/frontend` (unit tests for the discount math and promo lookup). Manual verification via the running app (quickstart.md).

**Target Platform**: Linux container, served at the existing frontend `/cart` routes.

**Project Type**: Web application (server-rendered Go frontend over existing microservices).

**Performance Goals**: No new network calls on the discount path; discount is pure in-memory arithmetic. No measurable change to checkout latency.

**Constraints**: Epic AIP-96 hard constraints C-001..C-004 — existing services only, no new datastore, match Go patterns of the service changed, no infra/manifest/CI changes.

**Scale/Scope**: Single service (`src/frontend`); ~1 new source file, edits to 3 existing files (`handlers.go`, `main.go`, `cart.html`) plus `order.html`; one hardcoded code.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The project constitution (`.specify/memory/constitution.md`) is the unmodified template with no ratified principles, so there are no project-specific gates to enforce. The epic's technical constraints (C-001..C-004) are treated as the binding gate instead:

- **C-001 existing services only** — PASS: change is confined to the existing `frontend` service. No new services.
- **C-002 no new datastore** — PASS: applied code stored in a cookie; code set is an in-memory map.
- **C-003 match language/patterns** — PASS: implemented in Go using the existing `money` package, `mux` routes, cookie helpers, and `html/template`, mirroring existing handlers.
- **C-004 no infra/manifest/CI changes** — PASS: only application source and templates change; ships through the existing pipeline unmodified.

No violations → Complexity Tracking not required.

## Project Structure

### Documentation (this feature)

```text
specs/009-promo-code-checkout/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output (UI/route contract)
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
src/frontend/
├── main.go              # add cookie name + POST /cart/promo route
├── handlers.go          # viewCartHandler (compute discount), placeOrderHandler (apply to total paid), applyPromoHandler (new)
├── promo.go             # NEW: hardcoded code→rate map, lookup, discount math
├── promo_test.go        # NEW: unit tests for lookup + discount math
├── money/money.go       # (unchanged) reused for Sum/Negate
└── templates/
    ├── cart.html        # promo input form + confirmation + discount line
    └── order.html       # discount line on confirmation
```

**Structure Decision**: All changes live in the existing `src/frontend` Go service — the only place that renders the checkout page and computes the displayed/charged total. No other service is touched, satisfying C-001..C-004.

## Complexity Tracking

Not applicable — no constitution/constraint violations to justify.
