# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

data "aws_availability_zones" "available" {
  state = "available"
}

locals {
  tags           = var.tags
  azs            = slice(data.aws_availability_zones.available.names, 0, 2)
  public_subnets = [cidrsubnet(var.vpc_cidr, 4, 0), cidrsubnet(var.vpc_cidr, 4, 1)]
}

# VPC (public-only)
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name                    = var.name
  cidr                    = var.vpc_cidr
  azs                     = local.azs
  public_subnets          = local.public_subnets
  enable_nat_gateway      = false
  enable_dns_support      = true
  enable_dns_hostnames    = true
  map_public_ip_on_launch = true

  public_subnet_tags = {
    "kubernetes.io/cluster/${var.name}" = "owned"
    "kubernetes.io/role/elb"            = "1"
  }

  tags = local.tags
}

# EKS
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.13"

  cluster_name                   = var.name
  cluster_version                = var.cluster_version
  cluster_endpoint_public_access = true

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.public_subnets
  enable_cluster_creator_admin_permissions = false
  enable_irsa = true
  access_entries = {
    aldrin = {
      principal_arn = "arn:aws:iam::225989353426:user/Aldrin"
      policy_associations = [{
        policy_arn   = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"
        access_scope = { type = "cluster" }
      }]
    }
  }

  eks_managed_node_groups = {
    default = {
      instance_types = var.node_instance_types
      min_size       = var.min_size
      max_size       = var.max_size
      desired_size   = var.desired_size
      capacity_type  = var.capacity_type
      ami_type       = "AL2_x86_64"
      labels         = { role = "worker" }
      tags           = local.tags
    }
  }

  tags = local.tags
}

# IRSA for CloudWatch Observability add-on
locals {
  oidc_provider_url = replace(module.eks.oidc_provider, "https://", "")
}

data "aws_iam_policy_document" "cwagent_assume" {
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    effect  = "Allow"

    principals {
      type        = "Federated"
      identifiers = [module.eks.oidc_provider_arn]
    }

    condition {
      test     = "StringEquals"
      variable = "${local.oidc_provider_url}:sub"
      values   = ["system:serviceaccount:amazon-cloudwatch:cloudwatch-agent"]
    }

    condition {
      test     = "StringEquals"
      variable = "${local.oidc_provider_url}:aud"
      values   = ["sts.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "cwagent_irsa" {
  name               = "${var.name}-cloudwatch-agent-irsa"
  assume_role_policy = data.aws_iam_policy_document.cwagent_assume.json
  tags               = local.tags
}

resource "aws_iam_role_policy_attachment" "cwagent_server_policy" {
  role       = aws_iam_role.cwagent_irsa.name
  policy_arn = "arn:aws:iam::aws:policy/CloudWatchAgentServerPolicy"
}

# CloudWatch Observability EKS add-on
resource "aws_eks_addon" "cloudwatch_observability" {
  cluster_name             = module.eks.cluster_name
  addon_name               = "amazon-cloudwatch-observability"
  service_account_role_arn = aws_iam_role.cwagent_irsa.arn

  depends_on = [aws_iam_role_policy_attachment.cwagent_server_policy]
  tags       = local.tags
}

# Deploy Online Boutique via Terraform
data "http" "microservices_demo" {
  url = "https://raw.githubusercontent.com/GoogleCloudPlatform/microservices-demo/main/release/kubernetes-manifests.yaml"
}

data "kubectl_file_documents" "online_boutique" {
  content = data.http.microservices_demo.response_body
}

resource "kubectl_manifest" "online_boutique" {
  for_each          = data.kubectl_file_documents.online_boutique.manifests
  yaml_body         = each.value
  server_side_apply = true
  apply_only        = true
  force_conflicts   = true

  depends_on = [
    module.eks,
    aws_eks_addon.cloudwatch_observability
  ]
}

# Wait for ELB to publish DNS
resource "time_sleep" "lb_settle" {
  depends_on      = [kubectl_manifest.online_boutique]
  create_duration = "60s"
}

# Read the Service to output the URL
data "kubernetes_service" "frontend" {
  metadata {
    name      = "frontend-external"
    namespace = "default"
  }

  depends_on = [time_sleep.lb_settle]
}
