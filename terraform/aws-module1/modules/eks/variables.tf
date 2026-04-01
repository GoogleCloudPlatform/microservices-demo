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
  description = "Node instance types for on-demand node group."
  type        = list(string)
}

variable "node_group_min_size" {
  description = "Minimum node count for on-demand node group."
  type        = number
}

variable "node_group_max_size" {
  description = "Maximum node count for on-demand node group."
  type        = number
}

variable "node_group_desired_size" {
  description = "Desired node count for on-demand node group."
  type        = number
}

variable "enable_spot_node_group" {
  description = "Enable an additional Spot node group for non-critical workloads."
  type        = bool
  default     = false
}

variable "spot_node_instance_types" {
  description = "Node instance types for Spot node group."
  type        = list(string)
  default     = ["m6i.large"]
}

variable "spot_node_group_min_size" {
  description = "Minimum node count for Spot node group."
  type        = number
  default     = 0
}

variable "spot_node_group_max_size" {
  description = "Maximum node count for Spot node group."
  type        = number
  default     = 10
}

variable "spot_node_group_desired_size" {
  description = "Desired node count for Spot node group."
  type        = number
  default     = 0
}

variable "tags" {
  description = "Tags for EKS resources."
  type        = map(string)
  default     = {}
}
