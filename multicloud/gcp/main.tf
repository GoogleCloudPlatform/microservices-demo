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

provider "google" {
  project = var.project_id
  region  = "us-central1"
} 