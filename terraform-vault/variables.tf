variable "aws_region" {
  description = "Región de AWS (la misma del clúster EKS)."
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "Tamaño de la EC2 de Vault. t3.small (2 GB RAM) es suficiente."
  type        = string
  default     = "t3.small"
}

variable "key_name" {
  description = "Par de llaves SSH. En AWS Academy ya existe uno llamado vockey."
  type        = string
  default     = "vockey"
}

variable "admin_cidr" {
  description = "Tu IP pública en formato CIDR (ej. 189.203.10.20/32). Solo esa IP podrá entrar por SSH."
  type        = string

  validation {
    condition     = can(cidrhost(var.admin_cidr, 0)) && var.admin_cidr != "0.0.0.0/0"
    error_message = "admin_cidr debe ser tu IP con /32 (ej. 189.203.10.20/32), nunca 0.0.0.0/0."
  }
}
