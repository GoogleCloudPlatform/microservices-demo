# Terraform: Online Boutique infrastructure (forgeteam)

Terraform provisions and deprovisions infrastructure: one GKE cluster and two environments (staging, production) using K8s namespaces. Naming and backend are set up for **forgeteam**.

---

## DevOps: How to work with this repo and Terraform state

**For anyone joining the team** — short guide to using this repo and the shared Terraform state.

### What you need

- **Repo**: clone as usual (`git clone ...`, then `cd microservices-demo`).
- **Tools**: Terraform >= 1.5, `gcloud`, `kubectl`.
- **GCP access**: permissions to use the project **forgeteam** (and the bucket `forgeteam-tfstate-1771882722` for state).  
  Authenticate once:
  ```bash
  gcloud auth application-default login
  gcloud config set project forgeteam
  ```

### Terraform state (important)

- **One bucket**: `forgeteam-tfstate-1771882722` (GCS). All Terraform state lives here.
- **Three states** (different prefixes in that bucket):
  - `state/cluster` — GKE cluster only.
  - `state/staging` — app deploy in namespace `staging`.
  - `state/production` — app deploy in namespace `production`.

You **do not** pass the bucket at init; it’s already in each env’s `backend.tf`.  
Do **not** edit state by hand; use `terraform plan/apply/destroy` from the correct env directory.

### Where to run Terraform

Always run Terraform **from the environment directory** you are changing:

- Cluster: `terraform/environments/cluster`
- Staging: `terraform/environments/staging`
- Production: `terraform/environments/production`

Never run `terraform` from `terraform/` root or from the repo root for these envs.

### First-time setup (cluster not created yet)

1. **Cluster (once per project)**  
   ```bash
   cd terraform/environments/cluster
   cp terraform.tfvars.example terraform.tfvars   # optional: project_id default is forgeteam
   terraform init
   terraform plan
   terraform apply
   ```
2. **Staging**  
   ```bash
   cd terraform/environments/staging
   cp terraform.tfvars.example terraform.tfvars   # optional
   terraform init
   terraform plan
   terraform apply
   ```
3. **Production**  
   ```bash
   cd terraform/environments/production
   cp terraform.tfvars.example terraform.tfvars   # optional
   terraform init
   terraform plan
   terraform apply
   ```

Staging and production read cluster name/region from cluster state (remote state); cluster must be applied first.

### Daily use (cluster already exists)

- **Change cluster (e.g. region, name)**:  
  `cd terraform/environments/cluster` → edit vars / tfvars → `terraform plan` → `terraform apply`.
- **Redeploy app to staging**:  
  `cd terraform/environments/staging` → `terraform plan` → `terraform apply` (re-runs `kubectl apply -k` for staging overlay).
- **Redeploy app to production**:  
  `cd terraform/environments/production` → same as above.
- **Only see what would change**:  
  In the right env dir: `terraform plan`.

### Frontend URLs

After staging/production apply:

- Staging:  
  `kubectl get svc frontend-external -n staging -o jsonpath='{.status.loadBalancer.ingress[0].ip}'`  
  Then open `http://<IP>`.
- Production:  
  `kubectl get svc frontend-external -n production -o jsonpath='{.status.loadBalancer.ingress[0].ip}'`.

Make sure `kubectl` context points to the forgeteam GKE cluster (Terraform apply does `gcloud get-credentials` for you when you run apply).

To apply manifests manually (without Terraform), from the **repo root** run:  
`kubectl apply -k kustomize/overlays/staging`  
Do not use `kubectl apply -f path/to/kubernetes-manifests/` — that directory contains `kustomization.yaml`, which is not a Kubernetes resource.

### Destroy (teardown)

Order matters:

1. `cd terraform/environments/staging` → `terraform destroy`
2. `cd terraform/environments/production` → `terraform destroy`
3. `cd terraform/environments/cluster` → `terraform destroy`

Do **not** destroy cluster before staging and production; staging/prod need the cluster to clean up their deploy resources.

### Changing variables

- **cluster**: `terraform/environments/cluster/terraform.tfvars` (or `.tfvars.example` as template). Main: `project_id`, `name`, `region`, `enable_apis`.
- **staging / production**: `terraform/environments/staging/terraform.tfvars` and `.../production/terraform.tfvars`. Main: `project_id`, `tfstate_bucket` (default already set). If you set `use_remote_state = false`, you must set `cluster_name` and `region` manually.

