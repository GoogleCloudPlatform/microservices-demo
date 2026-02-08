output "cluster_role_arn" {
  description = "ARN of the EKS cluster IAM role"
  value       = aws_iam_role.eks_cluster.arn
}

output "nodes_role_arn" {
  description = "ARN of the EKS nodes IAM role"
  value       = aws_iam_role.eks_nodes.arn
}
