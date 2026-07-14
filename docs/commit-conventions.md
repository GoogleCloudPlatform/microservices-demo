# Commit conventions

**Each unit of work gets its own branch** off `main` (`work/NNN-<slug>`, created in
`work-research`). Every commit is **atomic** — one closed change carrying exactly one acceptance
criterion (or a deliberately, clearly-flagged expected-red test commit) — and lands on that branch,
**never directly on `main`**. "Atomic" is scoped honestly: the acceptance check runs against the full
batch tree, so the tree is green at every **batch boundary**, but a single commit's subset is not
rebuilt in isolation and is not guaranteed to build when checked out alone — the per-task commits
exist for branch review and bisect granularity. That is fine because the unit ends with a **squash PR
to `main`** (opened by `work-docs`), so `main` receives **one squashed commit**, which the **team
reviews and merges manually**. The orchestrator never commits to `main` and never merges its own PR.
(If the repo has its own branch-naming / PR conventions, follow them.)

## Format
Conventional-commit style:

```
<type>(<scope>): <imperative summary>

<optional body — why, not just what>
```

- **type** — `feat` · `fix` · `refactor` · `test` · `docs` · `chore` · `build` · `perf`.
- **scope** — the area touched (e.g. a module/feature name); optional but encouraged.
- **summary** — imperative mood, lower-case, no trailing period, ~72 chars.

## Rules
- **One task = one commit = one acceptance criterion.** Don't bundle unrelated changes.
- **Stage by path** (`git add <files>`), **never `git commit -a`** — that sweeps in sibling WIP and
  breaks atomicity.
- **Green before commit.** The task's acceptance check (build + tests, or the build-style check the
  plan names for non-code tasks) passes on the **batch tree** before the commit lands — see the
  batch-boundary scoping in the intro above.
- **Pipeline commits** use these subjects:
  - `docs(work): research NNN <slug> …` — Step 1 artifact.
  - `docs(work): behaviour spec NNN <slug> …` — Step 2 artifact.
  - `docs(work): implementation plan NNN <slug> …` — Step 3 artifact.
  - feature/`test`/`fix` commits — Step 4 (one per task; the TODO tick rides inside the commit).
  - `test(e2e): …` — Step 4 live-smoke evidence under `docs/test/NNN-<slug>/`.
  - `docs: reconcile … for NNN <slug>` — Step 5 documentation sync.
