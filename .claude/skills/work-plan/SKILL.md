---
name: work-plan
description: Generate the spec-driven IMPLEMENTATION PLAN docs/work/NNN-<slug>/3-plan.md from the existing 1-research.md and 2-tests.md. A KISS/DRY/YAGNI/SRP plan of small atomic commits, test-first — seams → red tests (all up front) → implementation (red→green) → consolidation → mandatory live e2e smoke — with tasks grouped into BATCHES (one coder dispatch each, still one atomic commit per task) so execute spawns few subagents, ending in a batched TODO commit checklist that work-execute consumes. Writes the plan only, never code. Step 3 of the work pipeline (research → tests → plan → execute → docs). Use this as step 3, after 1-research.md and 2-tests.md exist, to produce 3-plan.md (before execute).
allowed-tools: Read, Glob, Grep, Bash(ls *), Bash(find *), Bash(git *), Agent, Task, TaskCreate, TaskUpdate, TaskList
disallowed-tools: Write, Edit
---

# work-plan — Step 3: implementation plan

Third step of the spec-driven pipeline: research (`work-research`) → tests (`work-tests`) →
**plan** → execute (`work-execute`) → docs (`work-docs`). From `1-research.md` + `2-tests.md`,
produces `docs/work/NNN-<slug>/3-plan.md` and nothing else. Writes the plan, never code.

## Keep in front of mind (every decision)
- **Think Before Coding** — the plan is where thinking happens; code is mechanical after.
- **Simplicity First** — the fewest, smallest commits that satisfy the tests.
- **Surgical Changes** — each task touches only the files it must.
- **Goal-Driven Execution** — every task maps to a test ID / acceptance criterion.
- Apply **KISS · YAGNI · SRP · DRY** to every task: minimum scope, one reason to change.

## Core rules
- **Track steps in the TODO tool.** Use the task/todo list (`TaskCreate`/`TaskUpdate`) to track
  the author→review→revise steps; one `in_progress` at a time, `completed` when done.
- **KISS/DRY/YAGNI/SRP minimum.** No task does more than one acceptance criterion needs.
- **Test-first, phased** per `format.md` (alongside this SKILL.md, in this skill's own directory):
  baseline → seams (serial, compile-safe) → red tests (all up front in one batch) →
  implementation (red→green, batched by area) → consolidation/coverage → **mandatory live e2e
  smoke**.
- **Small atomic commits.** Each task = **one commit = one acceptance criterion**, green at its
  batch boundary (not necessarily buildable in isolation — see `docs/commit-conventions.md`). No task
  leaves the tree red at its boundary (red tests are introduced in their own commits that are
  expected-red by design and flagged as such).
- **Batch to spend few subagents.** Group tasks into **batches** (`batch:` field) — a batch is
  **one `coder` dispatch**, the tasks under it implemented back-to-back with warm context, yet the
  orchestrator still makes **one atomic commit per task**. Default batches: all seams (1), all red
  tests (1, "tests up front"), implementation by feature area (1 each), consolidation (1). Aim for
  ~4–7 dispatches per unit, not one-per-task. See `format.md` → *Batching*.
- **Always end with e2e.** The last phase is a live **`e2e-tester`** smoke against the real
  running system (its own batch) **whenever the unit changes user-observable behaviour**;
  otherwise the plan states an explicit `e2e: n/a — <reason>`. Never silently omit it.
- **Mark parallelism.** Each task is `serial` or in a named `parallel group`. **Parallel tasks
  must not edit shared files** — that is how `work-execute` fans out safely. Prefer a single
  serial batch (fewer subagents) over a parallel group unless concurrency truly pays.
- **Config / build-tooling tasks are HIGH-RISK.** Flag them `[high-risk]`, isolate them in their
  own task with a **build acceptance criterion** (the build green). Never mix them with feature
  work.
- **No setup tasks outside the work.** Don't plan unrelated cleanup or speculative scaffolding.
- **Fixed commit convention.** Reference `docs/commit-conventions.md`. Every commit is atomic and
  lands on the **unit's branch** (`work/NNN-<slug>`), **never directly on `main`** — the unit ends
  with a squash PR to `main` (team-reviewed, merged manually). The plan must not contain any step that
  commits to `main` or merges the PR.
- **All work runs in subagents; author ≠ reviewer.**
- **Model tier.** Dispatch every subagent (author, reviewer) at the tier recorded as `Task tier` in
  `1-research.md` — pass **`model: sonnet`** for a **lightweight** unit, otherwise **Opus** (omit the
  param to inherit the always-Opus orchestrator). The tier changes only the worker model, never this
  step's procedure.
- All docs in **English**.

## Who writes what (this is NOT a contradiction)
This SKILL's frontmatter sets `disallowed-tools: Write, Edit` because the **MAIN / orchestrator
session writes nothing** — it only reads, coordinates, and verifies. The **author subagent** the
orchestrator spawns **does** have `Write` and is the one that actually creates `3-plan.md`. The
reviewer subagent reads it. So: orchestrator = no Write; author subagent = Write; reviewer
subagent = read-only.

## Procedure
1. **Scope / read inputs.** Read `docs/work/NNN-<slug>/1-research.md` and `2-tests.md` and the
   touched source/test areas. Reuse the same `NNN-<slug>`.
2. **Author subagent** writes `docs/work/NNN-<slug>/3-plan.md` **exactly** per
   `format.md` (alongside this SKILL.md, in this skill's own directory) (phases, per-task fields, final TODO checklist).
3. **Independent reviewer subagent** (different from the author) validates the plan against every
   item in `checklist.md` (in this skill's own directory).
4. **Loop** author→reviewer until the reviewer passes with no open items.
5. **Commit the artifact.** Once the reviewer passes with no open items, the orchestrator makes
   **one atomic `docs(work): implementation plan NNN <slug> …` commit** of `3-plan.md` on the
   **unit's branch** per `docs/commit-conventions.md` — **before** handing off. Stage by path
   (`git add docs/work/NNN-<slug>/3-plan.md`), never `git commit -a`. Later human-feedback fixes
   to the plan may **exceptionally** be folded into that commit with `git commit --amend` (instead
   of a new commit), as long as `work-execute` has not started consuming it yet.
6. **Hand off** to `work-execute` (Step 4), which walks the final TODO checklist.
