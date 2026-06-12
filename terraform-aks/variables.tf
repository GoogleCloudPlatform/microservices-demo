variable "subscription_id" {
  type        = string
  description = "Azure subscription ID"
}

variable "location" {
  type        = string
  description = "Azure region"
  default     = "eastus"
}

variable "resource_group_name" {
  type        = string
  description = "Name of the Azure resource group"
  default     = "online-boutique"
}

variable "acr_name" {
  type        = string
  description = "Azure Container Registry name — must be globally unique, alphanumeric only, 5-50 chars"
  default     = "onlineboutiqueacr"
}

variable "cluster_name" {
  type        = string
  description = "AKS cluster name"
  default     = "online-boutique"
}

