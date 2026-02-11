variable "project_name" {
  type        = string
  description = "Project name used for resource naming"
}

variable "ami_id" {
  type        = string
  description = "AMI ID for the database EC2 instance"
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type for the database"
  default     = "t2.micro"
}

variable "subnet_id" {
  type        = string
  description = "Subnet ID where the database EC2 instance will be launched"
}

variable "security_group_id" {
  type        = string
  description = "Security group ID for the database EC2 instance"
}

variable "key_name" {
  type        = string
  description = "Name of the SSH key pair"
}

variable "db_username" {
  type        = string
  description = "MySQL root username"
}

variable "db_password" {
  type        = string
  description = "MySQL root password"
  sensitive   = true
}
