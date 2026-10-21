# Consulta el rol proporcionado por AWS Learner Lab.
data "aws_iam_role" "lab_role" {
  name = "LabRole"
}

# Crea el clúster administrado de Kubernetes.
resource "aws_eks_cluster" "main" {
  name     = var.cluster_name
  role_arn = data.aws_iam_role.lab_role.arn

  access_config {
    authentication_mode                         = "API_AND_CONFIG_MAP"
    bootstrap_cluster_creator_admin_permissions = true
  }

  vpc_config {
    subnet_ids = [
      aws_subnet.public_a.id,
      aws_subnet.public_b.id
    ]

    endpoint_private_access = false
    endpoint_public_access  = true
  }

  depends_on = [
    aws_route_table_association.public_a,
    aws_route_table_association.public_b
  ]

  tags = {
    Name = var.cluster_name
  }
}
# Grupo de máquinas EC2 donde se ejecutarán los contenedores.
resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.cluster_name}-nodes"
  node_role_arn   = data.aws_iam_role.lab_role.arn

  subnet_ids = [
    aws_subnet.public_a.id,
    aws_subnet.public_b.id
  ]

  instance_types = ["t3.medium"]
  capacity_type  = "ON_DEMAND"
  disk_size      = 20

  scaling_config {
    desired_size = 2
    min_size     = 1
    max_size     = 2
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
