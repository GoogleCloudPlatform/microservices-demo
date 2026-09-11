variable "region" {
  type        = string
  description = "Región de AWS. Learner Lab normalmente solo permite us-east-1."
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Prefijo usado para nombrar los recursos de este proyecto"
  default     = "boutique-eq4"
}
