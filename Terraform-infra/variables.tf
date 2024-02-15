variable "project" {
  description = "Project"
  default = "alien-segment-410723"
}

variable "region" {
  description = "us-east4"
  default     = "us-east4"
}

variable "zones" {
  description = "List of GCP zones for the resources"
  default     = ["us-east4-a", "us-east4-b", "us-east4-c"]
}

variable "network_name" {
  description = "Name of the VPC network" 
  default     = "microservices-vpc"
}

variable "subnet_cidr" {
  description = "CIDR block for subnets"
  default     = "10.0.0.0/16"
}

variable "dev_subnet_name" {
  description = "Name of the development subnet"
  default     = "dev-subnet"
}

variable "prod_subnet_name" {
  description = "Name of the production subnet"
  default     = "prod-subnet"
}

variable "gke_cluster_name" {
  description = "Name of the GKE cluster"
  default     = "microservices-cluster"
}

variable "artifact_registry_repo_name" {
  description = "Name of the Artifact Registry"
  default     = "microservices-demo-final"
}
