---
name: work-docs
description: Step 5 (final) of the work pipeline (research → tests → plan → execute → docs). After work-execute lands a unit's commits, reconciles ALL documentation OUTSIDE the docs/work/NNN-<slug>/ artifacts so it matches the shipped reality — CLAUDE.md, the prose docs under docs/, every README.md, docs/work/README.md (the pipeline doc, only if the pipeline itself changed), and TODO.md (condense fully-shipped items into a historical `- [x] … — <commit>` checklist). Subagents author (one per surface, disjoint files), an independent reviewer validates against the code, the orchestrator commits atomic docs commits on the unit's branch, then opens a squash PR to main for team review. Never edits the NNN-<slug> research/tests/plan artifacts; never writes code. Use this as step 5, after work-execute has committed the unit, to bring the docs back in sync.
allowed-tools: Read, Glob, Grep, Bash(ls *), Bash(find *), Bash(git *), Agent, Task, TaskCreate, TaskUpdate, TaskList
disallowed-tools: Write, Edit, WebSearch, WebFetch
---

# work-docs — Step 5: reconcile the documentation

Final step of the spec-driven pipeline: research (`work-research`) → tests (`work-tests`) → plan
(`work-plan`) → execute (`work-execute`) → **docs**. Once a unit's code is committed on the unit's branch, the
surrounding documentation has drifted: `CLAUDE.md` describes the old current-state, a README
references a removed endpoint, `TODO.md` still lists a finished item as open. This step walks the
just-shipped change set and brings **all documentation outside the `docs/work/NNN-<slug>/`
artifacts** back in sync with what the code now actually does.

The orchestrator coordinates and commits; **subagents** do the writing; an **independent reviewer**
validates every claim against the code. Author ≠ reviewer.

## Keep in front of mind (every decision)
- **Think Before Coding** — the code is already shipped; the job is to make the docs *true*.
- **Simplicity First** — change only the sentences the unit invalidated. No doc rewrites.
- **Surgical Changes** — touch only the lines the shipped change made wrong or missing.
- **Goal-Driven Execution** — done means: every doc statement matches the committed code, and
  `TODO.md` reflects what is finished vs open. Verified, not assumed.
- Apply **KISS · YAGNI · SRP · DRY** — don't add speculative docs; one source of truth per fact.

## What is IN scope (everything outside the work artifacts)
- **`CLAUDE.md`** (root) — the "Current state" paragraph, Structure, Commands, anything the unit
  changed. This is the single most-read file; keep it honest about what exists *now*.
- **Prose docs under `docs/`** — architecture, repo-structure, environment, testing, etc.
  (commit-conventions only if the conventions themselves changed.)
- **Every `README.md`** the unit touched — root and any sub-package READMEs. Leave the rest.
- **`docs/work/README.md`** — the pipeline doc. Update it **only if the pipeline itself changed** (a
  new/renamed step, a changed convention). It is the one file *inside* `docs/work/` this step may
  edit.
- **`TODO.md`** (root, if present) — reconcile the backlog (see below).

## What is OUT of scope (never touch)
- **The unit artifacts `docs/work/NNN-<slug>/{1-research,2-tests,3-plan}.md`.** These are the
  immutable record of how the unit was built, each committed by its own step. This skill does
  **not** edit them.
- **Production code and tests.** This step writes documentation only. If syncing the docs reveals
  the *code* is wrong, **stop and report** — that is a new unit of work, not a doc edit.

## Core rules
- **Track steps in the TODO tool.** Use the task/todo list (`TaskCreate`/`TaskUpdate`) for the
  detect → author → review → commit steps; one `in_progress` at a time, `completed` when done.
- **Orchestrator writes nothing.** This SKILL's frontmatter disallows `Write`/`Edit` entirely: the
  main session reads, coordinates, verifies, and commits. The **author subagents** it spawns have
  `Write` and make every doc edit; a **different** reviewer subagent validates. Author ≠ reviewer —
  exactly as in `work-research`/`work-plan`.
- **Ground every claim in the committed reality — never in the plan's intentions.** Docs describe
  what the code *does now*, not what the unit set out to do. The author must verify each edited
  statement against the source, tests, and the actual commits (`git log`/`git show`/`git diff`). The
  working tree often carries uncommitted WIP — so describe what is **true now**, and don't document
  half-built layers as if they shipped.
- **Surgical, not a rewrite.** Edit the sentences the unit invalidated; preserve each file's
  existing structure, voice, and heading layout. No reflowing, no reordering, no "while I'm here".
- **Fan out by surface, disjoint files.** The doc surfaces are independent files, so dispatch one
  author subagent **per surface** (e.g. CLAUDE.md / the touched `docs/*.md` / the touched READMEs /
  TODO.md) in parallel — they must edit **disjoint files**. A single reviewer subagent then
  validates the whole set together.
