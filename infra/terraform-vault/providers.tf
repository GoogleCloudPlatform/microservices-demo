provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project   = "Online-Boutique-DevOps"
      Phase     = "Fase-3"
      ManagedBy = "Terraform"
      Team      = "Giovanna-Leonardo"
    }
  }
}
