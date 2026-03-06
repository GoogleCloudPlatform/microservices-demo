variable "project_name" {
  description = "Name of the project used for resource naming"
  type        = string
}

variable "eks_oidc_issuer_url" {
  description = "OIDC issuer URL from EKS cluster (empty to skip IRSA setup)"
  type        = string
  default     = ""
}

variable "redis_secret_arn" {
  description = "ARN of the Redis secret for IRSA policy"
  type        = string
  default     = ""
}
