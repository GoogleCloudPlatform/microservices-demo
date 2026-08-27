variable "repository_names" {
  description = "List of microservice names, one ECR repo per service"
  type        = list(string)
}

variable "tags" {
  description = "Common tags applied to all repositories"
  type        = map(string)
  default     = {}
}