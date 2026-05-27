## Phase 1 Limitations

**Context accumulation is the biggest practical problem.** Every tool call appends to the agent's context — the PRD, Design Doc, graph results, grep output, and every file read all pile up in the same window. For the INR case that's manageable (~30K tokens). For Subscribe & Save — which touches 5+ services, changes proto contracts in 3 places, and introduces a new CronJob — you'd want to read 12-15 source files. At 8000 chars each, that's ~30,000 tokens of source code alone, plus all the intermediate messages. gpt-4o-mini handles 128K tokens but has a known "lost in the middle" problem: details from early tool calls get less attention in synthesis than recent ones. The risk assessment might accurately describe what was in `server.js` (read last) and completely miss a constraint from the design doc (read first).

**The agent can deviate from your workflow.** The system prompt says "follow this order" but you can't programmatically enforce it. On a simple change, the agent might decide to skip `grep_codebase` because the Design Doc says "no other services are affected." That's sometimes right (INR case) and sometimes dangerously wrong (proto changes where the doc underestimates callers). There's no enforcement mechanism in Phase 1 — just a prompt instruction.

**Synthesis confuses sources.** After reading 10 files, when the agent writes the Risk Assessment, it might attribute an observation to the wrong file, conflate two services, or invent a connection it didn't actually verify. This is a known LLM failure mode with long contexts. Your eval rubric should specifically test whether the Affected Assets table references files the agent actually read.

**Grep pattern selection is agent-dependent.** The agent decides what regex to search for. For Go services, `NewCurrencyServiceClient` is right. For a proto change in a Python service, the pattern is completely different (`demo_pb2_grpc.CurrencyServiceStub`). If the agent picks the wrong pattern, it will silently miss real callers and confidently report a lower blast radius than actually exists.

**The graph's limitations are inherited.** As we established: the graph is undirected, misses dynamic file reads, and can't distinguish "has proto stub" from "makes runtime calls." Phase 1 does nothing to overcome these — it just works with what the graph provides and relies on grep to compensate.

**Code complexity the tools can't see:**
- Feature flags and environment variables that change which code path is active at runtime
- Dependency injection patterns — a gRPC client injected via an interface won't show up in a grep for `NewCurrencyServiceClient`
- Event-driven dependencies (Kafka topics, Pub/Sub) that aren't in the static call graph
- Generated proto code that doesn't exist in the repo yet (you can read the `.proto` definition but not how the generated client behaves)

**The biggest gap neither phase solves:** risk factors that live outside the codebase — incident history (this service has been flaky for 3 months), traffic volume (this endpoint handles 50K req/s), test coverage (is this path integration-tested or only unit-tested?), deployment history (last touched 2 years ago, high debt). A senior engineer weighs all of these. The agent has none of them.

---

## Phase 2 Limitations

**The orchestrator is still an LLM.** It decides what context to pass to each sub-agent. If it underspecifies what the Code Analyst should look for, that agent works with incomplete information. The orchestrator's errors propagate silently — there's no way for a sub-agent to say "I think I was given incomplete context."

**Splitting context means losing cross-cutting signals.** The Code Analyst sees the source code. The Risk Context Agent sees the PRD and handbook. But a compliance risk (say, GDPR deletion requirements visible in the code via a comment) might only be caught if the same agent sees both the code and the handbook section on data retention. By design, no single Phase 2 agent has both. The Risk Assessor gets summaries from each, but the nuance gets lost in translation.

**Inter-agent output is hard to make reliable.** Agent A produces a finding. Agent B must correctly parse and reason about it. If Agent A says "productcatalogservice is a confirmed caller" incorrectly, Agent B (Risk Assessor) will build on that wrong premise — and you have no automatic check between them.

**Debugging is harder, not easier.** With Phase 1 you have one LangGraph trace. With Phase 2 you have 4 traces (Orchestrator, Extractor, Code Analyst, Risk Assessor). When the final report is wrong, which agent failed? The orchestrator passing wrong context? The Code Analyst missing a caller? The Risk Assessor misjudging? Isolating the failure requires reading all four traces.

**Parallelism adds coordination complexity.** If Code Analyst and Risk Context Agent run in parallel, the Risk Assessor can't start until both finish. You need to handle partial failures — what if Code Analyst times out? Does the Risk Assessor wait, skip, or report with incomplete input? Phase 1 sidesteps this because there's only one agent.

---

## What Actually Helps

The honest answer is neither phase fully solves the hard problem. They both do structural risk assessment well and behavioral risk assessment partially. What would genuinely improve output quality, regardless of phase:

**Richer input signals.** If your system could consume a test coverage report, a service-level error rate dashboard, or even git blame (last modified X months ago, by Y people), risk inference becomes much more grounded.

**Constrained tool outputs.** Instead of returning raw file contents, tools that return *structured* observations ("this file loads data at startup: yes/no", "this service has a circuit breaker: yes/no") would give the LLM less to misinterpret. You're trading flexibility for reliability.

**Eval-driven prompt tuning.** The Phase 1 failures you'll find by running the high-risk order history scenario (new service, proto change, auth dependency) will tell you exactly where the prompt needs to be stronger. Build Phase 2 only after you've exhausted what better prompts and better tools can do for Phase 1.