output "namespace" {
  value       = var.namespace
  description = "Namespace where the app was deployed"
}

output "frontend_access_hint" {
  value       = "kubectl get svc frontend-external -n ${var.namespace} -o jsonpath='{.status.loadBalancer.ingress[0].ip}'"
  description = "Command to get frontend LoadBalancer IP"
}
