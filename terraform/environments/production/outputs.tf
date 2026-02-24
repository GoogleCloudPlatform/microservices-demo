output "namespace" {
  value       = "production"
  description = "Namespace where the app is deployed"
}

output "frontend_access_hint" {
  value       = module.app_deploy.frontend_access_hint
  description = "Command to get frontend LoadBalancer IP"
}
