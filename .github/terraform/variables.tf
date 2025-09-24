# Variable que define la región de AWS donde se desplegarán los recursos
variable "aws_region" {
  description = "AWS region to deploy resources" 
  type        = string                            
  default     = "us-east-2"                       
}

# Variable que contiene el ARN del rol IAM necesario para el clúster EKS
variable "eks_role_arn" {
  description = "IAM role ARN for the EKS cluster" 
  type        = string                              
}

# Variable que define el bloque CIDR para la VPC principal
variable "vpc_cidr" {
  description = "CIDR block for the main VPC"  
  type        = string                         
  default     = "10.0.0.0/16"                 
}

# Variable que define el bloque CIDR para la subred pública
variable "public_subnet_cidr" {
  description = "CIDR block for the public subnet"  
  type        = string                             
  default     = "10.0.1.0/24"                        
}

# Variable que define el bloque CIDR para la subred privada
variable "private_subnet_cidr" {
  description = "CIDR block for the private subnet"  
  type        = string                               
  default     = "10.0.2.0/24"                        
}

