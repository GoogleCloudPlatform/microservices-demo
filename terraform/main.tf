resource "aws_iam_role" "eks_cluster" {
  name = "eks_cluster"

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "eks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "eks_cluster-AmazonEKSClusterPolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks_cluster.name
}

resource "aws_iam_role_policy_attachment" "eks_cluster-AmazonEKSServicePolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSServicePolicy"
  role       = aws_iam_role.eks_cluster.name
}

resource "aws_security_group" "eks_worker_group" {
  name_prefix = "eks-worker-group-"
  vpc_id      = aws_vpc.project-vpc.id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "project_cluster"
  }
}
resource "aws_security_group" "eks_cluster" {
  name        = "eks_cluster-sg"
  description = "Cluster communication with worker nodes"
  vpc_id      = aws_vpc.project-vpc.id
}

locals {
  workstation-external-cidr = "0.0.0.0/32" 
}

resource "aws_security_group_rule" "project_cluster-ingress-workstation-https" {
  cidr_blocks       = [local.workstation-external-cidr]
  description       = "Allow workstation to communicate with the cluster API Server"
  from_port         = 443
  protocol          = "tcp"
  security_group_id = aws_security_group.eks_cluster.id
  to_port           = 443
  type              = "ingress"
}

resource "aws_eks_cluster" "eks_cluster" {
  name     = var.cluster-name
  role_arn = aws_iam_role.eks_cluster.arn

  vpc_config {
    security_group_ids = [aws_security_group.eks_cluster.id]
    subnet_ids = aws_subnet.project-vpc[*].id
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster-AmazonEKSClusterPolicy,
    aws_iam_role_policy_attachment.eks_cluster-AmazonEKSServicePolicy,
  ]
}

resource "aws_iam_policy_attachment" "eks_cluster" {
  name       = "eks-cluster-attach"
  roles      = [aws_iam_role.eks_cluster.name]
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

resource "aws_subnet" "private" {
  count = 2
  
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a" 
  map_public_ip_on_launch = false
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

variable "microservices" {
  type = list(object({
    name  = string
    image = string
    replicas = number
  }))
  default = [
    {
      name     = "adservice"
      image    = "thecodegirl/adservice:latest"
      replicas = 2
    },
    {
      name     = "cartservice"
      image    = "thecodegirl/cartservice:latest"
      replicas = 2
    },
    {
      name     = "checkoutservice"
      image    = "thecodegirl/checkoutservice:latest"
      replicas = 2
    },
    {
      name     = "currencyservice"
      image    = "thecodegirl/currencyservice:latest"
      replicas = 2
    },
    {
      name     = "emailservice"
      image    = "thecodegirl/emailservice:latest"
      replicas = 2
    },
    {
      name     = "frontend"
      image    = "thecodegirl/frontend:latest"
      replicas = 2
    },
    {
      name     = "loadgenerator"
      image    = "thecodegirl/loadgenerator:latest"
      replicas = 2
    },
    {
      name     = "paymentservice"
      image    = "thecodegirl/paymentservice:latest"
      replicas = 2
    },
    {
      name     = "productcatalogservice"
      image    = "thecodegirl/productcatalogservice:latest"
      replicas = 2
    },
    {
      name     = "recommendationservice"
      image    = "thecodegirl/recommendationservice:latest"
      replicas = 2
    },
    {
      name     = "shippingservice"
      image    = "thecodegirl/shippingservice:latest"
      replicas = 2
    },
  ]
}

resource "kubernetes_namespace" "microservices" {
  metadata {
    name = "microservices"
  }
}

resource "kubernetes_deployment" "microservices" {
  count = length(var.microservices)

  metadata {
    name      = var.microservices[count.index].name
    namespace = kubernetes_namespace.microservices.metadata.0.name
  }

  spec {
    replicas = var.microservices[count.index].replicas

    selector {
      match_labels = {
        app = var.microservices[count.index].name
      }
    }

    template {
      metadata {
        labels = {
          app = var.microservices[count.index].name
        }
      }

      spec {
        container {
          image = var.microservices[count.index].image
          name  = var.microservices[count.index].name  
        }
      }
    }
  }
}