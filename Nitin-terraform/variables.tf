variable "project_id" {
  description = "GCP project ID"
}

variable "region" {
  description = "The region for the GKE cluster"
  default     = "asia-south1-a"  # You can change this to your desired region
}

