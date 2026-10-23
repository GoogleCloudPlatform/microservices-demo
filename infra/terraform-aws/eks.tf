# Localiza automáticamente los roles creados por AWS Learner Lab.
data "aws_iam_roles" "eks_cluster" {
  name_regex = ".*LabEksClusterRole.*"
}

data "aws_iam_roles" "eks_nodes" {
  name_regex = ".*LabEksNodeRole.*"
}

locals {
  eks_cluster_role_arn = one(data.aws_iam_roles.eks_cluster.arns)
  eks_node_role_arn    = one(data.aws_iam_roles.eks_nodes.arns)
  kubernetes_version   = "1.35"
}

# Crea el clúster administrado de Kubernetes.
resource "aws_eks_cluster" "main" {
  name     = var.cluster_name
  role_arn = local.eks_cluster_role_arn
  version  = local.kubernetes_version

  access_config {
    authentication_mode                         = "API_AND_CONFIG_MAP"
    bootstrap_cluster_creator_admin_permissions = true
  }

  vpc_config {
    subnet_ids = [
      aws_subnet.public_a.id,
      aws_subnet.public_b.id
    ]

    endpoint_private_access = true
    endpoint_public_access  = true
  }

  upgrade_policy {
    support_type = "STANDARD"
  }

  depends_on = [
    aws_route_table_association.public_a,
    aws_route_table_association.public_b
  ]

  tags = {
    Name = var.cluster_name
  }
}

# Crea las máquinas EC2 donde se ejecutarán los contenedores.
resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.cluster_name}-nodes"
  node_role_arn   = local.eks_node_role_arn
  version         = local.kubernetes_version

  subnet_ids = [
    aws_subnet.public_a.id,
    aws_subnet.public_b.id
  ]

  ami_type       = "AL2023_x86_64_STANDARD"
  instance_types = ["t3.medium"]
  capacity_type  = "ON_DEMAND"
  disk_size      = 20

  scaling_config {
    desired_size = 2
    min_size     = 1
    max_size     = 3
  }

  update_config {
    max_unavailable = 1
  }

  depends_on = [
    aws_eks_cluster.main
  ]

  tags = {
    Name = "${var.cluster_name}-nodes"
  }
}