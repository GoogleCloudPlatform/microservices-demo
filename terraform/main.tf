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

# Each of these 11 services needs its own container registry repository, so images get built, tagged, and pulled independently per service.

module "ecr" {
  source = "./modules/ecr"

  repository_names = [
    "adservice",
    "cartservice",
    "checkoutservice",
    "currencyservice",
    "emailservice",
    "frontend",
    "loadgenerator",
    "paymentservice",
    "productcatalogservice",
    "recommendationservice",
    "shippingservice",
    "shoppingassistantservice"
  ]

  tags = {
    Project     = "eks-microservices-platform"
    Environment = "portfolio"
    ManagedBy   = "terraform"
  }
}