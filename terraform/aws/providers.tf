terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.4"
    }
  }

  # El bucket se pasa en tiempo de "terraform init" (no se puede usar una
  # variable aquí), por eso queda vacío. Ver README.md de esta carpeta.
  backend "s3" {
    key = "modulo-catalogo/terraform.tfstate"
  }
}

provider "aws" {
  region = var.region
}
