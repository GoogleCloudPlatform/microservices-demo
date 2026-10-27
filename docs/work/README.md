# Spec-driven development pipeline

Non-trivial work flows through a five-step, model-invocable pipeline. The top-level **`dev-kit`**
orchestrator skill fires on intent (you describe a feature/bugfix/refactor in plain language) and
runs the same five steps in order every time — the flow is invariant; a task tier
(lightweight | standard) chosen at the end of research sets only the worker-subagent model (Sonnet vs
Opus), not the process. Each step's skill auto-loads when its turn comes (you can also invoke it
explicitly with `/work-research` etc.). Each step is a project skill
under `.claude/skills/`, each is orchestrator-driven (the main session coordinates and verifies;
**subagents** do the authoring/coding), and each is validated by an **independent reviewer subagent**
before the next step begins. The main session is an **orchestrator only** — it never
writes production code; all coding goes to the [`coder`](../../.claude/agents/coder.md) subagent, one
small atomic task at a time. Each unit runs on its **own branch** (`work/NNN-<slug>`) off `main`;
every commit is **atomic** (one acceptance criterion, green at the batch boundary — see
`docs/commit-conventions.md`) and lands on that branch, and the unit ends with a **squash PR to
`main`** that the team reviews and merges manually.

## The five steps (run in order)

1. **`work-research`** → `docs/work/NNN-<slug>/1-research.md`
   Scope, the slice of the system touched, stack/seams, and unknowns. Any internet research is
   delegated to a **fresh clean research subagent** (cited sources). Research only — no tests, no
   plan, no code. Allocates the `NNN` number and the `slug`.

2. **`work-tests`** → `docs/work/NNN-<slug>/2-tests.md`
   The behaviour spec as **Given-When-Then** scenarios (happy path + edge/negative), each with a
   stable test ID, plus in/out-of-scope and the seams. No code, no plan.

3. **`work-plan`** → `docs/work/NNN-<slug>/3-plan.md`
   An ordered plan of **small atomic commits**, test-first and phased (baseline → seams → red tests
   **(all up front)** → implementation red→green → consolidation/coverage → **mandatory live e2e
   smoke**), ending in a **TODO commit checklist**. Each task = one commit = one acceptance
   criterion, mapped to test IDs, marked `serial` or `parallel group`, with config/build-tooling
   tasks isolated as `[high-risk]`. Tasks are grouped into **batches** (`### Batch` headers): a batch
   is **one `coder` dispatch** yet **still one atomic commit per task** — so execute spawns **few**
   subagents (~4–7 per unit) without coarsening the commit history. The plan **always ends with a
   live e2e task** (the `e2e-tester` subagent), unless the unit ships no user-observable change, in
   which case it states an explicit `e2e: n/a — <reason>`.

4. **`work-execute`** → commits on the unit's branch
   Walks the batched TODO checklist. For each **batch** the orchestrator dispatches **one** `coder`
   subagent with all the batch's tasks (a `parallel group` instead fans out one subagent per
   disjoint-file task), then makes **one atomic commit per task** on the unit's branch (red→green, avoid mocks;
   build + tests green before each) per [commit conventions](../commit-conventions.md). The final
   batch runs the **live e2e smoke** via the `e2e-tester` subagent (evidence into
   `docs/test/NNN-<slug>/`, a PASS `summary.md` is the acceptance) and commits it as `test(e2e): …` —
   or is skipped on a justified `e2e: n/a`. Stops at the first task it can't make green and reports.

5. **`work-docs`** → `docs` commits on the unit's branch, then the squash PR to `main`
   After the unit's code is committed, reconciles **all documentation outside the `NNN-<slug>/`
   artifacts** so it matches the shipped reality: `CLAUDE.md`, the prose docs under `docs/`, every
   touched `README.md`, this `docs/work/README.md` (only if the pipeline itself changed), and
   `TODO.md` (fully-shipped items condensed to a historical `- [x] … — <commit>` checklist; open
   items stay `- [ ]`). Subagents author one surface each (disjoint files), an independent reviewer
   validates every claim against the code, the orchestrator makes atomic `docs:` commits. Never edits
   the `NNN-<slug>` artifacts and never writes code — if the docs are wrong only because the *code*
   is wrong, it stops and reports a new unit. Finally it **opens the squash PR to `main`** for the
   team to review and merge manually.

## Layout

```
docs/work/
  README.md                ← this file
  NNN-<slug>/              ← one directory per unit of work (NNN zero-padded: 001, 002, …)
    1-research.md          ← Step 1 (work-research)
    2-tests.md             ← Step 2 (work-tests)
    3-plan.md              ← Step 3 (work-plan)
docs/test/
  NNN-<slug>/              ← Step 4 e2e evidence: ordered screenshots/outputs + summary.md
  README.md                ← the live-smoke runbook the e2e-tester follows
```

Steps 4 (`work-execute`) and 5 (`work-docs`) add **no per-unit plan file** — they produce commits on
the unit's branch (`work/NNN-<slug>`): feature/test commits + e2e evidence from execute, then `docs:`
commits from docs. The unit reaches `main` only via the squash PR. `work-docs` is also the only step
that may edit this `README.md`, and only when the pipeline itself changes.

## Conventions reflected in every step
- **Orchestrator-only main thread.** Plans, delegates, verifies, commits — never writes code.
- **Author ≠ reviewer.** Every step is authored by one subagent and validated by a different,
  independent reviewer subagent; loop until it passes.
- **Internet research is always a fresh clean subagent**; cite sources.
- **Principles in front of mind:** Think Before Coding · Simplicity First · Surgical Changes ·
  Goal-Driven Execution — applying **KISS · YAGNI · SRP · DRY** to every decision.
- **Tests are Given-When-Then**, covering edge/negative cases; test only what is observable and
  meaningful; avoid mocks unless a true external seam needs one.
- **Quality gate:** a Stop/SubagentStop hook runs the project's build + tests; nothing finishes red.
  It only sees what it is configured to build, so it no-ops on out-of-scope (e.g. script/infra-only)
  units — those are verified by their own acceptance check, not the gate.
- **Branch per unit, atomic commits, squash PR to `main` (team-reviewed, manual merge).** See
  [commit conventions](../commit-conventions.md).
- **All docs in English.**
