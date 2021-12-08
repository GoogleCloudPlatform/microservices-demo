terraform {
  required_providers {
    google = {
      version = "~> 3.89"
    }

    google-beta = {
      version = "~> 3.89"
    }
  }

  required_version = "= 1.0.6"
}

provider "google" {
  credentials = file(var.path_cred)
  project     = var.project_id
  region      = var.region
}

provider "google-beta" {
  credentials = file(var.path_cred)
  project     = var.project_id
  region      = var.region
}
