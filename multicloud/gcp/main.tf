# main.tf - Shared Terraform configuration for GCP services

terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 4.50.0"
    }
  }
}

variable "project_id" {
  description = "The GCP project ID where resources will be created"
  type        = string
}

variable "peering_project_id" {
  description = "GCP project with remote network you want to peer with"
  type = string
}

variable "peering_vpc_network" {
  description = "Valid name of VPC network in remote project"
  type = string
}

provider "google" {
  project = var.project_id
  region  = "us-central1"
} 