module "vpc" {
  source = "./modules/vpc"

  project_name = "induwara-eks-platform"
  vpc_cidr     = "10.0.0.0/16"

  tags = {
    Project     = "eks-microservices-platform"
    Environment = "portfolio"
    ManagedBy   = "terraform"
  }
}