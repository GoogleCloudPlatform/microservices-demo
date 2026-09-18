# Online Boutique (microservices-demo)

> A cloud-first microservices demo application: an 11-tier web e-commerce app
> ("Online Boutique") where users browse items, add them to a cart, and purchase
> them. Polyglot — services are written in Go, C#, Java, Node.js, and Python and
> communicate over gRPC.
>
> **Current state:** 12 services under `src/`, deployed to Kubernetes via
> `skaffold` + `kubernetes-manifests/` (also Helm, Kustomize, Terraform). CI
> unit-tests the Go and C# services; a full deploy + smoke test runs on GKE.

**Think Before Coding** — Don't assume. Don't hide confusion. Surface tradeoffs.
**Simplicity First** — Minimum code that solves the problem. Nothing speculative.
**Surgical Changes** — Touch only what you must. Clean up only your own mess.
**Goal-Driven Execution** — Define success criteria. Loop until verified.

## Coding principles
- **KISS** — the simplest thing that works.
- **YAGNI** — don't build what isn't asked for.
- **SRP** — one reason to change per unit.
- **DRY** — one source of truth; don't duplicate logic.

## Development workflow — dev-kit
This repo uses the **dev-kit** spec-driven pipeline. For ANY feature, bug fix, or refactor, the main
session acts ONLY as an **orchestrator**: it invokes the `dev-kit` skill and runs
research → tests → plan → execute → docs. Production code and tests are written by the
[coder](.claude/agents/coder.md) subagent (and live smokes by `e2e-tester`) — **never inline in
the main thread**. Exempt: pure questions about how the code works, a one-line edit the user
explicitly asks to apply inline, and non-code chores.
The flow is the same for every unit; only the model tier differs — run the orchestrator (this main
session) on **Opus** for pipeline work (`/model opus`; there is deliberately no repo-wide `model` pin
in `.claude/settings.json`, so unrelated sessions aren't forced onto Opus), and the worker subagents
run on **Sonnet** for a **lightweight** unit (classified at the end of research) or **Opus** for a
**standard** one.

## How we work
- **Always track work in the TODO tool** (`TaskCreate`/`TaskUpdate`/`TaskList`) for any task with
  3+ steps or multiple delegations: write the plan first, one `in_progress` at a time.
- **Subagents do the coding.** The main session is an **orchestrator only** — it plans, delegates,
  verifies, and commits. It does not write production code directly. Delegate to the
  [coder](.claude/agents/coder.md) subagent, one small atomic task at a time.
- **Internet research is ALWAYS delegated to a clean subagent.** For library/SDK/cloud APIs prefer
  the docs MCPs (context7; Microsoft Learn for Azure/Foundry) over open-web guessing or memory.
- **Branch per unit; squash PR to `main`; manual merge.** Each unit of work runs on its own branch
  (`work/NNN-<slug>`) off `main`; every commit is **atomic** and lands on that branch; the unit
  ends with a **squash PR to `main`** that the team reviews and merges manually — never commit to
  `main` directly. See [docs/commit-conventions.md](docs/commit-conventions.md).
- **Spec-driven for non-trivial work.** Follow the pipeline in
  [docs/work/README.md](docs/work/README.md): research → tests → plan → execute → docs. Artifacts
  live in `docs/work/NNN-<slug>/`.
- **Quality gate.** A Stop/SubagentStop hook runs the build + tests; nothing finishes red. See
  [.claude/hooks/quality-gate.sh](.claude/hooks/quality-gate.sh). This is a multi-service repo, so
  the gate is **routed**: [.claude/quality-gate.routes](.claude/quality-gate.routes) maps each
  service's path to its own build/test commands, so the gate runs only the service that changed —
  work in *the service you are editing* and check the green you get is that service's.
- **All docs and code are written in English.**

## Commands
There is no single build/test command — this repo is polyglot. Build/test **the service you are
editing**; the per-service commands the quality gate runs live in
[.claude/quality-gate.routes](.claude/quality-gate.routes).

| Service / area | Stack | Build | Test |
| :------------- | :---- | :---- | :--- |
| `src/frontend/` | Go 1.26 | `go -C src/frontend build ./...` | `go -C src/frontend test ./...` |
| `src/shippingservice/` | Go 1.26 | `go -C src/shippingservice build ./...` | `go -C src/shippingservice test ./...` |
| `src/productcatalogservice/` | Go 1.26 | `go -C src/productcatalogservice build ./...` | `go -C src/productcatalogservice test ./...` |
| `src/checkoutservice/` | Go 1.26 | `go -C src/checkoutservice build ./...` | _(none; pre-existing vet issue)_ |
| `src/cartservice/` | C# / .NET 10 | `dotnet build src/cartservice/` | `dotnet test src/cartservice/` |
| `src/adservice/` | Java 21 / Gradle | `sh src/adservice/gradlew -p src/adservice compileJava` | _(none)_ |
| Node.js: `currencyservice`, `paymentservice` | Node 22+ | _(no build)_ | _(no unit tests)_ |
| Python: `emailservice`, `recommendationservice`, `loadgenerator`, `shoppingassistantservice` | Python 3.12 | _(no build)_ | _(no unit tests)_ |

| Action | Command |
| :----- | :------ |
| Run (full app) | `skaffold run` (or `skaffold dev`) against a Kubernetes cluster (minikube / GKE) — see `docs/development-guide.md` |
| Format (Go) | `gofmt -w` on the edited Go service |

> The `coder` subagent and the quality gate read these. They are the single source of truth for
> "is this task green?". Build/test the service you're editing.

## Structure
- `src/<service>/` — the 12 microservices (Go, C#, Java, Node.js, Python), one dir each, gRPC.
- `protos/` — shared gRPC protobuf definitions.
- `kubernetes-manifests/`, `helm-chart/`, `kustomize/`, `istio-manifests/` — deployment manifests.
- `terraform/` — infra provisioning for GKE.
- `skaffold.yaml` — build + deploy orchestration for local/CI.
- `.github/workflows/` — CI (`ci-pr.yaml`, `ci-main.yaml`) and release automation.
- `docs/work/` — spec-driven pipeline artifacts (`NNN-<slug>/`).
- `docs/test/` — e2e runbook + live-smoke evidence.
- `.claude/` — committed agents, skills, hooks, settings, and `dev-kit.manifest` (the vendored dev-kit
  and its version stamp).

## Coding standards (the `coder` subagent loads these when the files match)
This repo has no separate style-guide docs; the toolchains' own config is the standard.
- Go's `gofmt` / `go vet` (run by `go test`) — the Go services (`frontend`, `checkoutservice`,
  `shippingservice`, `productcatalogservice`).
- `.editorconfig` (repo root) — whitespace/indent for all services.
- `.github/header-checker-lint.yml` — every source file needs the Apache-2.0 license header.
- Match the surrounding service's existing idioms; each service is self-contained.

## Tools & plugins
- `context7` MCP — up-to-date library/SDK docs, so APIs aren't guessed from memory.
