variable "project_id" {
  type        = string
  description = "GCP project ID"
}

variable "cluster_name" {
  type        = string
  description = "Name of the existing GKE cluster"
}

variable "region" {
  type        = string
  description = "Region of the GKE cluster"
}

variable "namespace" {
  type        = string
  description = "Kubernetes namespace to deploy into"
}

variable "filepath_manifest" {
  type        = string
  description = "Path to kustomize overlay dir relative to repo_root (e.g. kustomize/overlays/staging)"
}

variable "repo_root" {
  type        = string
  description = "Absolute path to repo root (where kustomize overlays live)"
}
