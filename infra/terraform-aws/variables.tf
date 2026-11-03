variable "aws_region" {
  description = "Región de AWS donde se creará la infraestructura"
  type        = string
  default     = "us-east-1"
}

variable "ecr_repository_name" {
  description = "Nombre del repositorio para la imagen Docker"
  type        = string
  default     = "online-boutique-frontend"
}

variable "cluster_name" {
  description = "Nombre del clúster de Kubernetes"
  type        = string
  default     = "online-boutique-cluster"
}
