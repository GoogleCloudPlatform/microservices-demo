# AI Change Impact Analyzer — Agent Architecture

**Status:** Draft  **Author:** Team 7  **Date:** 2026-05-26

---

## What We Are Building

The AI Change Impact Analyzer takes a proposed software change (PRD + Design Doc) and produces a structured risk assessment report. The report covers seven sections: Change Summary, Change Category, Affected Assets, Dependency Paths, Risk Assessment, Recommended Mitigation Steps, and a Summary with Confidence Level and Approval Recommendation.

This document describes how the system is built in two phases:

- **Phase 1** — A single workflow agent that uses tools to gather context and synthesizes a risk report.
- **Phase 2** — A multi-agent system where specialized agents run in parallel and an orchestrator synthesizes the final report.

---

## Phase 1: Single Workflow Agent

### What It Is

A single LLM instance running in a **ReAct loop** (Reason + Act). The agent reasons about what information it needs, calls tools to get it, observes the results, and repeats until it has enough context to produce the full report.

The LLM does two things that only an LLM should do:
1. Extract structured intent from the Design Doc (what files are changing, what services are involved, what kind of change it is).
2. Synthesize all gathered context into the final risk report.

Everything in between — graph traversal, grepping code, reading files — is done by deterministic tool functions. The LLM decides *which* tools to call and *in what order*, but the tools themselves are plain code, not LLM reasoning.

### System Inputs

| Input | Source |
|---|---|
| PRD | Markdown file |
| Design Doc | Markdown file |
| Dependency graph | `graphify-out/graph.json` |
| Codebase | File system (repo root) |
| Product Handbook | `product_handbook.pdf` |

### Tools Available to the Agent

| Tool | What It Does |
|---|---|
| `extract_from_design_doc(doc)` | Parses the Design Doc, returns named files, service names, change type, and any explicitly stated constraints |
| `traverse_graph(service, hops)` | Looks up nodes in `graph.json` matching the service, traverses edges up to N hops, returns candidate service names |
| `grep_codebase(services, pattern)` | Runs grep on source directories of specified services, returns matched file paths and line numbers |
| `read_file(path)` | Reads a specific source file and returns its contents |
| `read_product_handbook(section)` | Fetches a relevant section from the Product Handbook |

### The ReAct Loop

```
THINK  → what information do I need next?
ACT    → call a tool
OBSERVE → read the result
THINK  → do I have enough context, or do I need more?
... repeat ...
SYNTHESIZE → produce the risk report
```

The agent controls depth. For a narrow config change, it may only call 4 tools. For a proto change affecting 6 services, it may call 12. This adaptability is the main advantage of an agent over a fixed script.

---

## Phase 1 Walkthrough: INR Currency Example

**Input:** `prd_design_docs/low-risk-inr-currency-design-doc.md`

The following traces the exact sequence of tool calls the agent would make.

---

### Step 1 — Extract intent from Design Doc

**Tool call:**
```
extract_from_design_doc("prd_design_docs/low-risk-inr-currency-design-doc.md")
```

**Returns:**
```json
{
  "changed_files": ["src/currencyservice/data/currency_conversion.json"],
  "changed_services": ["currencyservice"],
  "change_type": "data_config",
  "proto_changes": false,
  "new_services": false,
  "constraints": [
    "GetSupportedCurrencies returns Object.keys(currencyData) — no allow-list",
    "Rate loaded once at container startup — no hot reload",
    "No frontend code change required — dropdown is runtime-fetched"
  ]
}
```

**Agent reasoning:** The change is a single JSON file addition. No proto changes. The Design Doc already names the affected file and explains the loading mechanism. I need to know which services call `currencyservice` at runtime.

---

### Step 2 — Find candidate services via graph traversal

**Tool call:**
```
traverse_graph("currencyservice", hops=1)
```

**Returns:**
```json
{
  "candidates": ["frontend", "productcatalogservice", "checkoutservice"],
  "note": "Edges are via genproto stubs — having a stub does not confirm actual runtime calls"
}
```

**Agent reasoning:** Three candidates. The graph edges are from generated protobuf files, not actual call sites. I need to verify which of these actually instantiate a `CurrencyServiceClient`.

---

### Step 3 — Verify actual call sites via grep

**Tool call:**
```
grep_codebase(
  services=["frontend", "productcatalogservice", "checkoutservice"],
  pattern="NewCurrencyServiceClient|currencyService\\.Convert|GetSupportedCurrencies"
)
```

