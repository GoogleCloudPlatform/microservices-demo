output "workspace" {
  description = "Current Terraform workspace."
  value       = terraform.workspace
}

output "vpc_id" {
  description = "Created VPC ID."
  value       = module.vpc.vpc_id
}

output "private_subnet_ids" {
  description = "Private subnet IDs used by EKS."
  value       = module.vpc.private_subnet_ids
}

output "cluster_name" {
  description = "EKS cluster name."
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "EKS API server endpoint."
  value       = module.eks.cluster_endpoint
}

output "argocd_namespace" {
  description = "Namespace where Argo CD is installed."
  value       = var.enable_cluster_bootstrap ? kubernetes_namespace.argocd[0].metadata[0].name : null
}
