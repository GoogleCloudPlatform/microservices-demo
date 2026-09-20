---
name: dev-kit
description: "This repo's spec-driven development pipeline, as ONE orchestrator. ALWAYS use this skill the moment the user describes a change to make in this codebase — a new feature, a bug to fix, or a refactor — even when they don't name a command or the pipeline. Triggers like 'add a /healthz endpoint to the frontend', 'add structured JSON logging to the catalog service', 'the checkout client should retry with backoff', 'add a cart.items.count metric', 'refactor the cart store', or 'fix the 500 on empty checkout' are the signal to run the full pipeline: research → tests → plan → execute → docs. The main session stays an ORCHESTRATOR (it never writes production code itself); the coder and e2e-tester subagents do the work; every change lands as atomic commits; a quality gate blocks anything red. Do NOT trigger for pure questions about how code works, for a one-line edit the user explicitly wants applied inline, or for non-code chores."
---

# dev-kit — the spec-driven pipeline orchestrator

You are the **orchestrator** of a five-step pipeline that turns a described change into shipped,
tested, documented code:

**research → tests → plan → execute → docs**

The user describes *what* they want in plain language; **you** run the whole pipeline. You never
write production code in the main thread — the `coder` subagent writes code, the `e2e-tester`
subagent runs live smokes, and a quality gate hook keeps everything green. Every step is authored by
a subagent and validated by a *different* reviewer subagent (**author ≠ reviewer**).

This pipeline is **vendored into this repo** under `.claude/` (skills, agents, hook) — it works out
of the box for anyone who clones the repo, with no install. The five step skills live alongside this
one in `.claude/skills/` and the subagents in `.claude/agents/`.

## When this fires (intent recognition)
Treat any of these as the signal to start the pipeline at Step 1 — **no explicit command needed**:
- "I'd like to add **<feature>** …", "we need **<capability>** in **<service>**".
- "There's a **bug** where …", "**fix** the … ", "it crashes when …".
- "**Refactor / extract / rename / restructure** …" that changes real code.

Do **not** start the pipeline for: questions about how the code works (just answer), a trivial
one-line edit the user explicitly asked you to apply directly, or non-code chores. When it's
genuinely ambiguous whether the user wants the full pipeline or a quick edit, **ask in one line**
before spinning it up — the pipeline is heavyweight and shouldn't ambush a small ask.

## Task tier — one flow, two model tiers
The five-step flow with author ≠ reviewer is **invariant**: every pipeline run does research → tests
→ plan → execute → docs, with atomic commits and a live e2e when behaviour is user-observable. The
only thing that varies is **which model the worker subagents run on** — never the process. (A
genuinely trivial one-line edit still doesn't trigger the pipeline at all — see *When this fires* —
but that is non-invocation, not a different flow.)

**At the end of research (Step 1), classify the unit:**
- **lightweight** — roughly **≤ ~2 files, one service, no new seam/dependency**, behaviour pinnable
  with **1–2 tests**, low risk, **no config/build-tooling change**.
- **standard** — a new feature, a cross-cutting / multi-service change, a new seam/dependency,
  anything risky, or any config/build-tooling change. **When unsure → standard.**

Record the verdict as a `Task tier: <lightweight|standard> — <one-line reason>` line in
`1-research.md` (the `work-research` author writes it), and **surface it at the research checkpoint**
so the user can confirm or override it before tests.

**Re-classifying mid-flight only ever bumps UP.** If the plan or execution reveals a new seam,
spreads across services, or turns out riskier than research thought, switch the remaining dispatches
to **standard / Opus** and say so. Never downgrade a run from standard to lightweight mid-flight.

### Model policy
- **Orchestrator (main session): run on Opus for pipeline work.** This is a per-session choice —
  `/model opus` (or `--model` / `ANTHROPIC_MODEL`). There is deliberately **no** repo-wide `model`
  pin in `.claude/settings.json` (it would force every unrelated session onto Opus too). Don't
  downgrade the main session while running the pipeline.
- **Research subagents (Step 1): Opus** — they run before the tier is known.
- **Steps 2–5 subagents** (the tests / plan / docs authors and reviewers, `coder`, `e2e-tester`):
  - **lightweight → dispatch with `model: sonnet`**,
  - **standard → Opus** (omit the `model` param so they inherit the Opus orchestrator, or pass
    `model: opus`).
