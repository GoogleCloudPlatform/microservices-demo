# Prompt: Generate a PRD + Design Doc for an Eval Scenario

Use this prompt with an AI assistant (Claude, etc.) to generate a new PRD and Design Doc for the AI Change Impact Analyzer eval suite.
Everyone on the team uses this same prompt to ensure consistent format, headings, and quality across all documents.

---

## HOW TO USE THIS PROMPT

1. Copy everything below the `---BEGIN PROMPT---` line.
2. Replace `[YOUR SCENARIO]` with a short description of the change you want to evaluate (e.g., "Add real-time inventory tracking", "Migrate cart storage to Cloud Spanner", "Add GDPR data deletion endpoint").
3. Paste into your AI assistant and run it.
4. Save the two output files into the `evals/` folder of the repo.

---BEGIN PROMPT---

You are writing engineering documents for the **AI Change Impact Analyzer** capstone project (Team 7).

The system under analysis is **Online Boutique** — a Google Cloud microservices demo e-commerce application.
Your job is to write **one PRD** and **one Design Doc** for the following proposed change:

> **[YOUR SCENARIO]**

---

## SYSTEM REFERENCE

Use the facts below to ground your documents. Do not invent services, ports, or behaviors that are not listed here.

### Services

| Service | Language | Port | Notes |
|---|---|---|---|
| frontend | Go | 8080 (HTTP) | Only externally-exposed service. Generates session UUID cookie `shop_session-id`. |
| cartservice | C# | 7070 | Stores cart in Redis. Keyed by `user_id` (= session UUID). |
| productcatalogservice | Go | 3550 | Serves 9 products from a static JSON file. RPCs: `ListProducts`, `GetProduct`, `SearchProducts`. |
| currencyservice | Node.js | 7000 | **Highest-QPS service.** Converts prices on every page render. Rates in `currency_conversion.json`. Base currency = EUR. |
| paymentservice | Node.js | 50051 | Mock credit card charge. Returns a UUID transaction ID. |
| shippingservice | Go | 50051 | Mock shipping quote + tracking ID. |
| emailservice | Python | 8080 (gRPC) | Mock order confirmation. Just logs. |
| checkoutservice | Go | 5050 | **Critical path orchestrator.** 16 dependency edges in the graph. |
| recommendationservice | Python | 8080 | Returns up to 5 random product IDs. Calls `ProductCatalogService.ListProducts`. |
| adservice | Java | 9555 | Text ads. Leaf node. Frontend renders empty slot on failure — graceful degradation. |
| redis-cart | Redis | 6379 | **Ephemeral by default** (in-cluster pod with no persistent volume). Cart lost on pod restart. |

### PlaceOrder critical path (checkoutservice)
1. `CartService.GetCart`
2. `ProductCatalogService.GetProduct` (per cart item)
3. `CurrencyService.Convert`
4. `ShippingService.GetQuote`
5. `ShippingService.ShipOrder`
6. `PaymentService.Charge` ← money moves here; point of no return
7. `EmailService.SendOrderConfirmation` ← failure is silently dropped, no retry
8. `CartService.EmptyCart`

### Key constraints to reference when relevant

- **No user accounts.** Session = UUID in `shop_session-id` cookie. No persistent user identity.
- **No order persistence.** `OrderResult` exists only in memory for the duration of the `PlaceOrder` response.
- **No auth anywhere.** gRPC calls are plaintext. No mTLS in base deployment.
- **No retry queue.** If any post-payment step fails, it is silently dropped (same pattern as EmailService).
- **PlaceOrderRequest field 4 is RESERVED.** A field was removed in the past. Field 4 must never be reused — doing so causes silent data corruption.
- **Product categories are a closed set:** accessories, clothing, tops, footwear, hair, beauty, decor, home, kitchen. Defined in `products.json`.
- **`SearchProductsRequest` has only `string query = 1`.** No category filter field exists today.
- **`Address.zip_code` is `int32`** — cannot hold leading-zero ZIPs or international alphanumeric postal codes.
- **`ENABLE_STATS` is a no-op.** Documented in manifests but not wired up in any service code.
- **SIGUSR1 on productcatalogservice** enables a deliberate CPU-burning bug (re-parses JSON on every request). Never enable in benchmarking.
- **CurrencyService failures affect every page.** It is called multiple times per page render.
- **Default Redis is ephemeral.** Features that assume cart durability across pod restarts will not work with the default deployment.

