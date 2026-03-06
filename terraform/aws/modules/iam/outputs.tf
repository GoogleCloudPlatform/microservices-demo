output "cluster_role_arn" {
  description = "ARN of the EKS cluster IAM role"
  value       = aws_iam_role.eks_cluster.arn
}

output "nodes_role_arn" {
  description = "ARN of the EKS nodes IAM role"
  value       = aws_iam_role.eks_nodes.arn
}

output "oidc_provider_arn" {
  description = "ARN of the EKS OIDC provider"
  value       = length(aws_iam_openid_connect_provider.eks) > 0 ? aws_iam_openid_connect_provider.eks[0].arn : ""
}

output "cartservice_role_arn" {
  description = "ARN of the cartservice IRSA role"
  value       = length(aws_iam_role.cartservice) > 0 ? aws_iam_role.cartservice[0].arn : ""
}