**Returns:**
```
frontend/rpc.go:31      pb.NewCurrencyServiceClient(fe.currencySvcConn).GetSupportedCurrencies(...)
frontend/rpc.go:81      pb.NewCurrencyServiceClient(fe.currencySvcConn).Convert(...)
frontend/handlers.go:84 fe.convertCurrency(r.Context(), p.GetPriceUsd(), currentCurrency(r))
checkoutservice/main.go [match — CurrencyServiceClient instantiated and Convert called]
productcatalogservice/  [no matches outside of genproto/ directory]
```

**Agent reasoning:** `frontend` and `checkoutservice` are confirmed callers. `productcatalogservice` only has the stub in generated code — drop it. I'll read the entry points of `currencyservice`, `frontend`, and `checkoutservice`.

---

### Step 4 — Targeted file reads

**Tool calls (in sequence):**

```
read_file("src/currencyservice/server.js")
```
→ Reveals: `currencyData` loaded via `fs.readFileSync` at startup. No hot-reload. Container restart required for rate changes.

```
read_file("src/frontend/rpc.go")
```
→ Reveals: `GetSupportedCurrencies` is called at runtime to populate the currency dropdown. `Convert` is called on every price render. If `currencyservice` is down, product pages fail.

```
read_file("src/checkoutservice/main.go")
```
→ Reveals: `user_currency` from `PlaceOrderRequest` is passed to `currencyservice.Convert`. INR will work automatically once the key is present. No code change needed.

**Agent reasoning:** I now have everything I need. The change is additive (new JSON key only), proto is unchanged, the loading mechanism is well-understood, and the rollout path is a standard stateless rolling restart. I can produce the full report.

---

### Step 5 — Synthesize the risk report

The agent now holds:
- PRD (goals, requirements, success metrics)
- Design Doc (change description, deployment plan, stated risks)
- Product Handbook (system-level constraints)
- Graph traversal result (blast radius candidates)
- Grep results (confirmed callers, dropped false positives)
- Three source files (loading behavior, call sites, pass-through behavior)

It produces all seven report sections:

| Section | Source of truth |
|---|---|
| Change Summary | PRD + Design Doc |
| Change Category | Design Doc (data/config, additive) |
| Affected Assets | Design Doc + verified grep results |
| Dependency Paths | Graph traversal + grep verification |
| Risk Assessment | File reads (behavioral) + Design Doc (stated risks) |
| Recommended Mitigation Steps | File reads + Product Handbook constraints |
| Summary / Confidence / Approval | Synthesis of all above |

**Sample Risk Assessment output:**

> **Risk Level: Low**
>
> The change adds a single key (`"INR": 89.47`) to `currency_conversion.json`. The `currencyservice` loading logic is fully data-driven — `GetSupportedCurrencies` returns `Object.keys(currencyData)` and `Convert` uses EUR-pivot arithmetic. No source code changes are required in any service.
>
> The confirmed blast radius is `frontend` and `checkoutservice`. Frontend fetches supported currencies at runtime — INR will appear in the dropdown on the next page render after deployment. Checkoutservice passes `user_currency` through without validation — INR will succeed automatically.
>
> The primary rollout risk is the container restart window (~30–60 seconds). During this window, users with INR selected in their session will receive `INVALID_ARGUMENT` errors on price conversion. This is recoverable: selecting any other currency resolves the error immediately.
>
> **Confidence: High** — the affected code is fully read, the blast radius is verified, and the change has no proto or schema implications.
>
> **Approval Recommendation: Approve with standard rollout** — deploy with a rolling update, monitor `currencyservice` error rate for 30 minutes, add INR session-state edge case to the rollback runbook.

---

## Phase 1 → Phase 2: When to Evolve

Start with Phase 1 and observe where it breaks down. The signal to move to multi-agent is one of these:

**Context window pressure.** A high-risk change may require reading 8–10 source files across 6 services. Combined with the Design Doc, PRD, and Product Handbook, this can exceed a single context window. Multi-agent solves this by giving each agent a focused context.

**Independent risk dimensions.** Security/compliance risk (PCI-DSS, GDPR, proto field exposure) and operational risk (rollout failure modes, rollback complexity) are different enough that they benefit from separate focused prompts. A single agent prompt trying to cover both tends to underweight one.

**The single agent makes mistakes on subsets.** In practice, if you observe the agent skipping graph traversal on simple changes, or over-reading on trivial ones, it's a sign the fixed-tool-list approach is hitting its limits and a planner agent would make better decisions.

---

## Phase 2: Multi-Agent System

### Architecture

