# Training infrastructure for Online Boutique

Provision per-attendee namespaces with a buggy boutique deployed, and
auto-deploy fixes when their PRs are merged. Designed for ~30 attendees
on a 1-day workshop, sharing an existing GKE Autopilot cluster.

## What attendees do

1. Open their training URL → reproduce the bug as a customer would
2. Check out their pre-seeded `attendee/<name>` branch (bug already
   committed, customer ticket as `BUG_REPORT.md`)
3. Use Claude Code to triage: locate the file, write an engineer-ready
   ticket (`ENGINEERING_TICKET.md`)
4. Fix the bug, push to a feature branch, open PR → `attendee/<name>`
5. PR auto-merges on green CI, GitHub Actions builds + pushes only the
   changed service to GAR, helm-upgrades their namespace
6. Re-test at the same URL

## Architecture in one paragraph

One GKE Autopilot cluster (`n8n-cluster` in `europe-west1`, shared with
prod) hosts a namespace per attendee (`attendee-<name>`). Each namespace
runs a trimmed Online Boutique (no loadgenerator, lean resource
requests). The cluster's existing nginx-ingress + external-dns +
cert-manager stack handles routing, DNS, and TLS — we just add an
Ingress per namespace pointing at `<name>.training.gcp.re-cinq.com`. A
single wildcard cert is replicated into each attendee namespace by
[reflector](https://github.com/emberstack/reflector). All images live in
one Artifact Registry (`europe-west1-docker.pkg.dev/re5-n8n-platform/microservices-demo-training`).
GitHub Actions pushes to GAR via Workload Identity Federation — no
service account keys.

## File layout

```
training/
├── terraform/         GAR repo + WIF pool/provider + IAM (run once)
├── k8s/               training-system ns + wildcard cert + reflector install
├── bugs/<bug-id>/     PATCH.diff (applied to attendee branch)
│                      BUG_REPORT.md (customer-voice ticket)
│                      ANSWER.md (trainer cheat sheet)
├── bootstrap/         provision.sh + teardown.sh + attendees.csv.example
├── values-training.yaml   Helm overrides (no loadgen, lean requests)
└── handouts/          (gitignored) generated per-attendee one-pagers
```

## One-time setup

### 1. Create GAR + WIF

```bash
cd training/terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform apply
```

Note the three outputs (`artifact_registry_repo`,
`workload_identity_provider`, `github_pusher_sa_email`).

### 2. Set GitHub repo variables

In `https://github.com/re-cinq/microservices-demo/settings/variables/actions`
add:

| Variable          | Value                                                              |
|-------------------|--------------------------------------------------------------------|
| `WIF_PROVIDER`    | output `workload_identity_provider`                                |
| `GAR_PUSHER_SA`   | output `github_pusher_sa_email`                                    |
| `GCP_PROJECT_ID`  | `re5-n8n-platform`                                                 |
| `GAR_REGION`      | `europe-west1`                                                     |
| `GAR_REPO`        | `microservices-demo-training`                                      |
| `GKE_CLUSTER`     | `n8n-cluster`                                                      |
| `GKE_REGION`      | `europe-west1`                                                     |

### 3. Bulk-copy upstream images to GAR as `:base`

```bash
for svc in adservice cartservice checkoutservice currencyservice \
           emailservice frontend paymentservice productcatalogservice \
           recommendationservice shippingservice; do
  src="us-central1-docker.pkg.dev/google-samples/microservices-demo/$svc:v0.10.5"
  dst="europe-west1-docker.pkg.dev/re5-n8n-platform/microservices-demo-training/$svc:base"
  gcloud container images add-tag --quiet "$src" "$dst"
done
```

### 4. Cluster-side setup

```bash
kubectl apply -f training/k8s/training-system.yaml
training/k8s/install-reflector.sh
# Wait for the wildcard cert to be Ready (may take 1-2 min for DNS-01)
kubectl -n training-system wait --for=condition=Ready certificate/wildcard-training --timeout=5m
```

### 5. Repository branch protection

For `attendee/*` (branch ruleset):
- Require pull request before merge: yes
- Approvals required: 0 (attendees self-merge)
- Require status checks to pass: yes, select `deploy-attendee` after first run
- Allow auto-merge: yes
- Restrict who can push: include training operator + the attendee

Or simpler for a 1-day workshop: skip protection, set `auto-merge` as the
default in repo settings, attendees enable it on their PR.

## Per-cohort provisioning

Make a CSV (`bootstrap/attendees.csv`) with one row per attendee:

```
name,bug
alice,currency-converter-mismatch
bob,visa-rejected
...
```

Run:

```bash
training/bootstrap/provision.sh training/bootstrap/attendees.csv
```

This creates each namespace + Helm release + Ingress + git branch
+ handout under `training/handouts/<name>.md`. Idempotent.

Print the handouts and hand them out. Attendees follow the instructions.

## Teardown after the training

```bash
training/bootstrap/teardown.sh training/bootstrap/attendees.csv
# or: training/bootstrap/teardown.sh --all
```

Leaves `training-system`, reflector, and the wildcard cert in place for
the next cohort.

## Bug catalog

| ID                                | Service                  | Language | Customer signal                              |
|-----------------------------------|--------------------------|----------|----------------------------------------------|
| `currency-converter-mismatch`     | currencyservice          | Node     | "Prices in JPY/TRY are tiny"                 |
| `visa-rejected`                   | paymentservice           | Node     | "Visa rejected, mastercard works"            |
| `duplicate-recommendations`       | recommendationservice    | Python   | "Same product appears twice in recs"         |
| `search-misses-descriptions`      | productcatalogservice    | Go       | "Search for descriptive words returns nothing" |

Each lives in `training/bugs/<id>/` with the patch, customer ticket, and
trainer answer.

## Cost note

Autopilot bills per pod resource request. With 30 attendees on the
trimmed `values-training.yaml`, expect roughly **15 vCPU + 20 GiB**
requested cluster-wide for the boutique pods, ~$5–7/hour. A full
8-hour day is ~$40–60.

## Things to know / footguns

- **PR concurrency**: `concurrency: deploy-${{ github.ref }}` cancels
  in-progress runs if an attendee pushes twice in quick succession.
  Their second push wins; the first is silently dropped. Tell them.
- **Helm `--reuse-values`**: the workflow uses `--reuse-values` and
  re-applies `values-training.yaml` on top via `-f`, so stale
  values from the bootstrap install are preserved + the per-service
  tag override is layered on. If you ever change `values-training.yaml`
  during a cohort, re-run `provision.sh` to roll it out.
- **Image leaks across attendees**: GAR is shared. An attendee can
  technically `docker pull` someone else's `attendee-bob-<sha>` image.
  Not a problem for a public training, but worth knowing.
- **Public repo + visible answers**: once any attendee's PR merges, the
  diff is public. Mitigation in place: 4-bug pool randomized across
  attendees + bugs chosen so the diff alone doesn't teach the triage
  skill (the skill is *finding* the file from a customer report).
- **LE rate limit**: we issue exactly one `*.training.gcp.re-cinq.com`
  cert and replicate it. The shared `re-cinq.com` registered domain has
  a 50/week LE limit — don't manually issue 30 per-host certs by
  mistake.
- **No kubectl for attendees**: deliberate. Forces them to triage from
  a customer's perspective rather than tailing logs.
