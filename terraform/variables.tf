variable "subscription_id" {
  description = "Azure subscription_id"
  type        = string  
}

variable "resource_group_name" {
  description = "The Name of the Azure Resource group"
  type        = string  
}

variable "location" {
    description = "Azure region"
    type        = string
}

variable "key_vault_name" {
  description = "The Name of the Key Vault."
  type        = string
}


variable "mysql_username"{
description = "username of the server"
type        = string
}

variable "mysql_password"{
description = "Password of the server"
type        = string
}


variable "mysql_server_name" {
  description = "Name of the Azure MySQL server"
  type        = string
}

variable "mysql_server_version" {
description = "Version of the MySQL felxible server"
type        = string
}

variable "mysql_sku_name"{
description = "Name of the MySQL SKU"
type        = string
}

# Kubernetes Cluster Veriables

variable "aks_cluster_name" {
  description = "Name of the AKS cluster"
  type        = string
}

variable "kubernetes_version" {
description = "Version of the kubernetes version"
type        = string
}

variable "default_node_pool_name" {
  description = "Name of the Default Node Pool Name"
  type        = string
}

variable "vm_size" {
  description = "VM size of the AKS nodes"
  type        = string
}

variable "os_sku" {
  description = "OS SKU for the nodes (e.g., AzureLinux, Ubuntu)"
  type        = string
}

variable "min_count" {
  description = "The minimum number of nodes for the default node pool."
  type        = number
  default     = 1
}

variable "max_count" {
  description = "The maximum number of nodes for the default node pool."
  type        = number
  default     = 2
}

variable "max_pods" {
  description = "Maximum number of pods per node"
  type        = number
  default = 30
}

variable "user_node_pool" {
  description = "Name of the User Node Pool Name"
  type        = string
}

variable "user_node_pool_labels" {
  description = "A map of labels to apply to the user node pool."
  type        = map(string)
  default = {
    workload-type = "staging-pool"
  }
}

variable "user_node_pool_min_count" {
  description = "The minimum number of nodes for the user node pool."
  type        = number
  default     = 1
}

variable "user_node_pool_max_count" {
  description = "The maximum number of nodes for the user node pool."
  type        = number
  default     = 2
}




