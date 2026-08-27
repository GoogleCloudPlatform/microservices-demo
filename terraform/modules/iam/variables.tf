variable "cluster_name" {
  description = "Name of the EKS cluster these roles belong to"
  type        = string
}

variable "tags" {
  type    = map(string)
  default = {}
}