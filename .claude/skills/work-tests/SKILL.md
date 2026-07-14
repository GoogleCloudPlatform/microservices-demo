---
name: work-tests
description: Step 2 of the work pipeline (research → tests → plan → execute → docs). From docs/work/NNN-<slug>/1-research.md, produces docs/work/NNN-<slug>/2-tests.md — the behaviour spec as Given-When-Then scenarios (happy path + edge/negative), each with a stable test ID, plus what is in/out of scope to test and the seams. No production code, no plan. Authored by a subagent, reviewed by a different subagent. Use this as step 2, after 1-research.md exists, to produce the Given-When-Then behaviour spec (before plan/execute).
allowed-tools: Read, Glob, Grep, Bash(ls *), Bash(find *), Bash(git *), Agent, Task, TaskCreate, TaskUpdate, TaskList
disallowed-tools: Write, Edit, WebSearch, WebFetch
---

# work-tests — Step 2: behaviour spec

Second step of the spec-driven pipeline: research (`work-research`) → **tests** → plan
(`work-plan`) → execute (`work-execute`) → docs (`work-docs`). From `1-research.md`, produces
`docs/work/NNN-<slug>/2-tests.md` and nothing else. No production code, no plan.

## Keep in front of mind (every decision)
- **Think Before Coding** — pin down observable behaviour before any plan or code.
- **Simplicity First** — the smallest set of scenarios that pins the behaviour.
- **Surgical Changes** — test the slice from `1-research.md`, not the whole system.
- **Goal-Driven Execution** — each scenario states the behaviour that proves done.
- Apply **KISS · YAGNI · SRP · DRY** — no redundant scenarios, no speculative coverage.

## Core rules
- **Track steps in the TODO tool.** Use the task/todo list (`TaskCreate`/`TaskUpdate`) to track
  the author→review→revise steps; one `in_progress` at a time, `completed` when done.
- **Orchestrator writes nothing.** The **author subagent** has `Write` and creates `2-tests.md`.
  A **different** reviewer subagent validates it. Author ≠ reviewer.
- **Behaviour, not implementation.** Tests are **Given-When-Then** scenarios covering the **happy
  path AND edge/negative cases**. Test only what is **observable and meaningful** — not framework
  code, not trivial getters.
- **Every scenario must be executable.** A scenario only counts if it can be turned into a test that
  actually **runs** (`work-execute` executes it, in a container if the local toolchain is missing).
  Don't pin behaviour on an API, function, or flag whose existence you haven't confirmed in the
  pinned dependency — an assertion against something that doesn't exist isn't a spec, it's a future
  compile error. When a scenario depends on an unverified API, flag it as an open question for
  research rather than asserting it.
- **Avoid mocks unless genuinely needed.** Prefer real/in-memory objects and the integration-style
  seam your stack offers; mock only true external seams (a database, outbound HTTP, a third-party
  API) and only when a real substitute isn't practical. Name those seams explicitly.
- **Stable test IDs.** Each scenario gets a stable ID (e.g. `T-001`, `T-002`) that `work-plan`
  maps tasks to and `work-execute` implements against. IDs never get reused.
- **Spec only.** No production code, no implementation plan (that's `work-plan`).
- **Model tier.** Dispatch every subagent (author, reviewer) at the tier recorded as `Task tier` in
  `1-research.md` — pass **`model: sonnet`** for a **lightweight** unit, otherwise **Opus** (omit the
  param to inherit the always-Opus orchestrator). The tier changes only the worker model, never this
  step's procedure.
- All docs in **English**.

## Procedure
1. **Read inputs.** Read `docs/work/NNN-<slug>/1-research.md` and the touched source/test areas.
   Reuse the same `NNN-<slug>` chosen in Step 1.
2. **Author subagent** writes `docs/work/NNN-<slug>/2-tests.md` containing:
   - **In/out of scope to test** — what behaviour this spec covers and explicitly excludes.
   - **Seams** — the boundaries under test and where (if anywhere) a substitute is used.
   - **Scenarios** — each as **Given / When / Then**, with a stable **test ID**, marked
     happy-path or edge/negative. Cover meaningful edge and negative cases.
3. **Independent reviewer subagent** checks: every scenario is observable and meaningful, happy +
   edge/negative covered, IDs stable/unique, no implementation detail leaking, no gratuitous
   mocks, scope matches `1-research.md`. Loop author→reviewer until it passes.
4. **Commit the artifact.** Once the reviewer passes, the orchestrator makes **one atomic
   `docs(work): behaviour spec NNN <slug> …` commit** of `2-tests.md` on the **unit's branch** per
   `docs/commit-conventions.md` — **before** handing off. Stage by path
   (`git add docs/work/NNN-<slug>/2-tests.md`), never `git commit -a`. Later human-feedback fixes
   to this artifact may **exceptionally** be folded into that commit with `git commit --amend`
   (instead of a new commit), as long as nothing has been built on top yet.
5. **Hand off** to `work-plan` (Step 3), which consumes `1-research.md` + `2-tests.md`.
