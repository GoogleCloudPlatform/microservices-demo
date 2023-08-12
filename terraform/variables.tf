#
# Variables Configuration
#

variable "cluster-name" {
  default = "eks-cluster"
  type    = string
}
variable "key_pair_name" {
  default = "since"
}
variable "eks_node_instance_type" {
  default = "t2.micro"
}
variable "region" {
  default = "us-east-1"
}
variable "workstation-external-cidr" {
  description = "CIDR block for the external IP address of your workstation"
  type        = string
  default     = "0.0.0.0/32"
}
variable "memorystore" {
  description = "Flag to enable or disable Google Cloud Memorystore"
  type        = bool
  default     = false 
}

