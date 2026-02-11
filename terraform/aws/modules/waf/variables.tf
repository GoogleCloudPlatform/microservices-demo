variable "project_name" {
  description = "Name of the project used for resource naming"
  type        = string
}

variable "alb_arn" {
  description = "ARN of the ALB to associate with the WAF"
  type        = string
}
