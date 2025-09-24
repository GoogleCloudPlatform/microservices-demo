# =========================
# VPC
# =========================
# Creamos una VPC con rango privado 10.0.0.0/16
# Habilitamos soporte DNS y hostnames para los recursos dentro de la VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = { Name = "online-boutique-vpc" }
}

# =========================
# Subredes públicas
# =========================
# Subred en AZ us-east-2a que asigna IP pública automáticamente
resource "aws_subnet" "public_az1" {
  vpc_id                 = aws_vpc.main.id
  cidr_block             = "10.0.1.0/24"
  availability_zone      = "us-east-2a"
  map_public_ip_on_launch = true
  tags = { Name = "online-boutique-public-subnet-az1" }
}

# Subred en AZ us-east-2b que asigna IP pública automáticamente
resource "aws_subnet" "public_az2" {
  vpc_id                 = aws_vpc.main.id
  cidr_block             = "10.0.3.0/24"
  availability_zone      = "us-east-2b"
  map_public_ip_on_launch = true
  tags = { Name = "online-boutique-public-subnet-az2" }
}

# =========================
# Subredes privadas
# =========================
# Subred privada en AZ us-east-2a
resource "aws_subnet" "private_az1" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.2.0/24"
  availability_zone = "us-east-2a"
  tags = { Name = "online-boutique-private-subnet-az1" }
}

# Subred privada en AZ us-east-2b
resource "aws_subnet" "private_az2" {
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.4.0/24"
  availability_zone = "us-east-2b"
  tags = { Name = "online-boutique-private-subnet-az2" }
}

# =========================
# IAM Role para EKS (Control Plane)
# =========================
# Rol que EKS usará para crear y administrar el clúster
resource "aws_iam_role" "eks_cluster_role" {
  name = "online-boutique-eks-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = { Service = "eks.amazonaws.com" }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Adjuntamos políticas necesarias al rol del clúster
resource "aws_iam_role_policy_attachment" "eks_cluster_AmazonEKSClusterPolicy" {
  role       = aws_iam_role.eks_cluster_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

resource "aws_iam_role_policy_attachment" "eks_cluster_AmazonEKSServicePolicy" {
  role       = aws_iam_role.eks_cluster_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSServicePolicy"
}

# =========================
# IAM Role para Node Group (Worker Nodes)
# =========================
# Rol que los nodos worker usarán para interactuar con AWS
resource "aws_iam_role" "eks_node_role" {
  name = "online-boutique-eks-node-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = { Service = "ec2.amazonaws.com" }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Adjuntamos políticas para nodos worker
resource "aws_iam_role_policy_attachment" "eks_node_AmazonEKSWorkerNodePolicy" {
  role       = aws_iam_role.eks_node_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
}

resource "aws_iam_role_policy_attachment" "eks_node_AmazonEKS_CNI_Policy" {
  role       = aws_iam_role.eks_node_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}

resource "aws_iam_role_policy_attachment" "eks_node_AmazonEC2ContainerRegistryReadOnly" {
  role       = aws_iam_role.eks_node_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

# =========================
# EKS Cluster
# =========================
# Creamos el clúster EKS usando el rol de control plane y las subredes definidas
resource "aws_eks_cluster" "main" {
  name     = "online-boutique-cluster"
  role_arn = aws_iam_role.eks_cluster_role.arn

  vpc_config {
    subnet_ids = [
      aws_subnet.public_az1.id,
      aws_subnet.public_az2.id,
      aws_subnet.private_az1.id,
      aws_subnet.private_az2.id
    ]
  }

  tags = { Name = "online-boutique-eks" }
}

# =========================
# Managed Node Group
# =========================
# Creamos nodos worker gestionados para ejecutar pods
resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "online-boutique-nodegroup"
  node_role_arn   = aws_iam_role.eks_node_role.arn

  # Nodos en subredes privadas
  subnet_ids      = [
    aws_subnet.private_az1.id,
    aws_subnet.private_az2.id
  ]

  # Configuración de escalado automático
  scaling_config {
    desired_size = 2
    max_size     = 3
    min_size     = 1
  }

  #instancia EC2 para los nodos
  instance_types = ["t3.medium"]

  tags = {
    Name = "online-boutique-nodegroup"
  }

  # Espera a que el clúster esté listo antes de crear nodos
  depends_on = [
    aws_eks_cluster.main
  ]
}

# =========================
# ECR Repository
# =========================
# Repositorio de imágenes Docker
resource "aws_ecr_repository" "app_repo" {
  name = "online-boutique"
  tags = { Name = "online-boutique-ecr" }
}