Commit `terraform.tfvars.example`; keep real `terraform.tfvars` out of git if it contains secrets (add to `.gitignore` if needed).

### Don’ts

- Don’t run `terraform apply` from `terraform/` or repo root for cluster/staging/production.
- Don’t destroy cluster before destroying staging and production.
- Don’t edit Terraform state files in GCS by hand.
- Don’t use a different state bucket/prefix unless you’re intentionally creating a new env (e.g. another team/project).

---

## State model (one bucket, three states)

- **One GCS bucket**: `forgeteam-tfstate-1771882722`
- **Three separate state files** (different key prefixes), so staging and production do **not** share state:

| Environment | State key (prefix)   | What it manages                          |
|-------------|----------------------|------------------------------------------|
| cluster     | `state/cluster`      | GKE cluster only                         |
| staging     | `state/staging`      | Deploy to namespace `staging` only       |
| production  | `state/production`   | Deploy to namespace `production` only    |

So: **one bucket, three states** — correct for isolating cluster, staging, and production. Staging and prod each have their own state and only deploy app manifests to their namespace; they read cluster name/region from cluster state via `terraform_remote_state`.

## Structure

```
terraform/
├── modules/
│   ├── gke/          # GKE Autopilot cluster + optional API enablement
│   └── app-deploy/   # get-credentials + kubectl apply -k (deploy into namespace)
└── environments/
    ├── cluster/      # single cluster per project
    ├── staging/      # deploy to namespace staging
    └── production/   # deploy to namespace production
```

## Prerequisites

