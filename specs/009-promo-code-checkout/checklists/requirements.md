# Specification Quality Checklist: Apply a valid promo code at checkout

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-06-16
**Feature**: [spec.md](../spec.md)

## Content Quality

- [ ] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [ ] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [ ] No implementation details leak into specification

## Notes

- **Content Quality / "No implementation details"** and **Feature Readiness / "No implementation details leak"** are intentionally left unchecked. The spec includes a **Constraints** section (C-001 to C-004) naming the repo's existing services, the in-memory `products.json` data source, and the Go language. This is a deliberate deviation: the user directed that the epic's technical-constraints section be carried in as **hard constraints**, which overrides the usual technology-agnostic rule for this spec.
- **One [NEEDS CLARIFICATION] marker remains** (FR-002 / Edge Cases): the base the 50% discount applies to (item subtotal only vs. subtotal plus shipping/taxes). This materially affects the amount charged, so it is surfaced as a question rather than silently assumed.
- All other items pass.
