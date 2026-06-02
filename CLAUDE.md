<!-- SPECKIT START -->
For additional context about technologies to be used, project structure,
shell commands, and other important information, read the current plan:

- Active feature: **Product Search (thin slice)** — branch `008-product-search`
- Plan: `specs/008-product-search/plan.md`
- Spec: `specs/008-product-search/spec.md`
- Research: `specs/008-product-search/research.md`
- Data model: `specs/008-product-search/data-model.md`
- Contracts: `specs/008-product-search/contracts/`
- Quickstart: `specs/008-product-search/quickstart.md`

Hard constraints in force (TC-001..TC-008 from the spec): case-insensitive substring on `Product.name` OR `Product.description` (no other fields); in-memory filtering over `products.json`; Go + existing protobuf/gRPC patterns; no new services, no new datastores, no new infra, no pipeline edits; merge to `attendee/matthew-buckland` for CI deploy.
<!-- SPECKIT END -->
