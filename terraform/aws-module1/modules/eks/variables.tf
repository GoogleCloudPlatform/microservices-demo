variable "cluster_name" {
  description = "EKS cluster name."
  type        = string
}

variable "cluster_version" {
  description = "EKS cluster version."
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs where EKS nodes run."
  type        = list(string)
}

variable "vpc_id" {
  description = "VPC ID for EKS."
  type        = string
}

variable "node_instance_types" {
  description = "Node instance types."
  type        = list(string)
}

variable "node_group_min_size" {
  description = "Minimum node count."
  type        = number
}

variable "node_group_max_size" {
  description = "Maximum node count."
  type        = number
}

variable "node_group_desired_size" {
  description = "Desired node count."
  type        = number
}

variable "tags" {
  description = "Tags for EKS resources."
  type        = map(string)
  default     = {}
}
