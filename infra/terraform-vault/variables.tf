variable "aws_region" {
  description = "Región de AWS donde se creará la infraestructura"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "Tipo de instancia EC2 para Vault"
  type        = string
  default     = "t2.micro"
}

variable "key_name" {
  description = "Nombre del par de llaves del laboratorio de AWS"
  type        = string
}

variable "allowed_cidr" {
  description = "Dirección IP autorizada para conectarse por SSH y acceder a Vault"
  type        = string
}

variable "project_name" {
  description = "Nombre utilizado para identificar los recursos"
  type        = string
  default     = "online-boutique-vault"
}
