variable "app_name" {
  default = "onlineboutique"
  description = "Application name"
}

variable "project_id" {
  description = "GCP project id"
}

variable "region" {
  description = "GCP region"
}

variable "machine_type" {
    default   = "e2-standard-2"
    description = "Machine type for GKE cluster nodes"
}

variable "preemptible" {
  default     = true
  description = "Preemptible VMs are cheaper however they might be stopped"
}

variable "min_node_count" {
  default     = 1
  description = "Minimum number of GKE nodes per zone"
}

variable "max_node_count" {
  default     = 2
  description = "Maximum number of GKE nodes per zone"
}

variable "gke_nodes_cidr" {
  default = "10.0.0.0/16"
  description = "CIDR range for the GKE Nodes subnet"
}

variable "gke_pods_cidr" {
  default = "10.1.0.0/16"
  description = "CIDR range for the GKE Pods subnet"
}

variable "gke_services_cidr" {
  default = "10.2.0.0/16"
  description = "CIDR range for the GKE Services subnet"
}