# Muestra el endpoint del clúster EKS al finalizar la ejecución de Terraform
output "cluster_endpoint" {
  description = "EKS cluster endpoint"  
  value       = aws_eks_cluster.main.endpoint  
}


# Muestra el nombre del clúster EKS
output "cluster_name" {
  description = "EKS cluster name"  
  value       = aws_eks_cluster.main.name  
}


# Muestra la URL del repositorio de contenedores en Amazon ECR
output "ecr_repository_url" {
  description = "ECR repository URL"  
  value       = aws_ecr_repository.app_repo.repository_url  
}

