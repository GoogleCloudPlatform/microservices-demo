variable "project_id" {
  description = "GCP project ID hosting the training cluster and registry."
  type        = string
}

variable "region" {
  description = "Region for the Artifact Registry repo. Should match the GKE cluster region for free in-region pulls."
  type        = string
  default     = "europe-west1"
}

variable "github_repo" {
  description = "GitHub repo allowed to push images via Workload Identity Federation, in 'owner/name' form."
  type        = string
  default     = "re-cinq/microservices-demo"
}

variable "gke_node_service_account" {
  description = "Email of the service account used by GKE Autopilot nodes (for image pulls). Defaults to the project's compute default SA, which is what Autopilot uses unless overridden."
  type        = string
  default     = ""
}
