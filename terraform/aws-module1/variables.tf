variable "project_name" {
  description = "Project identifier used for naming AWS resources."
  type        = string
  default     = "blackfriday-survival"
}

variable "name_suffix" {
  description = "Suffix appended to AWS resource names."
  type        = string
  default     = "MAH-groupe1"
}

variable "aws_region" {
  description = "AWS region where resources are created."
  type        = string
  default     = "eu-west-3"
}

variable "vpc_cidr" {
  description = "CIDR for the VPC."
  type        = string
  default     = "10.40.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "Public subnet CIDRs mapped to each AZ."
  type        = list(string)
  default     = ["10.40.0.0/20", "10.40.16.0/20", "10.40.32.0/20"]

  validation {
    condition     = length(var.public_subnet_cidrs) == 3
    error_message = "public_subnet_cidrs must contain exactly 3 CIDRs (one per AZ)."
  }
}

variable "private_subnet_cidrs" {
  description = "Private subnet CIDRs mapped to each AZ."
  type        = list(string)
  default     = ["10.40.64.0/20", "10.40.80.0/20", "10.40.96.0/20"]

  validation {
    condition     = length(var.private_subnet_cidrs) == 3
    error_message = "private_subnet_cidrs must contain exactly 3 CIDRs (one per AZ)."
  }
}

variable "cluster_version" {
  description = "EKS Kubernetes version."
  type        = string
  default     = "1.31"
}

variable "node_instance_types" {
  description = "EC2 instance types for EKS managed nodes."
  type        = list(string)
  default     = ["m6i.large"]
}

variable "node_group_min_size" {
  description = "Minimum desired node count."
  type        = number
  default     = 3
}

variable "node_group_max_size" {
  description = "Maximum desired node count."
  type        = number
  default     = 12
}

variable "node_group_desired_size" {
  description = "Desired node count on creation."
  type        = number
  default     = 3
}

variable "argocd_chart_version" {
  description = "Argo CD helm chart version."
  type        = string
  default     = "7.8.2"
}

variable "enable_cluster_bootstrap" {
  description = "If true, apply Kubernetes namespaces/RBAC and Helm releases after EKS is available."
  type        = bool
  default     = false
}

variable "tags" {
  description = "Additional tags applied to AWS resources."
  type        = map(string)
  default = {
    Owner = "mt5-team"
  }
}
