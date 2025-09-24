# Configuración principal de Terraform
terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.12"
    }
  }
}

# Configura el proveedor AWS
provider "aws" {
  region = var.aws_region  
}