### Core proto types
```protobuf
message Money {
  string currency_code = 1;
  int64  units         = 2;
  int32  nanos         = 3;
}

message Address {
  string street_address = 1;
  string city           = 2;
  string state          = 3;
  string country        = 4;
  int32  zip_code       = 5;  // int32 — cannot hold leading-zero or alphanumeric codes
}

message PlaceOrderRequest {
  string         user_id       = 1;
  string         user_currency = 2;
  Address        address       = 3;
  // field 4 RESERVED — never reuse
  string         email         = 5;
  CreditCardInfo credit_card   = 6;
}

message SearchProductsRequest {
  string query = 1;  // no category filter exists today
}
```

---

## DOCUMENT 1 — PRD

Write a Product Requirements Document using **exactly this structure and these headings**:

```
# PRD: [Title]
**Status:** Draft  **Author:** Product Team  **Date:** [today's date]

## Problem Statement
[2–4 sentences. What user or business problem does this solve? Why now?]

## Goals
[Bullet list. What must be true when this ships?]

## Non-Goals
[Bullet list. What is explicitly out of scope? Be specific.]

## User Stories
[3–5 user stories in "As a [role], I want [action] so that [outcome]" format.]

## Requirements
[Numbered list. Functional requirements only. Reference current system behavior where relevant
 (e.g., "Currently, orders are not persisted after checkout completes...").]

## Success Metrics
[How will you know this worked? 2–4 measurable criteria.]

## Open Questions
[2–4 genuine open questions the team needs to resolve before or during implementation.]
```

Target length: **400–600 words**.

---

## DOCUMENT 2 — DESIGN DOC

Write an Engineering Design Document using **exactly this structure and these headings**:

```
# Design Doc: [Title]
**Status:** Draft  **Author:** Engineering Team  **Date:** [today's date]

## Background
[What is the current system state relevant to this change? Reference specific services,
 RPCs, proto fields, and known constraints. 3–6 sentences.]

## Current State
[More detailed breakdown: which services are involved today, what the relevant proto
 definitions look like, what does NOT exist yet. Use subsections if needed.]

## Proposed Solution
[The full engineering proposal. Subsections for each major component:
 new services, proto changes, logic changes, UI changes.
 Include actual proto definitions for any new or modified messages.
 Include actual field numbers. Do not use placeholder names.]

## Affected Services
[Table with columns: Service | Change
 List every service. If a service has no changes, say "No changes".]

## API / Proto Changes
[Enumerate every change to demo.proto or any new .proto file.
 Show before/after for modified messages. Note backward compatibility.]

## Data Model
[If persistent storage is introduced: schema with column names, types, and indexes.
 If no new storage: state "No new persistent storage introduced."]

## Deployment Plan
[Ordered steps. Include rollback strategy.]

## Risks & Open Questions
[4–6 items. For each: describe the risk and, where possible, a mitigation or
 the reason it is deferred. Do not rate risks as High/Medium/Low —
 describe them factually and let the reader assess.]
```

Target length: **700–1000 words**.

---

## RULES — READ BEFORE WRITING

1. **Do NOT label the overall change as "high risk", "medium risk", or "low risk" anywhere in either document.** Risk signals must be embedded naturally — in what services are affected, what proto changes are required, what constraints are hit. An AI system will evaluate these documents and must derive the risk level from the content.

2. **Use real service names, real port numbers, and real proto field numbers** from the System Reference above. Do not invent names.

3. **Reference constraints when they apply.** If your change touches the checkout critical path, say so. If it adds a post-payment step, describe the drop risk. If it changes a proto message, call out field numbers explicitly. If it depends on a capability that doesn't exist today (e.g., user auth, persistent storage), name that dependency clearly.

4. **Write as a real engineer would.** Complete sentences in prose sections, real code blocks for proto definitions, a real schema if storage is introduced. No placeholder text like `[details TBD]`.

5. **The PRD and Design Doc should be consistent with each other.** The PRD defines what; the Design Doc defines how. They should not contradict.

6. **File naming convention:**
   - PRD: `evals/[short-kebab-name]-prd.md`
   - Design Doc: `evals/[short-kebab-name]-design-doc.md`
   - Example: `evals/order-history-prd.md`, `evals/order-history-design-doc.md`

---END PROMPT---
