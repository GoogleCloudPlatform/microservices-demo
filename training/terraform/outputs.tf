output "artifact_registry_repo" {
  description = "Full path of the training Artifact Registry repo."
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.training.repository_id}"
}

output "github_pusher_sa_email" {
  description = "Email of the SA that GitHub Actions impersonates. Use in the workflow's google-github-actions/auth@v2 step."
  value       = google_service_account.github_pusher.email
}

output "workload_identity_provider" {
  description = "Full resource name of the WIF provider, for google-github-actions/auth@v2."
  value       = google_iam_workload_identity_pool_provider.github.name
}
