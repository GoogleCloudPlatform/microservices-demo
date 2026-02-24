variable "project_id" {
  type        = string
  description = "GCP project ID"
}

variable "name" {
  type        = string
  description = "Name of the GKE cluster"
  default     = "online-boutique"
}

variable "region" {
  type        = string
  description = "Region for the GKE cluster (Autopilot is regional)"
  default     = "us-central1"
}

variable "enable_apis" {
  type        = bool
  description = "Enable required Google APIs via Terraform (may be blocked by org policy)"
  default     = false
}

variable "memorystore" {
  type        = bool
  description = "Enable Redis API for optional Memorystore"
  default     = false
}
