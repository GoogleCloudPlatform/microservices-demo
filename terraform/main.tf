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

#IAM roles for the EKS cluster and its node groups. The cluster role is assumed by the EKS service, while the node role is assumed by EC2 instances in the node group. Each role has the necessary policies attached to allow proper operation of the EKS cluster and its nodes.

module "iam" {
  source = "./modules/iam"

  cluster_name = "induwara-eks-platform"

  tags = {
    Project     = "eks-microservices-platform"
    Environment = "portfolio"
    ManagedBy   = "terraform"
  }
}