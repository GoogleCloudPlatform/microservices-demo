# Research: Recently Viewed Strip

**Phase**: 0 — Outline & Research
**Feature**: `specs/004-recently-viewed-strip/spec.md`
**Date**: 2026-05-20

---

## Decision 1: Where to store the viewed-product history

**Decision**: Store the list of viewed product IDs in a browser cookie (`shop_recently_viewed`), following the existing `shop_session-id` / `shop_currency` cookie pattern already in the frontend.

**Rationale**:
- The hard constraint (HC-002) prohibits any new datastore. A cookie is client-side transport, not a datastore — consistent with how the frontend already tracks currency preference.
- The frontend server is stateless; using a server-side in-process map would break under multiple replicas and require a TTL/eviction mechanism.
- Cookie approach requires zero new infrastructure, no new service, and no changes to deployment manifests.
- Max payload is small: 5 product IDs × ~10 chars each = ~50 bytes, well within cookie limits.

**Alternatives considered**:
- **In-process `sync.Map` in the frontend server** (keyed by session ID): Fails under horizontal scaling; adds memory pressure without eviction; violates spirit of HC-003 (would require a sticky-session or shared-state change).
- **New Redis/memcached cache**: Explicitly prohibited by HC-002.
- **localStorage / client-side JS**: Requires JavaScript changes; inconsistent with the server-rendered Go template pattern used throughout the frontend.

---

## Decision 2: How to resolve product details for the strip

**Decision**: Use the existing `getProduct()` RPC call (already present in `rpc.go`) to fetch full `*pb.Product` for each ID read from the cookie. Calls are made in `productHandler` before template execution.

**Rationale**:
- The identical pattern is already used for recommendations: the recommendation service returns IDs, then the frontend fetches each product via `getProduct()`. Reusing this is consistent with existing code and requires no new RPC methods.
- `*pb.Product` already carries all fields needed for the strip: `Id`, `Name`, `Picture`, `PriceUsd`.

**Alternatives considered**:
- **Pass only IDs to the template and fetch client-side**: Requires JavaScript; inconsistent with server-rendered architecture.
- **Add a batch-fetch RPC**: Unnecessary complexity; 5 serial `getProduct()` calls in Go are fast enough and match existing patterns.

---

## Decision 3: Cookie encoding format

**Decision**: Store product IDs as a pipe-separated (`|`) string, e.g. `OLJCESPC7Z|L9ECAV7KIM|2ZYFJ3GM2N`. Pipe is safe in cookie values (RFC 6265) and simple to split in Go.

**Rationale**: Simpler than JSON; no import needed; easier to inspect manually during development. IDs in `products.json` use only alphanumeric characters.

---

## Decision 4: Cookie update logic (deduplication + cap)

**Decision**: On every `productHandler` invocation, prepend the current product ID to the list, deduplicate (keeping the most-recent occurrence), then truncate to 5 entries. Write the updated cookie before rendering.

**Rationale**: Matches FR-005 (current product excluded from strip — it is prepended then excluded at render time), FR-006 (cap of 5), and FR-007 (no duplicates). "Prepend then deduplicate" means re-visiting a product promotes it to position 1, matching the assumption in the spec.

---

## Decision 5: Template and styling approach

**Decision**: Add a new partial template `recently_viewed.html` following the exact same structure as the existing `recommendations.html`. Include it in `product.html` with the same conditional guard used for recommendations.

**Rationale**: Zero new patterns to learn or review; consistent UX; reuses existing CSS grid. Styling additions are minimal (a new section class) and go in the existing `styles.css`.

---

## All NEEDS CLARIFICATION items resolved

| Item | Resolution |
|------|-----------|
| Maximum strip display cap | 5 products (agreed by stakeholder 2026-05-20) |
| History persistence mechanism | Browser cookie `shop_recently_viewed` (no new datastore) |
| Duplicate handling | Deduplicate on write; most-recent visit promoted to position 1 |
| Ordering | Most recently viewed first (prepend strategy) |
