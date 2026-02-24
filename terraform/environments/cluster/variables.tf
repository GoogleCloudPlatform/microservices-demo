variable "project_id" {
  type        = string
  description = "GCP project ID"
  default     = "forgeteam"
}

variable "name" {
  type        = string
  description = "GKE cluster name (forgeteam default: forgeteam-online-boutique)"
  default     = "forgeteam-online-boutique"
}

variable "region" {
  type        = string
  description = "Region for GKE Autopilot"
  default     = "us-central1"
}

variable "enable_apis" {
  type        = bool
  description = "Enable required GCP APIs (disable if org policy manages them)"
  default     = false
}

variable "memorystore" {
  type        = bool
  description = "Enable Redis API for Memorystore"
  default     = false
}
