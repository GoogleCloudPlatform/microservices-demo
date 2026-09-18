# 3-plan.md — required format

The author subagent writes `docs/work/NNN-<slug>/3-plan.md` with **exactly** the structure
below. Keep it tight. Every commit lands on the unit's branch (`work/NNN-<slug>`), never on
`main`; the unit ends with a squash PR to `main`.

## Header
- **Title:** `# Plan: NNN-<slug>`
- **Inputs:** links to `1-research.md` and `2-tests.md`.
- **Summary:** 1–3 sentences — what shipping this plan achieves.
- **Commit convention:** state that every task is one atomic commit on the **unit's branch**
  (`work/NNN-<slug>`) per `docs/commit-conventions.md`, and the unit ends with a squash PR to
  `main` (team-reviewed, merged manually).

## Phases (in this order)
Tasks are grouped into phases and executed top-to-bottom:

1. **Baseline** — confirm the tree builds/tests green before changes (verification only; no
   subagent — the orchestrator runs it).
2. **Seams** — `serial`, compile-safe scaffolding (interfaces, signatures, wiring) so later tests
   compile. No behaviour yet.
3. **Red tests** — Given-When-Then tests from `2-tests.md`. These commits are expected-red by
   design (flag each task `expected-red: yes`). **Default: author every red test in ONE batch**
   (one coder dispatch — "write all the tests up front"); only split into a `parallel group` by area
   when the surface is large AND the areas are file-disjoint AND concurrency is worth the extra
   dispatch.
4. **Implementation (red → green)** — make each red test pass with the minimum code, **one
   implementation batch per feature area** (one coder dispatch per area).
5. **Consolidation / coverage** — edge/negative gaps, refactor for DRY, final green (one batch).
6. **E2E live smoke (MANDATORY when the unit changes user-observable behaviour)** — a final task
   that dispatches the **`e2e-tester`** subagent against the LIVE running system per
   `docs/test/README.md`, capturing ordered evidence + a pass/fail `summary.md` into
   `docs/test/NNN-<slug>/`. If — and only if — the unit ships **no** user-observable change (pure
   infra/build/refactor with identical runtime behaviour), replace this task with a single explicit
   line **`e2e: n/a — <one-sentence reason>`**. Never silently omit it.

## Batching: dispatch unit vs commit unit (how we avoid spawning too many subagents)
A **batch** is the **dispatch** unit — a group of tasks **one** `coder` subagent implements in a
**single** invocation, keeping its context warm. A batch is **NOT** a commit: inside a batch the
orchestrator still makes **one atomic commit per acceptance criterion** (staged by path), each
green when it lands. So batching cuts the number of subagent dispatches **without** coarsening the
commit history — fewer dispatches, same atomic commits along the way.

- **Group into one batch** the tasks that (a) sit in the **same phase**, (b) touch a **coherent
  file set**, and (c) the same subagent can do **back-to-back** without re-reading context.
- **Canonical batches:** all **seams** → one batch; all **red tests** → one batch ("tests up
  front"); **one implementation batch per feature area**; **consolidation** → one batch; **e2e** →
  its own task (dispatched to `e2e-tester`, not `coder`).
- **Prefer a single serial batch over a parallel group.** A `parallel group` fans work OUT to
  **multiple concurrent** `coder` subagents — only do that when the areas are large, file-disjoint,
  and the wall-clock win beats the extra dispatches. Otherwise coalesce into one serial batch (one
  subagent, sequential tasks) — that is **fewer** subagents.
- **Rough dispatch budget per unit:** seams (1) + tests (1) + implementation (1–3 by area) +
  consolidation (1) + e2e (1) ≈ **4–7 dispatches**, not one-per-micro-task.
- A batch is **never** allowed to merge two acceptance criteria into one commit. If two tasks
  can't each be committed green on their own, they are **one task**, not a batch of two.

## Per-task fields
Each task is a sub-section with **all** of these fields:

```
### <id>: <title>
- id: <T-task id, e.g. P3-07>
- phase: <baseline | seams | red-tests | implementation | consolidation | e2e>
- batch: <batch-id, e.g. B2 — tasks sharing a batch are ONE coder dispatch; or "own" if solo>
- mode: <serial | parallel group: <group-name>>
- files touched: <explicit list of files; parallel tasks in the same group MUST NOT overlap>
- acceptance criterion: <one observable, checkable outcome = the commit's reason to exist>
- maps-to test IDs: <T-001, T-002 ... from 2-tests.md; or "n/a" for baseline/seams/config>
- expected-red: <yes | no>   # yes only for red-test tasks
- high-risk: <yes | no>      # yes for config/build-tooling; isolate; build must stay green
```

Rules encoded by the fields:
- **One task = one commit = one acceptance criterion.** (Batching changes *dispatch*, never this.)
- **`batch` is the dispatch unit.** All tasks with the same `batch` id are handed to **one** `coder`
  subagent in a single dispatch; the orchestrator still commits each task atomically. Tasks in the
  same batch share a phase and a coherent file set and run **in listed order**.
- Every behaviour **test ID** in `2-tests.md` must appear in `maps-to` of at least one task.
- `parallel group` tasks must have **disjoint** `files touched`.
- `seams` tasks are `serial` and precede the `red-tests` that depend on them.
- `high-risk: yes` tasks are config/build-tooling, isolated in **their own batch**, with a build
  acceptance criterion. Never fold a high-risk task into a feature batch.
- The `e2e` task (when present) is its **own batch**, dispatched to the **`e2e-tester`** subagent
  (not `coder`); its acceptance criterion is a **PASS `summary.md` + evidence** under
  `docs/test/NNN-<slug>/`, and `maps-to` is `n/a` (it is a live black-box smoke, not a unit test).

## Final TODO commit checklist
End the file with an ordered checklist that `work-execute` consumes verbatim. **Group lines under
a `### Batch` header** — each header is **one coder dispatch**; each `- [ ]` line under it is **one
atomic commit**. The header names the dispatch target (`coder` by default, `e2e-tester` for the e2e
batch) and `serial` vs `parallel group`. The e2e batch comes **last**; if the unit has no
user-observable change, replace it with the single `e2e: n/a — …` line.

```
## TODO (work-execute consumes this)

### Batch B0 — baseline (orchestrator only, no dispatch)
- [ ] P3-01 (baseline) verify build+test green

### Batch B1 — seams (1 coder dispatch, serial)
- [ ] P3-02 (seams) <title>

### Batch B2 — red tests (1 coder dispatch, serial) [expected-red]
- [ ] P3-03 (red-tests) area-a specs  -> maps T-001, T-002
- [ ] P3-04 (red-tests) area-b specs  -> maps T-003

### Batch B3 — implementation: area-a (1 coder dispatch, serial)
- [ ] P3-05 (implementation) <title>  -> maps T-001
- [ ] P3-06 (implementation) <title>  -> maps T-002

### Batch B4 — consolidation (1 coder dispatch, serial)
- [ ] P3-07 (consolidation) DRY + edge gaps, final green

### Batch B5 — e2e live smoke (1 e2e-tester dispatch)
- [ ] P3-08 (e2e) live smoke per docs/test/README.md -> evidence in docs/test/NNN-<slug>/
# or, when nothing user-observable changed, replace Batch B5 with exactly:
# e2e: n/a — <one-sentence reason>
```
