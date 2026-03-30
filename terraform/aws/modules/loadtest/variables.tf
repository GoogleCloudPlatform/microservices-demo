variable "project_name" {
  type        = string
  description = "Project name used for resource naming"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID where resources will be deployed"
}

variable "subnet_id" {
  type        = string
  description = "Subnet ID for EC2 instances"
}

variable "ami_id" {
  type        = string
  description = "AMI ID for the EC2 instances"
}

variable "instance_type_master" {
  type        = string
  description = "EC2 instance type for the Locust master"
  default     = "t3.small"
}

variable "instance_type_worker" {
  type        = string
  description = "EC2 instance type for the Locust workers"
  default     = "t3.large"
}

variable "worker_count" {
  type        = number
  description = "Number of Locust worker instances"
  default     = 3
}

variable "key_name" {
  type        = string
  description = "Name of the SSH key pair for EC2 access"
}

variable "target_host" {
  type        = string
  description = "Target host URL for load testing"
}

variable "locustfile_content" {
  type        = string
  description = "Content of the locustfile.py to deploy on all instances"
}
