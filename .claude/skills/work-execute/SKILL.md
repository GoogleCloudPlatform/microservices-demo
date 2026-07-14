---
name: work-execute
description: "Step 4 of the work pipeline (research → tests → plan → execute → docs). Walks the BATCHED TODO commit checklist in docs/work/NNN-<slug>/3-plan.md. For each batch (one coder dispatch — all the batch's tasks in a single invocation, warm context) it still makes ONE atomic commit per task (red→green, Given-When-Then, avoid mocks), verifying the build + tests green before each commit; then ends with the MANDATORY final e2e batch — dispatching the e2e-tester subagent against the live system and committing the evidence (or skipping on a justified e2e: n/a). Never writes code in the main thread. Stops at the first task that can't be made green and reports. Use this as step 4, after 3-plan.md exists, to implement and commit the plan's TODO checklist."
allowed-tools: Read, Glob, Grep, Bash, Agent, Task, TaskCreate, TaskUpdate, TaskList, Edit(docs/work/**)
disallowed-tools: Write
---

# work-execute — Step 4: execute the plan

Step 4 of the spec-driven pipeline: research (`work-research`) → tests (`work-tests`) → plan
(`work-plan`) → **execute** → docs (`work-docs`). Walks the TODO checklist in
`docs/work/NNN-<slug>/3-plan.md`, turning each task into one atomic commit on the **unit's branch**
(`work/NNN-<slug>`, created in `work-research`). The orchestrator coordinates and commits; the
**`coder` subagent** writes all code.

## Keep in front of mind (every decision)
- **Think Before Coding** — the thinking is done in the plan; execute it faithfully.
- **Simplicity First** — implement exactly the task's acceptance criterion, nothing more.
- **Surgical Changes** — one task = one commit = one closed change.
- **Goal-Driven Execution** — a task is done only when **its own acceptance criterion** (from
  `3-plan.md`) is green and it's committed — not merely when the build/tests pass.
- Apply **KISS · YAGNI · SRP · DRY** — let the `coder` subagent resist scope creep.

## Core rules
- **The orchestrator drives, in the main thread.** This skill runs in the main session: the
  orchestrator owns every decision (what to dispatch, whether a task is green, when to commit, when
  to stop). It does this work itself — it does **not** delegate the coordination to a subagent — so
  the live TODO list and the decisions are visible in the main thread.
- **Mirror the plan into the TODO tool — and keep BOTH surfaces in lockstep.** Before dispatching
  anything, turn the plan's commit checklist into task-list items (`TaskCreate`); mark each
  `in_progress` (`TaskUpdate`) before dispatching its `coder` subagent. The live `TaskList` is the
  in-session decision/visibility surface; the `## TODO` checklist in `docs/work/NNN-<slug>/3-plan.md`
  is the **durable, in-repo record** that outlives the session. They must agree at all times — so
  for each task: flip its `[ ]→[x]` in `3-plan.md` **before** committing and fold that tick **into
  the task's own atomic commit** (the commit's tree shows the box checked), then `TaskUpdate` the
  live item to `completed` after the commit lands. Never leave the markdown tick dangling in the
  working tree as a separate, uncommitted change — that would pollute the next task's commit and
  break the clean-tree precondition.
- **Orchestrator never writes code — and edits ONLY the plan checklist.** This SKILL's frontmatter
  disallows `Write` entirely and scopes `Edit` to `docs/work/**`. The orchestrator's *only*
  permitted edit is ticking the `## TODO` boxes in `3-plan.md`. All production code and tests are
  written by the **`coder` subagent** (`.claude/agents/coder.md`), one atomic task at a time — never in
  the main thread.
- **One dispatch per BATCH; one atomic commit per TASK.** The plan groups tasks under `### Batch`
  headers. Dispatch **one** `coder` subagent per batch and give it **all** the batch's tasks (in
  listed order) in that single invocation — this is how we avoid spawning a subagent per micro-task.
  The subagent implements the whole batch and leaves the tree **uncommitted**; the **orchestrator**
  then walks the batch's task lines and makes **one atomic commit per task** (staging by path), each
  green before it lands. Batching never coarsens history — it changes how many subagents run, not
  how many commits there are. Note the acceptance check runs against the **full batch tree**, then
  only that task's files are staged — the committed subset is **not** rebuilt in isolation (fine:
  `main` gets one squashed commit; see `docs/commit-conventions.md` for the full scoping).
- **One task → one atomic commit on the unit's branch.** Never commit to `main` directly (the unit
  ends with a squash PR to `main`, team-reviewed and merged manually — `work-docs` opens it). Commit
  per `docs/commit-conventions.md` only after the task's **acceptance criterion** is green — usually the
  project's build + test commands (see `CLAUDE.md` → **Commands**); for tasks whose files the build
  doesn't cover (e.g. shell/infra scripts) it is the build-style check the plan names (e.g.
  `bash -n <script>` + `shellcheck <script>`).
- **The final batch is the live e2e smoke.** When the plan ends with an `e2e` task, dispatch the
  **`e2e-tester`** subagent (NOT `coder`) against the live system per `docs/test/README.md`; it writes
  ordered evidence + a pass/fail `summary.md` into `docs/test/NNN-<slug>/`. A **PASS summary is the
  acceptance criterion**; the orchestrator commits that evidence as one `test(e2e): …` commit. When
  the plan instead says `e2e: n/a — <reason>`, **skip** this batch and record the reason in the
  final report. The build/test gate does **not** cover the e2e run.
- **Red → green.** For implementation tasks, the `coder` subagent makes the mapped Given-When-Then
  tests pass with minimum code. **Avoid mocks** unless a true external seam genuinely requires one.
- **Parallel groups fan out; serial batches coalesce.** A `### Batch` marked **`parallel group`**
  means its tasks are file-disjoint and the orchestrator dispatches **one `coder` subagent per task**
  concurrently (fan-out). A normal **serial batch** is the opposite — **one** subagent for **all**
  the batch's tasks (coalesce, fewer subagents). Either way, **stage by path** — `git add <this
  task's files touched>` plus `3-plan.md` — and commit one task at a time; **never `git commit -a`**,
  or one commit would sweep in a sibling/next-task's uncommitted work.
- **Quality gate (necessary, not sufficient).** A Stop/SubagentStop hook
  (`.claude/hooks/quality-gate.sh`) runs the project's build + tests. Never finish or commit red.
  **But the gate only sees what it is configured to build** — it may no-op green on changes outside
  that scope (e.g. script/infra-only changes, or — on a multi-service repo with a routed gate — a path
  matching no route in `.claude/quality-gate.routes`). So a green gate does **not** prove a task
  outside that scope is verified; the orchestrator must run that task's own acceptance check itself
  (step 2c).
- **Fail loud, fail early.** Stop at the **first** task that can't be made green and report.
- **Model tier.** Dispatch every subagent (`coder` per batch, `e2e-tester` for the e2e) at the
  tier recorded as `Task tier` in `1-research.md` — pass **`model: sonnet`** for a **lightweight**
  unit, otherwise **Opus** (omit the param to inherit the always-Opus orchestrator). If execution
  reveals the unit is riskier than research thought, **bump the tier up to standard/Opus** for the
  remaining dispatches and say so. The tier changes only the worker model, never this step's procedure.
- All docs/commits in **English**.

## Procedure
1. **Preconditions — abort if any fails.** Read `docs/work/NNN-<slug>/3-plan.md`; it must exist and
   contain a `## TODO (work-execute consumes this)` block — **if it is missing or has no TODO block,
   stop and report** (do not improvise a plan). Confirm `git status` shows a **clean tree on
   `main`** — if the tree is dirty or you are off `main`, **stop and report** rather than committing
   onto someone else's WIP. Then take the TODO checklist as the work
   list, in order, and **create one task-list item per checklist entry** with `TaskCreate` so
   progress is tracked live.
2. **For each `### Batch`, in order:**
   a. **Dispatch once per batch.** `TaskUpdate` the batch's task items to `in_progress`. For a **serial
      batch**, dispatch **one** `coder` subagent and give it **all** the batch's tasks in listed
      order (each task's acceptance criterion, files touched, and mapped test IDs from `3-plan.md`),
      telling it to implement them back-to-back and **leave everything uncommitted**. For a
      **`parallel group`** batch, dispatch one `coder` subagent per task concurrently (disjoint
      files). For the **e2e batch**, dispatch the **`e2e-tester`** subagent instead — see step 2e.
   b. **Confirm the subagent left the tree UNcommitted** (`git status`/`git log` — the orchestrator,
      not `coder`, owns commits; a stray `coder` commit means a double-commit/atomicity break — stop and
      report).
   c. **Commit each task in the batch, one at a time, in listed order.** For each task line run
      **its own acceptance criterion from `3-plan.md`**: usually the project's build then test
      commands; for tasks the gate doesn't cover (e.g. shell/infra), the build-style check the plan
      names. Expected-red tasks may have failing **tests** by design — verify the failure is the
      planned one and the **build** is green; **never auto-"fix"** a red the plan declares
      intentional. Then tick this task's `[ ]→[x]` in the `## TODO` block of `3-plan.md` (the
      orchestrator's only edit), `git add <this task's files touched>` + `3-plan.md`, and make **one
      atomic commit** on the **unit's branch** per `docs/commit-conventions.md` — the tick rides
      **inside** that commit. Never `git commit -a`. `TaskUpdate` the item to `completed`.
   d. When every task in the batch is committed, move to the next batch.
   e. **E2E batch (final, when present).** If the plan ends with an `e2e` task: dispatch the
      **`e2e-tester`** subagent to run the live smoke per `docs/test/README.md`, writing ordered
      evidence + a pass/fail `summary.md` into `docs/test/NNN-<slug>/`. **On a multi-service repo, name
      the service(s) under test in the dispatch** so the tester follows the right `### <service>`
      subsection of the runbook. **Read the `summary.md`
      verdict** — a **PASS is the acceptance criterion**. On PASS, tick the box and commit the
      evidence (`git add docs/test/NNN-<slug>/` + `3-plan.md`) as one `test(e2e): …` commit. On
      **FAIL**, stop and report (do not commit a failing smoke as if it passed). If the plan says
      **`e2e: n/a — <reason>`**, skip this batch and carry the reason into step 4.
3. **On failure** (a task can't be made green / the build breaks / a parallel conflict / a stray
   `coder` commit / a FAIL e2e summary): **stop**, leave the tree clean, and report which
   task failed, why, and the exact acceptance output.
4. **On completion:** report the commits made (one per task, plus the `test(e2e)` evidence commit or
   the recorded `e2e: n/a` reason) and that the unit of work in `docs/work/NNN-<slug>/` is fully
   executed on the **unit's branch**. Hand off to `work-docs` (Step 5) to reconcile the surrounding
   documentation and open the squash PR to `main`.
