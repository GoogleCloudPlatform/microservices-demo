output "acr_login_server" {
  description = "ACR login server — use as --default-repo for Skaffold"
  value       = azurerm_container_registry.this.login_server
}

output "acr_name" {
  description = "ACR name"
  value       = azurerm_container_registry.this.name
}

output "configure_kubectl" {
  description = "Run this to update your local kubeconfig after provisioning"
  value       = "az aks get-credentials --resource-group ${var.resource_group_name} --name ${var.cluster_name}"
}

output "kube_config" {
  description = "Raw kubeconfig — use for CI if needed"
  value       = azurerm_kubernetes_cluster.this.kube_config_raw
  sensitive   = true
}
