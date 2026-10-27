# 3-plan.md — reviewer validation checklist

The **reviewer subagent** (different from the author) checks the plan against every item below.
Any failure → return the plan to the author with specifics; loop until all pass.

## Coverage & traceability
- [ ] Every behaviour **test ID** in `2-tests.md` has at least one producing task (appears in some
      task's `maps-to test IDs`).
- [ ] No task maps to a test ID that doesn't exist in `2-tests.md`.
- [ ] Plan scope matches `1-research.md` — nothing added beyond the unit of work.

## Phasing & ordering
- [ ] Phases are present and ordered: baseline → seams → red-tests → implementation →
      consolidation/coverage → e2e.
- [ ] **Seams precede the red tests** that depend on them (tests compile when introduced).
- [ ] Red-test tasks are flagged `expected-red: yes`; all other tasks `expected-red: no`.
- [ ] Implementation tasks take their mapped tests red → green.

## E2E (always ends the plan)
- [ ] The plan ends with **either** a final `e2e` task that dispatches the **`e2e-tester`**
      subagent (live system per `docs/test/README.md`, evidence into `docs/test/NNN-<slug>/`)
      **or** a single explicit `e2e: n/a — <reason>` line.
- [ ] If `n/a`, the reason is justified — the unit ships **no** user-observable change (pure
      infra/build/refactor). Any user-observable change ⇒ a real e2e task is **required**.
- [ ] The e2e task is its **own batch**, `maps-to: n/a`, acceptance = PASS `summary.md` + evidence.

## Batching (fewest dispatches, still atomic commits)
- [ ] Every task has a `batch` id; tasks sharing a batch share a **phase** and a **coherent,
      non-conflicting file set** and are one **coder dispatch**.
- [ ] Batching is used to **minimise dispatches** — seams in one batch, all red tests in one batch
      ("tests up front"), implementation grouped by feature area — not one batch per micro-task.
- [ ] A **parallel group** (multiple concurrent subagents) is used **only** where areas are large
      and file-disjoint and the win beats the extra dispatches; otherwise a single serial batch is
      preferred.
- [ ] No batch merges two acceptance criteria into one commit (still one commit per task).

## Atomicity & parallelism
- [ ] Each task = **one commit = one acceptance criterion**, atomic (green at the batch boundary — see `docs/commit-conventions.md`).
- [ ] Each task is marked `serial` or `parallel group: <name>`, and carries a `batch` id.
- [ ] **Parallel tasks within a group have disjoint `files touched`** (no shared files).
- [ ] `files touched` is explicit for every task.

## Risk isolation
- [ ] Config / build-tooling tasks are flagged `high-risk: yes`, isolated in their own task, and
      have a **build acceptance criterion** (build green).
- [ ] No high-risk config change is mixed into a feature/implementation task.

## Conventions
- [ ] Commit convention named: every task is one atomic commit per `docs/commit-conventions.md`.
- [ ] Commits land on the **unit's branch** (`work/NNN-<slug>`), never directly on `main`; no plan
      step merges the PR (the team does that manually after review).
- [ ] No setup/cleanup tasks outside this unit of work.
- [ ] Plan ends with the **TODO commit checklist** in execution order that `work-execute` can
      consume verbatim, **grouped under `### Batch` headers** (one dispatch each).
- [ ] Document is in **English**.
