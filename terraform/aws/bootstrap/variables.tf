variable "region" {
  type        = string
  description = "Región de AWS. Learner Lab normalmente solo permite us-east-1."
  default     = "us-east-1"
}

variable "state_bucket_name" {
  type        = string
  description = "Nombre del bucket S3 para el state de Terraform. Debe ser único a nivel global en todo AWS, no solo en tu cuenta."
}
