provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project   = "Online-Boutique-DevOps"
      ManagedBy = "Terraform"
      Team      = "Giovanna-Leonardo"
    }
  }
}
