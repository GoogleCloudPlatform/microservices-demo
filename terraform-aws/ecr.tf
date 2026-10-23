locals {

  microservices = [
    "adservice",
    "cartservice",
    "checkoutservice",
    "currencyservice",
    "emailservice",
    "frontend",
    "paymentservice",
    "productcatalogservice",
    "recommendationservice",
    "shippingservice",
    "loadgenerator",
    "accountservice",
    "supportassistantservice",
    "frontend-web",
  ]
}

resource "aws_ecr_repository" "services" {
  for_each             = toset(local.microservices)
  name                 = "online-boutique/${each.value}"
  image_tag_mutability = "MUTABLE"

  force_delete = true
}

output "ecr_repository_urls" {
  value = { for k, v in aws_ecr_repository.services : k => v.repository_url }
}