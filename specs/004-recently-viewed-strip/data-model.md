# Data Model: Recently Viewed Strip

**Phase**: 1 — Design
**Feature**: `specs/004-recently-viewed-strip/spec.md`
**Date**: 2026-05-20

---

## Entities

### RecentlyViewedList (runtime / cookie)

Represents the ordered list of product IDs viewed by a shopper during the current session. Stored entirely in a browser cookie — no server-side persistence.

| Field | Type | Description |
|-------|------|-------------|
| ProductIDs | `[]string` | Ordered list of product IDs, most-recently viewed first. Max 5 entries. No duplicates. |

**Cookie name**: `shop_recently_viewed`
**Cookie encoding**: pipe-separated string, e.g. `OLJCESPC7Z|L9ECAV7KIM|2ZYFJ3GM2N`
**Cookie max-age**: reuses the existing `cookieMaxAge` constant (48 hours), consistent with `shop_session-id`

**Invariants**:
- Length ≤ 5
- No duplicate IDs
- Current product being viewed is NOT in the list at render time (it is excluded during template data preparation, not during cookie write)

---

### Product (existing — `*pb.Product`)

No new fields. The existing protobuf `Product` message is used as-is for strip rendering.

| Field | Used by strip? | Source |
|-------|---------------|--------|
| `Id` | Yes — for navigation links and deduplication | ProductCatalogService |
| `Name` | Yes — strip item label | ProductCatalogService |
| `Picture` | Yes — strip item thumbnail | ProductCatalogService |
| `PriceUsd` | Optional — can be shown for comparison | ProductCatalogService |
| `Description` | No | — |
| `Categories` | No | — |

---

## State Transitions

```
Request arrives at productHandler (product ID = X)
        │
        ▼
Read cookie shop_recently_viewed → parse to []string
        │
        ▼
Prepend X to list
        │
        ▼
Deduplicate (keep first occurrence = most recent)
        │
        ▼
Truncate to max 5 entries
        │
        ▼
Write updated cookie (shop_recently_viewed)
        │
        ▼
Exclude X from list for template rendering
        │
        ▼
Fetch *pb.Product for each remaining ID via getProduct() RPC
        │
        ▼
Pass [](*pb.Product) as "recently_viewed" to product.html template
        │
        ▼
Template renders strip if len(recently_viewed) > 0
```

---

## Cookie Update Algorithm (pseudocode)

```
func updateRecentlyViewed(cookie string, currentID string) (updated string, forRender []string) {
    ids = split(cookie, "|")          // may be empty on first visit
    ids = prepend(currentID, ids)
    ids = deduplicate(ids)            // keep first occurrence of each ID
    ids = truncate(ids, 5)
    updated = join(ids, "|")
    forRender = ids[1:]               // exclude index 0 (current product)
    return
}
```

---

## No New Contracts

This feature makes no changes to any service interface. It is contained entirely within the frontend's HTTP handler and template layer. No new gRPC methods, REST endpoints, or protobuf messages are introduced.
