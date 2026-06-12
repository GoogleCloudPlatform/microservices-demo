resource "azurerm_resource_group" "this" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_container_registry" "this" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location
  sku                 = "Basic"
  admin_enabled       = true
}

variable "tenant_id" {
  type        = string
  description = "Azure AD tenant ID — required for AAD integration"
}

variable "node_count" {
  type        = number
  description = "Number of nodes in the default node pool"
  default     = 3
}

variable "node_vm_size" {
  type        = string
  description = "VM size for the default node pool"
  default     = "Standard_D2s_v3"
}

resource "azurerm_kubernetes_cluster" "this" {
  name                = var.cluster_name
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  dns_prefix          = var.cluster_name

  default_node_pool {
    name       = "default"
    node_count = var.node_count
    vm_size    = var.node_vm_size
  }

  identity {
    type = "SystemAssigned"
  }

  azure_active_directory_role_based_access_control {
    tenant_id = var.tenant_id
  }
}

# Grant AKS nodes AcrPull so they can pull images without an imagePullSecret
resource "azurerm_role_assignment" "aks_acr_pull" {
  principal_id                     = azurerm_kubernetes_cluster.this.kubelet_identity[0].object_id
  role_definition_name             = "AcrPull"
  scope                            = azurerm_container_registry.this.id
  skip_service_principal_aad_check = true
}

variable "cielara_scanner_principal_id" {
  type        = string
  description = "Object ID of the cielara-scanner service principal for AKS cluster access"
  default     = "403814fd-079f-4604-be76-c2c0aeceef63"
}

# Grant cielara-scanner SP read access to the AKS cluster
resource "azurerm_role_assignment" "cielara_scanner_aks" {
  principal_id         = var.cielara_scanner_principal_id
  role_definition_name = "Azure Kubernetes Service Cluster User Role"
  scope                = azurerm_kubernetes_cluster.this.id
}