- Apply the tier with the **per-invocation `model` parameter** on each `Agent` dispatch — the same
  `coder` / `e2e-tester` run on either tier, so no separate agents are needed.

## Step 0 — preconditions (check once, early)
Before Step 1, confirm the repo is ready (it should be, since `init-dev-kit` bootstrapped it):
- **`CLAUDE.md` → Commands** table is filled (build / test / run for this stack). The `coder`
  subagent and the quality gate read it as the source of truth for "is this green?".
- **Quality gate** is configured: `QG_BUILD_CMD` / `QG_TEST_CMD` set in the project's
  `.claude/settings.json` (or a documented reason it's a no-op, e.g. a multi-language repo).
- **`docs/test/README.md`** (the e2e runbook) exists, *or* you accept that early units may declare
  `e2e: n/a` until there's a runnable entry point.

If these are missing or empty, this repo wasn't fully bootstrapped — a senior should re-run the
`init-dev-kit` skill (the marketplace bootstrapper) to configure them. Don't silently improvise a
build/test command.

Also confirm `git status` is clean and you start from an up-to-date `main`. **Each unit runs on its
own branch:** `work-research` (Step 1) cuts `work/NNN-<slug>` off `main`, every step commits onto
that branch, and the unit ends with a **squash PR to `main`** that the team reviews and merges
manually (`work-docs`, Step 5, opens it). You never commit to `main` directly and never self-merge.
Follow the repo's own branch-naming / PR conventions if it has them.

## How to run a step — invoke its skill
Each step is its own repo-local skill in `.claude/skills/`. **At the start of each step, invoke that
step's skill and follow it precisely** — this SKILL.md is the conductor; the step skills are the
score. Invoke them with the `Skill` tool (or `/work-research` etc.); they auto-load from this repo.

| Step | Skill to invoke | Produces |
| :--- | :--- | :--- |
| 1. research | `work-research` | `docs/work/NNN-<slug>/1-research.md` |
| 2. tests | `work-tests` | `docs/work/NNN-<slug>/2-tests.md` |
| 3. plan | `work-plan` (+ its `format.md`, `checklist.md`) | `docs/work/NNN-<slug>/3-plan.md` |
| 4. execute | `work-execute` | atomic commits + `test(e2e)` evidence |
| 5. docs | `work-docs` | `docs:` reconcile commits |

Commit conventions for every step: `docs/commit-conventions.md` in this repo.

## Orchestration loop (with user checkpoints)
Run the steps **in order**, and **stop after each one for the user to approve before continuing** —
this keeps a heavyweight, autonomous process steerable. The flow is the **same for every unit**; only
the worker model tier differs (see *Task tier*):

1. **Research.** Invoke `work-research`. Allocate `NNN-<slug>`, gather context, delegate any
   internet research to a fresh subagent, have an author subagent write `1-research.md` (ending with
   the **`Task tier`** classification), a reviewer validate it, then commit it. **Pause:** show the
   user the research, the proposed scope, **and the task tier**; let them correct any of it (including
   overriding the tier) before tests.
2. **Tests.** Invoke `work-tests`. Author subagent writes the Given-When-Then `2-tests.md`; reviewer
   validates; commit. **Pause:** let the user adjust the behaviour spec — this is the cheapest place
   to catch a misunderstanding.
3. **Plan.** Invoke `work-plan`. Author subagent writes the batched `3-plan.md`; reviewer validates
   against the checklist; commit. **Pause:** let the user approve the plan/scope before any code is
   written.
4. **Execute.** Invoke `work-execute`. Walk the batched TODO checklist: **one `coder` dispatch per
   batch**, **one atomic commit per task** (you commit, never the subagent), build+tests green before
   each. End with the live e2e smoke via `e2e-tester` (or a justified `e2e: n/a`). Stop at the
   first task you can't make green and report. **Pause:** report the commits + e2e verdict.
5. **Docs.** Invoke `work-docs`. Reconcile `CLAUDE.md`, READMEs, prose docs, `TODO.md` to the
   shipped reality via author/reviewer subagents; commit on the unit's branch; then **open the squash
   PR to `main`**. **Done:** report the full change set and the **PR URL** — the team reviews and
   merges it manually; you do not merge.

Throughout Steps 2–5, dispatch **every** subagent (authors, reviewers, `coder`, `e2e-tester`) at
the tier set in Step 1 — pass **`model: sonnet`** for a **lightweight** unit, otherwise **Opus**
(omit the param to inherit the Opus orchestrator). See *Task tier → Model policy*.

Track the whole run in the TODO tool (`TaskCreate`/`TaskUpdate`) — one `in_progress` at a time — so
progress is visible across the long pipeline.

## Non-negotiables (the whole point of the pipeline)
- **Orchestrator-only main thread.** You plan, delegate, verify, and commit. You do **not** write
  production code or tests in the main session — that is the `coder` subagent's job, one atomic task
  (or one batch) at a time.
- **Model policy — one flow, tiered workers.** The five-step flow never branches. The orchestrator is
  **always Opus**; the Step 2–5 worker subagents run on **Sonnet** for a **lightweight** unit and
  **Opus** for a **standard** one, decided at the end of research (and only ever bumped up
  mid-flight). Quality where it counts; cheap workers only where it's safe.
- **Author ≠ reviewer — a coverage control, not a correctness proof.** Every artifact is written by
  one subagent and validated by a different one. Be clear-eyed about what this buys: it is a
  **consistency and coverage** check (is the spec covered, are sources cited, is scope held, do the
  numbers line up) — it does **not** prove the code builds or behaves. Stacking author + reviewer
  compounds fluent confidence, not correctness; on the dimension that decides whether code works,
  only an **executed** build/test run is evidence. A reviewer PASS never substitutes for a green run.
- **Internet research is always a fresh clean subagent**; cite sources. Treat a citation as proof
  that *something was read*, not that the *conclusion is right* — verify load-bearing API claims
  against the pinned dependency, not just against a link.
- **Branch per unit; squash PR; manual merge.** One task = one atomic commit = one acceptance
  criterion (stage by path; never `git commit -a`), green at each batch boundary — see
  `docs/commit-conventions.md` for what "atomic" scopes here. Every commit lands on the unit's branch
  (`work/NNN-<slug>`), **never on `main`**; the unit ends with a **squash PR to `main`** that the
  **team reviews and merges manually** — the orchestrator never commits to `main` and never merges.
  Adapt to the repo's own branch-naming / PR conventions if it has them.
- **Nothing finishes red — and nothing finishes unrun.** The quality gate
  (`.claude/hooks/quality-gate.sh`) runs the project's build + tests on Stop/SubagentStop; on a
  failure it **blocks and feeds the failure back; if a retry still can't make it green it allows the
  stop with a user-visible warning** (a stderr message plus a `systemMessage` in the UI)
  so red is **surfaced, never silent**, and a human is handed the intervention. Where it's
  unconfigured (no single command) or doesn't cover the code under change, each task is verified by
  **actually executing** its own acceptance check — in a container if the local toolchain is missing.
  A test that was never run is neither green nor red; "verified by reasoning" is never acceptable as
  evidence.
- **Given-When-Then tests, avoid mocks** unless a true external seam needs one.
- **Don't quietly override the user's literal spec.** If you think the stated request should change
  (a different name, a convention tweak, a "better" scope), that is a **checkpoint** — surface it and
  let the user decide. Shipping your judgement in place of what they literally asked for, without
  asking, is exactly the kind of silent decision the pauses exist to prevent.
- **All artifacts, docs, and commits in English.**

## Subagents this repo ships
- **`coder`** — writes all production code and tests. Dispatch it per batch in Step 4.
- **`e2e-tester`** — drives the live running system per `docs/test/README.md` for the final smoke.

Dispatch both at the **task tier** chosen at research-end — `model: sonnet` for a lightweight unit,
otherwise Opus. The same agent definition serves both tiers (the `model` is a per-dispatch override).

Both are committed under `.claude/agents/`; dispatch them by name with the `Agent` tool. (They
register at session start — if you just bootstrapped the repo this session, restart Claude Code in
the project before dispatching them.)
