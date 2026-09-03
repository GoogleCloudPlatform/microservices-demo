---
name: work-research
description: Step 1 of the work pipeline (research → tests → plan → execute → docs). Produces docs/work/NNN-<slug>/1-research.md — scope, the slice of the system touched, stack/seams, unknowns, and cited findings. Any internet research is delegated to a fresh clean research subagent. Writes research only — no tests, no code, no plan. Use this as step 1 when starting a new unit of non-trivial work under docs/work/NNN-<slug>/ (before tests/plan/execute).
allowed-tools: Read, Glob, Grep, Bash(ls *), Bash(find *), Bash(git *), Agent, Task, TaskCreate, TaskUpdate, TaskList
disallowed-tools: Write, Edit, WebSearch, WebFetch
---

# work-research — Step 1: research a unit of work

First step of the spec-driven pipeline: **research → tests (`work-tests`) → plan
(`work-plan`) → execute (`work-execute`) → docs (`work-docs`)**. Produces
`docs/work/NNN-<slug>/1-research.md` and nothing else. No tests, no plan, no production code.

## Keep in front of mind (every decision)
- **Think Before Coding** — understand the slice before anyone writes anything.
- **Simplicity First** — research only what this unit of work touches.
- **Surgical Changes** — name the seams; don't redesign the system.
- **Goal-Driven Execution** — the goal is a clear, cited, scoped research note.
- Apply **KISS · YAGNI · SRP · DRY** to scope: research the smallest coherent slice.

## Core rules
- **Track steps in the TODO tool.** Use the task/todo list (`TaskCreate`/`TaskUpdate`) to track
  the author→review→revise steps; one `in_progress` at a time, `completed` when done.
- **Orchestrator writes nothing.** The main session plans and verifies. The **author subagent**
  it spawns has `Write` and creates `1-research.md`. A **different** reviewer subagent validates
  it. Author ≠ reviewer.
- **Internet research is ALWAYS delegated to a fresh, clean research subagent** — the orchestrator
  never browses in the main thread. Every external claim must cite its source (URL + what it
  establishes). For library/framework API details, prefer a docs MCP (e.g. a `context7`-style
  server) over open-web guessing.
- **Research only.** No Given-When-Then scenarios (that's `work-tests`), no plan (that's
  `work-plan`), no code.
- All docs in **English**.

## Procedure
1. **Scope, number & branch.** Confirm the unit of work with the user in one line. Allocate the next
   `NNN`: list `docs/work/`, take the highest existing number + 1, zero-padded to 3 digits
   (e.g. `001`, `002`). Choose a short kebab-case `slug`. The dir is `docs/work/NNN-<slug>/`. Then,
   from a clean `main`, **create the unit's branch** `work/NNN-<slug>` (or the repo's own naming
   convention) and switch to it — **every commit for this unit lands on that branch**, never on
   `main`. The unit ends with a squash PR to `main` (see `docs/commit-conventions.md`).
2. **Gather local context.** Read the touched source and test areas, `CLAUDE.md`, and relevant
   `docs/`. Identify the stack slice and the **seams** involved (DB, outbound HTTP, third-party
   APIs, queues — wherever your code meets something it doesn't own). In a multi-service / monorepo,
   name the exact service(s) and language(s) in scope.
3. **Delegate external research (if any).** Spawn a **fresh clean research subagent** with a
   focused question. It returns cited findings; it writes no project files.
4. **Author subagent** writes `docs/work/NNN-<slug>/1-research.md` containing:
   - **Scope** — what this unit of work is and is not.
   - **System slice** — the components/files/seams touched.
   - **Stack & seams** — relevant tech and where the boundaries are.
   - **Unknowns / open questions** — what's still uncertain.
   - **Findings & sources** — cited external research from the research subagent.
   - **Task tier** — end the file with a `Task tier: <lightweight|standard> — <one-line reason>`
     line. **lightweight** = roughly ≤ ~2 files, one service, no new seam/dependency, pinnable with
     1–2 tests, low risk, no config/build-tooling change; **standard** = a feature, cross-cutting /
     multi-service change, a new seam/dependency, anything risky, or a config/build-tooling change.
     **When unsure → standard.** This sets the *model* the later phases' subagents run on (Sonnet vs
     Opus) — it does **not** change the flow. The orchestrator confirms or overrides it at the
     research checkpoint.
5. **Independent reviewer subagent** checks: scope is tight, seams named, no tests/plan/code
   leaked in, every external claim cited, the **Task tier** line is present and its classification
   matches the researched scope. Loop author→reviewer until it passes.
6. **Commit the artifact.** Once the reviewer passes, the orchestrator makes **one atomic
   `docs(work): research NNN <slug> …` commit** of `1-research.md` on the **unit's branch** per
   `docs/commit-conventions.md` — **before** handing off. Stage by path
   (`git add docs/work/NNN-<slug>/1-research.md`), never `git commit -a`. Later human-feedback
   fixes to this artifact may **exceptionally** be folded into that commit with
   `git commit --amend` (instead of a new commit), as long as nothing has been built on top yet.
7. **Hand off** to `work-tests` (Step 2), which consumes `1-research.md`.