- **`TODO.md` is a historical checklist.** See the dedicated section below.
- **Atomic `docs` commits on the unit's branch.** Stage **by path** and commit per
  `docs/commit-conventions.md` (`docs: …` / `docs(work): …`). Never `git commit -a` — that would
  sweep in unrelated WIP. Keep it to the fewest atomic commits that read as one closed change
  (typically one `docs: reconcile … for NNN <slug>` commit; split TODO grooming into its own commit
  only if it is unrelated to this unit). These are the **last commits before the squash PR**.
- **Quality gate.** Doc-only changes don't affect the build, but the Stop/SubagentStop hook still
  runs — keep the build/tests green (they are, since no code changed) and never leave the tree dirty
  after committing.
- **Model tier.** Dispatch every subagent (per-surface authors, reviewer) at the tier recorded as
  `Task tier` in `1-research.md` — pass **`model: sonnet`** for a **lightweight** unit, otherwise
  **Opus** (omit the param to inherit the always-Opus orchestrator). The tier changes only the worker
  model, never this step's procedure.
- All docs in **English**.

## TODO.md — reconcile to a historical checklist
`TODO.md` is the backlog. After a unit ships, groom it so it reflects truth and stays small:
- **Condense fully-shipped items.** When a backlog item is completely delivered, collapse its
  verbose decision/prose block into a **single simple checklist line**, ticked, with the commit
  where it landed:
  ```
  - [x] <short item title> — shipped in <NNN-slug> (<short-sha or final commit subject>)
  ```
  Keep a one-line pointer to its `docs/work/NNN-<slug>/` unit if useful; drop the long rationale (it
  already lives in the unit's research/plan).
- **Leave open items as `- [ ]`.** Items not yet done stay unchecked, in the same simple `- [ ]`
  form. Don't invent new backlog items here.
- **Result:** `TODO.md` becomes a flat, scannable history — done work crossed off with its commit,
  open work as plain unchecked boxes — not a wall of prose.

## Procedure
1. **Identify the shipped change set — abort if unclear.** Confirm with the user (one line) which
   unit just shipped; reuse its `NNN-<slug>`. Confirm `git status` shows a **clean tree on the unit's
   branch** (`work/NNN-<slug>`) — if dirty or off the branch, **stop and report** (don't reconcile
   onto someone's WIP). Determine
   what actually changed: `git log`/`git diff` for the unit's commits and the current source state.
2. **Find the drift.** For each in-scope surface, read it and compare against the shipped reality.
   Build the precise edit list: which file, which statement, what it should now say. If nothing
   drifted for a surface, leave it untouched (and say so). If a doc is correct only because the
   *code* is wrong, **stop and report** — that's a new unit, not a doc edit.
3. **Author subagents (parallel, one per surface, disjoint files).** Dispatch an author subagent per
   surface with its exact edit list, the grounding evidence (the relevant commits/code), and the
   rule "surgical edits only; verify every changed sentence against the code". Include
   `docs/work/README.md` only if the pipeline itself changed, and `TODO.md` per the section above.
4. **Independent reviewer subagent (one, over the whole set).** A subagent that did **not** author
   validates: every edited statement matches the committed code (spot-check against the source/`git
   show`); no NNN-`<slug>` artifact was touched; no production code/tests changed; edits are surgical
   (no gratuitous rewrites); `TODO.md` follows the historical-checklist form; English; internal
   links still resolve. Loop author→reviewer until it passes with no open items.
5. **Commit on the unit's branch.** The orchestrator stages **by path** the touched doc files
   (`git add CLAUDE.md docs/… README.md TODO.md …`) and makes the atomic `docs: …` commit(s) per
   `docs/commit-conventions.md`. Never `git commit -a`; never stage `docs/work/NNN-<slug>/` artifacts
   (already committed by their own steps).
6. **Open the squash PR to `main`.** Push the unit's branch and open a **squash** PR into `main`
   (e.g. `gh pr create --base main`), titled for the unit, with a description that summarises the
   change and links the `docs/work/NNN-<slug>/` artifacts. **The team reviews and merges it manually
   — you do NOT merge it, and you never commit to `main` yourself.** (Follow the repo's own PR
   conventions if it has them — labels, reviewers, template.)
7. **On failure** (drift can't be resolved without a code change / reviewer can't pass / a stray edit
   hit a work artifact or code): **stop**, leave the tree clean, and report what blocked it.
8. **On completion:** report the doc commit(s) made, which surfaces changed (and which were already
   accurate), the **PR URL** awaiting team review, and that the documentation is back in sync with the
   unit shipped in `docs/work/NNN-<slug>/`.
