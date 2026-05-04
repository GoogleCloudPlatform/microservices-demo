data "google_project" "project" {}

locals {
  # Autopilot pulls images using the cluster's node SA. Unless overridden it
  # is the project's compute default SA: <project_number>-compute@developer.gserviceaccount.com.
  gke_pull_sa = coalesce(
    var.gke_node_service_account,
    "${data.google_project.project.number}-compute@developer.gserviceaccount.com"
  )
}

# ---- Artifact Registry: training images ---------------------------------

resource "google_artifact_registry_repository" "training" {
  location      = var.region
  repository_id = "microservices-demo-training"
  description   = "Training images for microservices-demo. :base = upstream copy, :attendee-<name>-<sha> = per-attendee fix."
  format        = "DOCKER"

  cleanup_policy_dry_run = false

  cleanup_policies {
    id     = "delete-untagged-after-1d"
    action = "DELETE"
    condition {
      tag_state  = "UNTAGGED"
      older_than = "86400s"
    }
  }

  cleanup_policies {
    id     = "delete-attendee-tags-after-7d"
    action = "DELETE"
    condition {
      tag_state    = "TAGGED"
      tag_prefixes = ["attendee-"]
      older_than   = "604800s"
    }
  }

  cleanup_policies {
    id     = "keep-base"
    action = "KEEP"
    condition {
      tag_state    = "TAGGED"
      tag_prefixes = ["base"]
    }
  }
}

# Cluster nodes need to pull from the repo.
resource "google_artifact_registry_repository_iam_member" "gke_pull" {
  location   = google_artifact_registry_repository.training.location
  repository = google_artifact_registry_repository.training.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${local.gke_pull_sa}"
}

# ---- Workload Identity Federation for GitHub Actions --------------------

resource "google_iam_workload_identity_pool" "github" {
  workload_identity_pool_id = "github-training"
  display_name              = "GitHub Actions (training)"
  description               = "OIDC pool for the microservices-demo training repo CI."
}

resource "google_iam_workload_identity_pool_provider" "github" {
  workload_identity_pool_id          = google_iam_workload_identity_pool.github.workload_identity_pool_id
  workload_identity_pool_provider_id = "github"
  display_name                       = "GitHub OIDC"

  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }

  attribute_mapping = {
    "google.subject"       = "assertion.sub"
    "attribute.actor"      = "assertion.actor"
    "attribute.repository" = "assertion.repository"
    "attribute.ref"        = "assertion.ref"
  }

  # Restrict the provider to our specific repo. Without this any GitHub repo
  # can mint tokens against our pool.
  attribute_condition = "assertion.repository == \"${var.github_repo}\""
}

# Service account that GH Actions impersonates. It only has push rights to the
# training repo - no other project-wide perms.
resource "google_service_account" "github_pusher" {
  account_id   = "training-image-pusher"
  display_name = "Microservices-demo training image pusher"
  description  = "Used by GitHub Actions in ${var.github_repo} to push images to the training Artifact Registry."
}

resource "google_artifact_registry_repository_iam_member" "github_push" {
  location   = google_artifact_registry_repository.training.location
  repository = google_artifact_registry_repository.training.name
  role       = "roles/artifactregistry.writer"
  member     = "serviceAccount:${google_service_account.github_pusher.email}"
}

# Lets the workflow run get-gke-credentials and helm-upgrade against the
# training cluster. Project-wide scope is broader than necessary; refine
# with RBAC later if upstreaming.
resource "google_project_iam_member" "github_gke_developer" {
  project = var.project_id
  role    = "roles/container.developer"
  member  = "serviceAccount:${google_service_account.github_pusher.email}"
}

# Allow the GitHub repo's tokens (any branch) to impersonate the SA.
resource "google_service_account_iam_member" "github_wif_binding" {
  service_account_id = google_service_account.github_pusher.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github.name}/attribute.repository/${var.github_repo}"
}
