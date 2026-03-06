# Role IAM pour le cluster EKS
resource "aws_iam_role" "eks_cluster" {
  name = "${var.project_name}-eks-cluster"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "eks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })

  tags = {
    Name = "${var.project_name}-eks-cluster"
  }
}

resource "aws_iam_role_policy_attachment" "eks_cluster" {
  role       = aws_iam_role.eks_cluster.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

# Role IAM pour les nodes (machines qui font tourner les pods)
resource "aws_iam_role" "eks_nodes" {
  name = "${var.project_name}-eks-nodes"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })

  tags = {
    Name = "${var.project_name}-eks-nodes"
  }
}

resource "aws_iam_role_policy_attachment" "nodes_worker" {
  role       = aws_iam_role.eks_nodes.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}

resource "aws_iam_role_policy_attachment" "nodes_cni" {
  role       = aws_iam_role.eks_nodes.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}

resource "aws_iam_role_policy_attachment" "nodes_ecr" {
  role       = aws_iam_role.eks_nodes.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

# --- IRSA : allow Kubernetes pods to assume specific IAM roles ---

# OIDC provider for EKS (links Kubernetes ServiceAccounts to IAM)
data "tls_certificate" "eks" {
  count = var.eks_oidc_issuer_url != "" ? 1 : 0
  url   = var.eks_oidc_issuer_url
}

resource "aws_iam_openid_connect_provider" "eks" {
  count           = var.eks_oidc_issuer_url != "" ? 1 : 0
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.eks[0].certificates[0].sha1_fingerprint]
  url             = var.eks_oidc_issuer_url

  tags = {
    Name = "${var.project_name}-eks-oidc"
  }
}

# IRSA role : allows cartservice pod to read Redis secret (least privilege)
resource "aws_iam_role" "cartservice" {
  count = var.eks_oidc_issuer_url != "" ? 1 : 0
  name  = "${var.project_name}-cartservice"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Federated = aws_iam_openid_connect_provider.eks[0].arn
      }
      Action = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringEquals = {
          "${replace(var.eks_oidc_issuer_url, "https://", "")}:sub" = "system:serviceaccount:default:cartservice"
        }
      }
    }]
  })

  tags = {
    Name = "${var.project_name}-cartservice-irsa"
  }
}

# Least-privilege policy : only read the Redis secret
resource "aws_iam_role_policy" "cartservice_secrets" {
  count = var.eks_oidc_issuer_url != "" ? 1 : 0
  name  = "read-redis-secret"
  role  = aws_iam_role.cartservice[0].id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = [var.redis_secret_arn]
    }]
  })
}
