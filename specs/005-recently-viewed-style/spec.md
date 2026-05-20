# Feature Specification: Recently Viewed Strip — Style Parity with Recommendations

**Feature Branch**: `005-recently-viewed-style`
**Created**: 2026-05-20
**Status**: Draft
**Source**: Observed defect post-implementation of AIP-156 / `004-recently-viewed-strip`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Recently Viewed Strip Looks Like the Recommendations Strip (Priority: P1)

A shopper arrives on a product detail page that shows both a "You May Also Like" strip and a "Recently Viewed" strip. Both strips look visually consistent: same image size, same card proportions, same typography, same spacing. The "Recently Viewed" strip does not show oversized images that dwarf the recommendations above it.

**Why this priority**: The current implementation renders product images at full natural height in the "Recently Viewed" strip, making the strip unusable and visually broken. This is the entire purpose of this work.

**Independent Test**: Open any product detail page after viewing two or more products. Both strips are visible on the same page. Hold a ruler (or use browser devtools) to compare image dimensions and card layout between the two strips — they must be indistinguishable in size and proportion.

**Acceptance Scenarios**:

1. **Given** both the "You May Also Like" and "Recently Viewed" strips are visible on a product detail page, **When** I look at both strips side by side, **Then** the product card dimensions, image sizes, and typography in the "Recently Viewed" strip match those in the "You May Also Like" strip.
2. **Given** the "Recently Viewed" strip is visible, **When** I view it on a desktop screen, **Then** product cards are displayed in the same compact grid layout as the recommendations strip (no oversized images).
3. **Given** the "Recently Viewed" strip is visible, **When** I view it on a narrow (mobile) screen, **Then** the strip responds in the same way as the recommendations strip.

---

### Edge Cases

- What if a product has a very tall or very wide image — does the card maintain consistent proportions regardless of the image's natural aspect ratio?
- What if only one or two products are in the strip — does the layout still look reasonable without filling all four columns?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The "Recently Viewed" strip MUST use the same card dimensions as the "You May Also Like" strip — same image height, same card width, same internal spacing.
- **FR-002**: Product images in the "Recently Viewed" strip MUST be constrained to the same fixed dimensions as in the recommendations strip; images MUST NOT render at their natural (full) size.
- **FR-003**: The "Recently Viewed" strip MUST use the same responsive grid breakpoints as the recommendations strip so that both strips reflow identically on narrow screens.
- **FR-004**: The "Recently Viewed" strip heading, product name typography, and section background MUST match those of the "You May Also Like" strip.
- **FR-005**: The fix MUST NOT alter the appearance or behaviour of the existing "You May Also Like" strip.

### Hard Constraints *(from Epic AIP-97 — still in effect)*

- **HC-001**: Only existing services in the repository may be modified. No new services.
- **HC-002**: No new datastores introduced.
- **HC-003**: No changes to infrastructure, deployment manifests, or CI configuration.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A shopper viewing a product detail page cannot visually distinguish the card size or image proportions between the "You May Also Like" and "Recently Viewed" strips.
- **SC-002**: No product image in the "Recently Viewed" strip is taller than the equivalent image in the "You May Also Like" strip on the same page.
- **SC-003**: The fix introduces no visible regression to the "You May Also Like" strip.

## Assumptions

- The correct reference for visual style is the existing "You May Also Like" (recommendations) strip as rendered in the browser — not a design file.
- The fix is CSS/template only; no changes to Go handler logic or cookie behaviour are needed.
- Mobile responsiveness should match whatever the recommendations strip already does at each breakpoint.
