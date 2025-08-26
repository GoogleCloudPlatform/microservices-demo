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

terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws        = { source = "hashicorp/aws", version = ">= 5.50" }
    kubernetes = { source = "hashicorp/kubernetes", version = ">= 2.29" }
    kubectl    = { source = "alekc/kubectl", version = "2.1.3" }
    http       = { source = "hashicorp/http", version = ">= 3.4.0" }
    time       = { source = "hashicorp/time", version = ">= 0.11.1" }
  }

  backend "s3" {
    bucket         = "tf-state-xebia-shared"
    key            = "online-boutique/aws-tf/terraform.tfstate"
    region         = "ap-south-1"
    dynamodb_table = "tf-locks-xebia-shared"
    encrypt        = true
  }
}

provider "aws" {
  region  = var.region
  profile = var.aws_profile
}

provider "kubernetes" {
  host                   = module.eks.cluster_endpoint
  cluster_ca_certificate = base64decode(module.eks.cluster_certificate_authority_data)

  exec {
    api_version = "client.authentication.k8s.io/v1beta1"
    command     = "aws"
    args = [
      "eks",
      "get-token",
      "--cluster-name",
      module.eks.cluster_name,
      "--region",
      var.region,
      "--profile",
      var.aws_profile
    ]
  }
}

data "aws_eks_cluster_auth" "this" {
  name = module.eks.cluster_name
}

provider "kubectl" {
  load_config_file = true
  config_path      = pathexpand("~/.kube/config")
  # pin the right context so TF doesn't pick docker-desktop, etc.
  config_context   = "arn:aws:eks:ap-south-1:225989353426:cluster/online-boutique"
}
