# =============================================================================
# EKS Module
# Creates EKS cluster with managed Spot node groups, IRSA, and essential add-ons
# =============================================================================

# -----------------------------------------------------------------------------
# KMS Key for EKS Secrets Encryption
# -----------------------------------------------------------------------------
resource "aws_kms_key" "eks" {
  description             = "KMS key for EKS ${var.cluster_name} secrets encryption"
  deletion_window_in_days = 7
  enable_key_rotation     = true
}

resource "aws_kms_alias" "eks" {
  name          = "alias/${var.cluster_name}-eks-secrets"
  target_key_id = aws_kms_key.eks.key_id
}

# -----------------------------------------------------------------------------
# CloudWatch Log Group for EKS Control Plane
# -----------------------------------------------------------------------------

resource "aws_cloudwatch_log_group" "cluster" {
  name              = "/aws/eks/${var.cluster_name}/cluster"
  retention_in_days = 30
}

# NOTE: No custom security group is created here. EKS automatically creates a
# "cluster security group" that is attached to BOTH the control plane ENIs and
# the managed node group instances. It is exposed via the
# `cluster_primary_security_group_id` output and used by other modules
# (e.g. ElastiCache) to allow traffic from pods/nodes.

# -----------------------------------------------------------------------------
# EKS Cluster
# -----------------------------------------------------------------------------
resource "aws_eks_cluster" "main" {
  name     = var.cluster_name
  version  = var.cluster_version
  role_arn = aws_iam_role.cluster.arn

  vpc_config {
    subnet_ids              = var.private_subnet_ids
    endpoint_private_access = true
    endpoint_public_access  = var.endpoint_public_access
    public_access_cidrs     = var.public_access_cidrs
  }

  access_config {
    authentication_mode = "API"
  }

  encryption_config {
    resources = ["secrets"]
    provider {
      key_arn = aws_kms_key.eks.arn
    }
  }

  enabled_cluster_log_types = var.cluster_log_types

  depends_on = [
    aws_iam_role_policy_attachment.cluster_AmazonEKSClusterPolicy,
    aws_iam_role_policy_attachment.cluster_AmazonEKSVPCResourceController,
    aws_cloudwatch_log_group.cluster,
  ]

  # Clean up the orphaned CloudWatch log group after EKS cluster is fully deleted.
  # EKS may recreate it during cluster shutdown. This provisioner runs AFTER
  # the cluster is gone, catching any log group EKS recreated.
  provisioner "local-exec" {
    when       = destroy
    command    = "aws logs delete-log-group --log-group-name /aws/eks/${self.name}/cluster"
    on_failure = continue
  }

  tags = {
    Name = var.cluster_name
  }
}

# -----------------------------------------------------------------------------
# Launch Template for EKS Worker Nodes (Enables IMDSv2 Hop Limit = 2 for AWS LB Controller)
# -----------------------------------------------------------------------------
resource "aws_launch_template" "node" {
  name_prefix = "${var.cluster_name}-node-"

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 2
  }

  lifecycle {
    create_before_destroy = true
  }
}

# -----------------------------------------------------------------------------
# EKS Managed Node Group (Spot Instances)
# -----------------------------------------------------------------------------
resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.cluster_name}-main"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = var.private_subnet_ids
  ami_type        = var.node_ami_type
  instance_types  = var.node_instance_types
  capacity_type   = var.capacity_type
  disk_size       = var.node_disk_size

  launch_template {
    id      = aws_launch_template.node.id
    version = aws_launch_template.node.latest_version
  }

  scaling_config {
    desired_size = var.node_desired_size
    min_size     = var.node_min_size
    max_size     = var.node_max_size
  }

  update_config {
    max_unavailable = 1
  }

  labels = {
    role        = "general"
    environment = var.environment
  }

  depends_on = [
    aws_iam_role_policy_attachment.node_AmazonEKSWorkerNodePolicy,
    aws_iam_role_policy_attachment.node_AmazonEKS_CNI_Policy,
    aws_iam_role_policy_attachment.node_AmazonEC2ContainerRegistryReadOnly,
    # Nodes must launch after VPC CNI is configured with prefix delegation
    aws_eks_addon.vpc_cni,
    aws_eks_addon.kube_proxy,
  ]

  tags = {
    Name = "${var.cluster_name}-main-node-group"
  }

  lifecycle {
    ignore_changes = [scaling_config[0].desired_size]
  }
}
