# Deploying Online Boutique with the "Deploy to Cloud" workflow

This document explains how to use the GitHub Actions workflow at
[`../.github/workflows/deploy-to-cloud.yml`](../.github/workflows/deploy-to-cloud.yml)
to deploy Online Boutique to an existing Kubernetes cluster on Azure (AKS),
AWS (EKS), or GCP (GKE). The workflow is manually triggered
(`workflow_dispatch`) — it never runs automatically on push or pull request.

It applies the plain manifests in [`../kubernetes-manifests/`](../kubernetes-manifests/)
with `kubectl apply`. It does **not** use kustomize overlays, so this
`overlays/` folder is documentation-only for the workflow's purposes.

## Table of contents

1. [Activating the workflow on GitHub](#1-activating-the-workflow-on-github)
2. [One-time setup: repository secrets](#2-one-time-setup-repository-secrets)
3. [Running the workflow](#3-running-the-workflow)
4. [Deploying to Azure (AKS)](#4-deploying-to-azure-aks)
5. [Deploying to AWS (EKS)](#5-deploying-to-aws-eks)
6. [Deploying to GCP (GKE)](#6-deploying-to-gcp-gke)
7. [Input reference](#7-input-reference)
8. [Verifying the deployment](#8-verifying-the-deployment)
9. [Troubleshooting](#9-troubleshooting)

## 1. Activating the workflow on GitHub

The workflow file already lives in `.github/workflows/deploy-to-cloud.yml`,
which is the only location GitHub Actions scans for workflows, so it is
picked up automatically once the file is on the default branch (or any
branch you run it from). A few things to check the first time:

1. Push/merge this branch so `.github/workflows/deploy-to-cloud.yml` exists
   on GitHub.
2. Open the repository on GitHub and click the **Actions** tab.
3. If this repository was created by forking, GitHub disables workflows on
   forks by default. You will see a banner: *"Workflows aren't being run on
   this forked repository"*. Click **"I understand my workflows, go ahead
   and enable them"** to turn them on.
4. If Actions are disabled at the repository level, go to
   **Settings → Actions → General → Actions permissions** and select
   **"Allow all actions and reusable workflows"** (or your organization's
   equivalent policy), then **Save**.
5. Back in the **Actions** tab, you should now see **"Deploy to Cloud"**
   listed in the left-hand sidebar of workflows. If it doesn't appear,
   refresh the page — GitHub indexes new workflow files within a few
   seconds of the push.

## 2. One-time setup: repository secrets

The workflow authenticates to each cloud using repository secrets. Add
these under **Settings → Secrets and variables → Actions → New repository
secret**. You only need to add the secrets for the cloud(s) you intend to
deploy to.

| Secret name | Cloud | What it is |
|---|---|---|
| `AZURE_CREDENTIALS` | Azure | JSON output of an `az ad sp create-for-rbac --sdk-auth` service principal |
| `AWS_ACCESS_KEY_ID` | AWS | Access key ID of an IAM user/role with EKS access |
| `AWS_SECRET_ACCESS_KEY` | AWS | Secret access key matching the access key ID above |
| `GCP_SA_KEY` | GCP | JSON key of a service account with GKE access |

Commands to generate each credential are in the cloud-specific sections
below.

## 3. Running the workflow

1. Go to the **Actions** tab.
2. Click **"Deploy to Cloud"** in the left sidebar.
3. Click the **"Run workflow"** dropdown button on the right.
4. Choose the branch that contains the workflow (usually `main`).
5. Fill in the inputs:
   - `cloud_provider`: choose `azure`, `aws`, or `gcp` from the dropdown.
   - `cluster_name`: the name of your existing cluster.
   - `namespace`: optional, defaults to `default`. The workflow creates
     the namespace automatically if it doesn't exist yet.
   - Fill in **only the fields relevant to the cloud you picked** (see the
     sections below). Leave the others blank — GitHub Actions doesn't
     support showing/hiding inputs based on another input, so all fields
     are listed together regardless of the chosen cloud.
6. Click the green **"Run workflow"** button.
7. Click into the new run to watch progress. The `validate-inputs` job
   fails immediately with a clear message if a required field for your
   chosen cloud was left blank, before anything touches the cluster.

## 4. Deploying to Azure (AKS)

### Prerequisites

- An existing AKS cluster.
- A service principal with permission to fetch cluster credentials
  (`Azure Kubernetes Service Cluster User Role` at minimum) and, if the
  cluster uses Azure RBAC for Kubernetes authorization, a role such as
  `Azure Kubernetes Service RBAC Cluster Admin` scoped to the cluster.

Create the service principal and capture the JSON for the
`AZURE_CREDENTIALS` secret:

```bash
az ad sp create-for-rbac --sdk-auth --role contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP>
```

Paste the entire JSON output as the value of the `AZURE_CREDENTIALS`
secret.

### Inputs to fill in

| Input | Value |
|---|---|
| `cloud_provider` | `azure` |
| `cluster_name` | Name of the AKS cluster |
| `azure_resource_group` | Resource group containing the cluster (**required**) |
| `azure_subscription_id` | Optional — only needed if the service principal has access to multiple subscriptions and you want to target a specific one |
| `namespace` | Optional, defaults to `default` |

## 5. Deploying to AWS (EKS)

### Prerequisites

- An existing EKS cluster.
- An IAM user (or role) whose access key/secret you'll store as secrets,
  with `eks:DescribeCluster` permission, and mapped to a Kubernetes RBAC
  identity inside the cluster (via the `aws-auth` ConfigMap, or EKS access
  entries) with enough permissions to apply Deployments and Services —
  `system:masters` is the simplest option for a demo cluster.

Create an access key for that IAM user (from the AWS Console: **IAM → Users
→ your user → Security credentials → Create access key**), then store the
key ID and secret as the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
secrets.

### Inputs to fill in

| Input | Value |
|---|---|
| `cloud_provider` | `aws` |
| `cluster_name` | Name of the EKS cluster |
| `aws_region` | AWS region the cluster is in, e.g. `us-east-1` (**required**) |
| `namespace` | Optional, defaults to `default` |

## 6. Deploying to GCP (GKE)

### Prerequisites

- An existing GKE cluster.
- A service account with `roles/container.developer` (or higher) on the
  project.

Create the service account key:

```bash
gcloud iam service-accounts create gh-actions-deployer \
  --display-name "GitHub Actions - Online Boutique deployer"

gcloud projects add-iam-policy-binding <PROJECT_ID> \
  --member "serviceAccount:gh-actions-deployer@<PROJECT_ID>.iam.gserviceaccount.com" \
  --role "roles/container.developer"

gcloud iam service-accounts keys create key.json \
  --iam-account "gh-actions-deployer@<PROJECT_ID>.iam.gserviceaccount.com"
```

Paste the contents of `key.json` as the value of the `GCP_SA_KEY` secret,
then delete the local `key.json` file.

### Inputs to fill in

| Input | Value |
|---|---|
| `cloud_provider` | `gcp` |
| `cluster_name` | Name of the GKE cluster |
| `gcp_project_id` | Project ID containing the cluster (**required**) |
| `gcp_location` | Cluster's zone (e.g. `us-central1-a`) or region (e.g. `us-central1`) (**required**) |
| `gcp_location_type` | `zone` or `region`, matching `gcp_location` above. Defaults to `zone` |
| `namespace` | Optional, defaults to `default` |

## 7. Input reference

| Input | Required | Applies to | Notes |
|---|---|---|---|
| `cloud_provider` | Always | all | `azure`, `aws`, or `gcp` |
| `cluster_name` | Always | all | Name of the target cluster |
| `namespace` | No | all | Defaults to `default`; created automatically |
| `azure_resource_group` | If `cloud_provider=azure` | Azure | Resource group of the AKS cluster |
| `azure_subscription_id` | No | Azure | Overrides the subscription in `AZURE_CREDENTIALS` |
| `aws_region` | If `cloud_provider=aws` | AWS | Region of the EKS cluster |
| `gcp_project_id` | If `cloud_provider=gcp` | GCP | Project ID of the GKE cluster |
| `gcp_location` | If `cloud_provider=gcp` | GCP | Zone or region of the GKE cluster |
| `gcp_location_type` | No | GCP | `zone` (default) or `region` |

## 8. Verifying the deployment

The workflow's final steps do this for you, but if you want to check
manually after it finishes, point `kubectl` at the same cluster (using
the same `az aks get-credentials` / `aws eks update-kubeconfig` /
`gcloud container clusters get-credentials` command shown in the run log)
and run:

```bash
kubectl get pods -n <namespace>
kubectl get service frontend-external -n <namespace>
```

`frontend-external` is a `LoadBalancer` Service. The external IP can take
a minute or two to be assigned on a fresh cluster — if it shows
`<pending>`, wait and re-run the `get service` command. Once an IP is
assigned, the storefront is reachable at `http://<EXTERNAL-IP>`.

## 9. Troubleshooting

**"Deploy to Cloud" doesn't appear in the Actions tab.**
Confirm the workflow file is on the branch you're looking at and that
Actions are enabled (see [section 1](#1-activating-the-workflow-on-github)).

**`validate-inputs` fails with "Missing required input(s)".**
You left a field blank that's required for the cloud you selected — see
the [input reference](#7-input-reference) or the cloud-specific section
above.

**Login/authentication step fails.**
The corresponding secret (`AZURE_CREDENTIALS`, `AWS_ACCESS_KEY_ID` /
`AWS_SECRET_ACCESS_KEY`, or `GCP_SA_KEY`) is missing, malformed, or
expired. Re-generate it using the commands in the cloud-specific section
and update the repository secret.

**`az aks get-credentials` / `aws eks update-kubeconfig` /
`gcloud container clusters get-credentials` succeeds but `kubectl apply`
fails with a permissions/forbidden error.**
The identity used to log in can reach the cluster's control plane but
isn't authorized inside the cluster's RBAC. Grant it a Kubernetes RBAC
role (see the prerequisites in each cloud-specific section above).

**Re-deploying after a change.**
Just run the workflow again with the same inputs. `kubectl apply` is
idempotent, so it updates existing resources rather than duplicating
them.
