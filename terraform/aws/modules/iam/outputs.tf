output "cluster_role_arn" {
  value = aws_iam_role.eks_cluster.arn
}

output "nodes_role_arn" {
  value = aws_iam_role.eks_nodes.arn
}
