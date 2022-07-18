variable "gcp_project_id" {
  type        = string
  description = "The GCP project ID to apply this config to."
  default     = "<gcp-project-id>"    # Change this to your Google Cloud project ID
}

variable "apis" {
    description = "List of Google Cloud APIs to be enabled"
    type        = list(string)
    default = [
        "container.googleapis.com",
        "monitoring.googleapis.com",
        "cloudtrace.googleapis.com",
        "clouddebugger.googleapis.com",
        "cloudprofiler.googleapis.com"]
}

variable "name" {
    type        = string
    description = "Name of Cluster"
    default     = "online-boutique"
}

variable "region" {
    type        = string
    description = "Region of Cluster"
    default     = "us-central1"
}

variable "namespace" {
    type        = string
    description = "Namespace of the Pods"
    default     = "default"
}

variable "filepath_manifest" {
    type        = string
    description = "Filepath of kubernetes-manifests.yaml"
    default     = "../release/kubernetes-manifests.yaml"
}