- [Terraform](https://www.terraform.io/downloads) >= 1.5
- GCP project and `gcloud` CLI
- Auth: `gcloud auth application-default login` and `gcloud config set project YOUR_PROJECT_ID`

## How to run (order matters)

Run from the repo root. Set your GCP project in each env's `terraform.tfvars` (`project_id`).

**1. Cluster (once per project)**  
`cd terraform/environments/cluster` → copy `terraform.tfvars.example` to `terraform.tfvars`, set `project_id` → `terraform init` → `terraform plan` → `terraform apply`

**2. Staging**  
`cd terraform/environments/staging` → copy `terraform.tfvars.example` to `terraform.tfvars`, set `project_id` → `terraform init` → `terraform plan` → `terraform apply`  
Frontend: `kubectl get svc frontend-external -n staging -o jsonpath='{.status.loadBalancer.ingress[0].ip}'`

**3. Production**  
`cd terraform/environments/production` → same as staging (set `project_id`) → `terraform init` → `terraform plan` → `terraform apply`  
Frontend: `kubectl get svc frontend-external -n production -o jsonpath='{.status.loadBalancer.ingress[0].ip}'`

## Backend (GCS, forgeteam)

All environments use the same bucket **forgeteam-tfstate-1771882722** with a distinct prefix per env:

| Environment | Prefix            |
|-------------|-------------------|
| cluster     | `state/cluster`   |
| staging     | `state/staging`   |
| production  | `state/production` |

Bucket is set in each env's `backend.tf`; run `terraform init` with no extra flags.

## Usage

### 1. Cluster (once per project)

```bash
cd terraform/environments/cluster
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars: project_id, and enable_apis if needed

terraform init
terraform plan
terraform apply
```

After apply, note `cluster_name` and `cluster_location` (or rely on remote state in staging/production).

### 2. Staging (namespace `staging`, frontend via LoadBalancer)

```bash
cd terraform/environments/staging
cp terraform.tfvars.example terraform.tfvars
# Set project_id; tfstate_bucket is already in example

terraform init
terraform plan
terraform apply
```

Frontend in staging:

```bash
kubectl get svc frontend-external -n staging -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
# Open http://<IP>
```

### 3. Production (namespace `production`)

```bash
cd terraform/environments/production
cp terraform.tfvars.example terraform.tfvars
# project_id and tfstate_bucket same as staging

terraform init
terraform plan
terraform apply
```

Frontend in production:

```bash
kubectl get svc frontend-external -n production -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

## Destroy

Reverse order: staging and production first, then cluster.

```bash
cd terraform/environments/staging && terraform destroy
cd ../production && terraform destroy
cd ../cluster && terraform destroy
```

After destroying the cluster, delete the **forgeteam-tfstate-1771882722** bucket in GCP if no longer needed.

## Improvements: GCP, security, Terraform

Concrete next steps to harden the setup (by priority).

### GCP

| Improvement | Why | How |
|-------------|-----|-----|
| **Release channel** | Controlled, predictable upgrades for the control plane | In `modules/gke/main.tf`, add `release_channel { channel = "REGULAR" }` (or `RAPID` / `REGULAR`) to `google_container_cluster.main`. Autopilot defaults to REGULAR if omitted; setting it explicitly makes upgrades predictable. |
| **State bucket versioning** | Recover from accidental overwrites or deletes | Enable versioning on `forgeteam-tfstate-1771882722` in GCS (Console or `gsutil versioning set on gs://forgeteam-tfstate-1771882722`). |
| **State bucket uniform bucket-level access** | Simpler and safer IAM | Use uniform bucket-level access on the state bucket and grant minimal roles (e.g. `roles/storage.objectAdmin` or custom) only to identities that run Terraform. |
| **Separate project for state** | Blast-radius reduction | Optional: create a dedicated project (e.g. `forgeteam-tfstate`) and move the state bucket there; grant cross-project access from the app project. |

### Security (cluster and workloads)

| Improvement | Why | How |
|-------------|-----|-----|
| **Master authorized networks** | Restrict who can talk to the GKE API | In `modules/gke`, add `master_authorized_networks_config` to `google_container_cluster.main` with your office/CI IP ranges (or skip if you need open access). |
| **Workload Identity** | No long-lived keys; pods use GCP IAM | GKE Autopilot has Workload Identity on by default. Use it for apps that call GCP APIs: create a GCP SA, bind it to a K8s SA via workload identity, and use the K8s SA in pod specs. |
| **Network policies** | Limit pod-to-pod traffic by namespace/service | Repo already has `kustomize/components/network-policies`. Add that component to `kustomize/overlays/staging` and `overlays/production` so traffic is restricted (e.g. frontend → backend only). |
| **Resource quotas per namespace** | Avoid one env consuming all cluster resources | Add a `ResourceQuota` (and optionally `LimitRange`) in each overlay (staging/production) to cap CPU/memory per namespace. |
| **Private cluster / VPC** | No public IPs on nodes; egress control | For stricter networking, create a VPC and use a private GKE cluster (private endpoint, private nodes). Requires more Terraform (VPC, subnets, peering) and is a larger change. |

### Terraform

| Improvement | Why | How |
|-------------|-----|-----|
| **Pin provider versions** | Reproducible applies | In each env’s `providers.tf`, pin `version = "x.y.z"` for `hashicorp/google` (and any others) instead of `>= 5.0`. Align with `.terraform.lock.hcl` and commit the lock file. |
| **`terraform plan` in CI** | Catch drift and risky changes before apply | In GitHub Actions (or similar), run `terraform plan -out=tfplan` on PRs for cluster, staging, production and (optionally) post the plan as a comment. |
| **Backend state encryption** | Encrypt state at rest with a key you control | Create a Cloud KMS key and set `backend "gcs" { ... encryption_key = "projects/.../keyRings/.../cryptoKeys/..." }` for each env (or use a shared key). |
| **Avoid secrets in tfvars** | No secrets in repo or in state as plain text | Keep only non-sensitive vars in `terraform.tfvars.example`. For secrets, use env vars (`TF_VAR_...`), a secret manager (e.g. Google Secret Manager + external data source), or a separate secrets backend — and mark sensitive outputs as `sensitive = true` (already done for `cluster_endpoint`). |
| **`required_version` in modules** | Consistent Terraform version across team | Add `terraform { required_version = ">= 1.5" }` in `modules/gke` and `modules/app-deploy` so wrong Terraform version fails early. |

### Quick wins to do first

1. Enable **versioning** on the state bucket.
2. Add **network-policies** component to staging and production overlays.
3. Pin **provider versions** in `providers.tf` and keep `.terraform.lock.hcl` in git.
4. Add **release_channel** to the GKE cluster resource.

## Variables (forgeteam defaults)

- **cluster**: `project_id` (required), `name` (default `forgeteam-online-boutique`), `region`, `enable_apis`, `memorystore`
- **staging / production**: `project_id`, `tfstate_bucket` (default `forgeteam-tfstate-1771882722`), `use_remote_state` (default true). If `use_remote_state = false`, set `cluster_name` (e.g. `forgeteam-online-boutique`) and optionally `region`

## Manifests (Kustomize)

- Staging: `kustomize/overlays/staging` (namespace `staging`)
- Production: `kustomize/overlays/production` (namespace `production`)

Overlay path is passed into the `app-deploy` module; `kubectl apply -k` applies the generated manifests with the correct namespace.
