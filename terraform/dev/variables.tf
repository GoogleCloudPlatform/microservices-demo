variable "project_id" {
  description = "Project id"
  type        = string
}

variable "region" {
  description = "Project region"
  type        = string
}

variable "zone" {
  description = "Project zone"
  type        = string
}

variable "network_name" {
  description = "Name of the vpc network"
  type        = string
}

variable "gke_subnet_name" {
  description = "Name of the gke subnet"
  type        = string
}

variable "gke_subnet_cidr_range" {
  description = "Cidr range for gke subnet"
  type        = string
}

variable "gke_subnet_cidr_range_pod" {
  description = "Cidr range for gke subnet pods"
  type        = string
}

variable "gke_subnet_cidr_range_services" {
  description = "Cidr range for gke subnet services"
  type        = string
}

variable "gke_cidr_range_master" {
  description = "Cidr range for gke subnet master ipv4"
  type        = string
}

variable "gke_name" {
  description = "Name for GKE cluster"
  type        = string
}