The multi-agent system has three roles:

**Orchestrator Agent** — Receives the inputs (PRD, Design Doc, graph, codebase, handbook), plans which sub-agents to invoke and with what context, and synthesizes the final report from sub-agent outputs. Does not read code directly.

**Extractor Agent** — Receives the Design Doc + graph. Runs `extract_from_design_doc` and `traverse_graph`. Returns: changed files, change type, candidate services, dependency paths. Runs first and its output feeds both downstream agents.

**Code Analyst Agent** — Receives the candidate services list from Extractor. Runs `grep_codebase` and `read_file` on confirmed callers. Returns: verified affected assets, behavioral observations (error handling, loading patterns, call sites). Runs in parallel with the Risk Context Agent.

**Risk Context Agent** — Receives the PRD + Product Handbook + change type from Extractor. Pulls relevant product constraints, compliance requirements, and success metrics. Returns: applicable constraints, compliance flags, product-level risk signals. Runs in parallel with Code Analyst.

**Risk Assessor Agent** — Receives the outputs of all three upstream agents. Produces the final seven-section report. This is the only agent that sees the full assembled picture.

### Execution Flow

```
Inputs
  └─► Orchestrator
        └─► Extractor Agent  ──────────────────────────────────┐
              ├─► Code Analyst Agent (parallel) ─────────────► Risk Assessor
              └─► Risk Context Agent (parallel) ──────────────►     │
                                                                     ▼
                                                              Risk Report
```

### What Changes From Phase 1

| Concern | Phase 1 | Phase 2 |
|---|---|---|
| Context window | One large context | Each agent has focused context |
| Risk dimensions | Single prompt covers all | Separate agents, better coverage |
| Parallelism | Sequential tool calls | Code Analyst + Risk Context run in parallel |
| Debuggability | Single trace | Per-agent traces, easier to isolate failures |
| Complexity | Lower | Higher — orchestration logic, inter-agent contracts |

### When NOT to Add Multi-Agent

Do not add multi-agent complexity until Phase 1 is producing correct outputs. The eval suite (PRD + Design Doc → expected report) will tell you where Phase 1 fails. Fix the failures in Phase 1 first. Multi-agent is the right fix for *scale and parallelism* problems, not for *reasoning quality* problems — those require better prompts and better tools, not more agents.

---

## Implementation Notes

### Tool Implementation (Phase 1 starting point)

```python
def extract_from_design_doc(doc_path: str) -> dict:
    # Read the file, pass to LLM with structured extraction prompt
    # Return: changed_files, changed_services, change_type, proto_changes, constraints
    ...

def traverse_graph(service: str, hops: int = 1) -> dict:
    # Load graph.json, find nodes matching service name
    # BFS/DFS up to N hops, collect unique source_file values
    # Return: candidate service names + note about edge type
    ...

def grep_codebase(services: list[str], pattern: str) -> dict:
    # For each service, grep src/{service}/ excluding genproto/
    # Return: {service: [matched file paths + line numbers]}
    ...

def read_file(path: str) -> str:
    # Read file, return contents (truncate if > token limit)
    ...
```

### Eval Harness

Each eval case is: inputs (PRD + Design Doc + graph + codebase) → expected output (seven report sections). Run the agent, score the output:

- **Change Category**: exact match
- **Affected Assets**: precision + recall against known ground truth
- **Risk Assessment**: LLM judge with rubric (correct level, grounded reasoning, no hallucinated services)
- **Mitigation Steps**: LLM judge (actionable, references actual files/services from the read step)

The three eval scenarios already in the repo (high/medium/low risk) cover the range. Subscribe & Save is the fourth, highest-complexity case.

---

## File Reference

| File | Role |
|---|---|
| `prd_design_docs/low-risk-inr-currency-design-doc.md` | Walkthrough example (this doc) |
| `prd_design_docs/high-risk-order-history-design-doc.md` | High-risk eval case (proto + new service) |
| `prd_design_docs/medium-risk-category-filter-design-doc.md` | Medium-risk eval case (proto change, 3 callers) |
| `prd_design_docs/subscribe-and-save-design-doc.md` | Complex eval case (new service + payment vault + worker) |
| `graphify-out/graph.json` | Dependency graph (2908 nodes, 3401 edges) |
| `graphify-out/GRAPH_REPORT.md` | Human-readable graph summary |
| `product_handbook.pdf` | System-level constraints and service descriptions |
| `evals/TEAM-PROMPT-generate-prd-and-design-doc.md` | Prompt template for generating new eval scenarios |
