variable "project_name" {
  type        = string
  description = "Project name used for resource naming"
}

variable "vpc_id" {
  type        = string
  description = "ID of the VPC"
}

variable "subnet_ids" {
  type        = list(string)
  description = "Public subnet IDs for the ALB"
}

variable "security_group_id" {
  type        = string
  description = "Security group ID for the ALB"
}

variable "instance_id" {
  type        = string
  description = "EC2 instance ID to register in the target group"
}
