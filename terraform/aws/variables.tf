variable "aws_region" {
  type        = string
  description = "AWS region to deploy resources"
  default     = "eu-central-2"
}

variable "aws_access_key" {
  type        = string
  description = "AWS access key"
  sensitive   = true
}

variable "aws_secret_key" {
  type        = string
  description = "AWS secret key"
  sensitive   = true
}

variable "project_name" {
  type        = string
  description = "Project name used for resource naming"
  default     = "online-boutique"
}

variable "ami_id" {
  type        = string
  description = "AMI ID for the EC2 instance"
  default     = "ami-095791d719c96cf1d"
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type"
  default     = "t3.micro"
}

variable "key_name" {
  type        = string
  description = "Name of the SSH key pair for EC2 access"
}

variable "db_username" {
  type        = string
  description = "MySQL username for the database EC2 instance"
  default     = "admin"
}

variable "db_password" {
  type        = string
  description = "MySQL password for the database EC2 instance"
  sensitive   = true
}

variable "availability_zones" {
  type        = list(string)
  description = "Availability zones to use"
  default = [
    "eu-central-2a",
    "eu-central-2b"
  ]
}
