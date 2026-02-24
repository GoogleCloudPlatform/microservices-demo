variable "project_id" {
  type        = string
  description = "GCP project ID (must match cluster)"
  default     = "forgeteam"
}

variable "tfstate_bucket" {
  type        = string
  description = "GCS bucket holding cluster state (forgeteam: forgeteam-tfstate-1771882722)"
  default     = "forgeteam-tfstate-1771882722"
}

variable "region" {
  type        = string
  description = "Region (must match cluster)"
  default     = "us-central1"
}

variable "cluster_name" {
  type        = string
  description = "GKE cluster name (from cluster env output). Optional if using remote state."
  default     = ""
}

variable "use_remote_state" {
  type        = bool
  description = "Read cluster_name/region from cluster Terraform state"
  default     = true
}
