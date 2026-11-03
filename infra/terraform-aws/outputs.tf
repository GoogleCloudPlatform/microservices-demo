output "aws_region" {
  description = "Región utilizada para la infraestructura"
  value       = var.aws_region
}

output "ecr_repository_name" {
  description = "Nombre del repositorio de imágenes"
  value       = aws_ecr_repository.frontend.name
}

output "ecr_repository_url" {
  description = "Dirección del repositorio ECR"
  value       = aws_ecr_repository.frontend.repository_url
}
output "eks_cluster_name" {
  description = "Nombre del cluster EKS"
  value       = aws_eks_cluster.main.name
}

output "eks_cluster_endpoint" {
  description = "Direccion del cluster EKS"
  value       = aws_eks_cluster.main.endpoint
}

output "vpc_id" {
  description = "Identificador de la VPC"
  value       = aws_vpc.eks.id
}

output "public_subnet_ids" {
  description = "Identificadores de las subredes publicas"
  value = [
    aws_subnet.public_a.id,
    aws_subnet.public_b.id
  ]
}
