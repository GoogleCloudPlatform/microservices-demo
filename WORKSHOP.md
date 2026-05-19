# Workshop Branches

Quick reference for the staged branches used in the Claude Code
enablement workshop. If you're not running the workshop, ignore this
file — `main` is the canonical workshop starting point.

## Where to start

- **Lab 1 (cross-service feature build):** start on `main`. Lab 1 has
  you design and implement FBT from scratch.
- **Lab 1 review (planted regression):** check out `lab1/peer-review`.
  This is a complete FBT implementation that builds and runs and has a
  hidden bug. Use Claude as your reviewer to find it.
- **Lab 2 (distributed debug):** start on `lab2/start`. The FBT feature
  is already implemented and a race-condition bug has been introduced.
  Reproduce, investigate, fix, test.

## First-time setup

`cartservice` (.NET 10) is not built locally by the compose files: the
SDK Docker build fails under Docker Desktop on Apple Silicon (MSB4184
during BuildKit restore; protoc SIGSEGV during the classic-builder
publish). Pull the published v0.10.5 image and tag it as
`cartservice:5096a85` once, before the first `docker compose up`:

```bash
docker pull us-central1-docker.pkg.dev/google-samples/microservices-demo/cartservice:v0.10.5@sha256:85c4fee0ddb6eada076003abcbff17ac3daf8e18dde68c7bde03b15fc8e17417
docker tag us-central1-docker.pkg.dev/google-samples/microservices-demo/cartservice:v0.10.5 cartservice:5096a85
```

The pulled image is amd64 and runs under Docker Desktop's emulation
alongside the locally-built arm64 services. Workshop labs do not modify
cartservice internals, so the version skew is intentional.

## Branch map

### Starting points

| Branch       | What it is                                                                                                                                                  |
| ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `main`       | Clean workshop foundation. `docker compose up -d --build` (first run builds all images, ~5-10 min) and the FBT panel does not yet exist. Lab 1 starts here. |
| `lab2/start` | `lab1/complete` plus a few realistic-looking evolution commits. One introduces a cache race in FBT recommendations. Lab 2 starts here.                      |

### Lab 1 — bailout checkpoints

If you fall behind during Lab 1, an architect can point you at the
checkpoint that matches where you are. Stash your work, check out the
checkpoint, and continue from there.

| Branch                    | State                                                                                                          |
| ------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `lab1/checkpoint-proto`   | Proto contract added (FBT + GetCartHistory), all language stubs regenerated. No service implementations yet.   |
| `lab1/checkpoint-backend` | Above plus `cartservice` GetCartHistory and `recommendationservice` ListFrequentlyBoughtTogether. No frontend. |
| `lab1/complete`           | Above plus the frontend FBT panel. Full feature, ready to demo.                                                |

### Lab 1 — peer review

| Branch             | State                                                                                              |
| ------------------ | -------------------------------------------------------------------------------------------------- |
| `lab1/peer-review` | Alternate complete FBT implementation with a deliberate planted regression. Use Claude to find it. |

### Lab 2 — bailout checkpoints

| Branch                       | State                                                                                                                |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `lab2/checkpoint-hypothesis` | `lab2/start` plus `notes/repro.md` and `notes/investigation.md` capturing reproduction and the cache-key hypothesis. |
| `lab2/checkpoint-fix`        | Above plus the fix (cache key includes cart contents) and `notes/fix.md`.                                            |
| `lab2/complete`              | Above plus the regression test that catches the bug.                                                                 |

### Reference

| Branch                       | State                                                                                                                                                                                                                                                          |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `reference/fbt-cooccurrence` | Branched from `lab1/complete`. Replaces the hardcoded co-occurrence map with lift/confidence association mining over a seeded transaction history. Includes `notes/prompts.md` capturing the prompt scaffolding that built it. Used at debrief; not a bailout. |

## Pulling a checkpoint mid-lab

```bash
git stash push -m "lab1 in-progress"
git checkout lab1/checkpoint-backend
docker compose up -d --build       # if you're not already running
# continue from here
```

To return to your work later: `git checkout your-branch && git stash pop`.

## Inside Claude Code

Run `/lab-help` from the repo root to print this branch list. The
slash command is defined under `.claude/commands/lab-help.md`.
