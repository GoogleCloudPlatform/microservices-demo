output "grafana_url" {
  value       = "http://${try(data.kubernetes_service.grafana.status[0].load_balancer[0].ingress[0].hostname, "")}"
  description = "Grafana URL"
}

output "app_url" {
  value       = "http://${try(data.kubernetes_service.frontend.status[0].load_balancer[0].ingress[0].hostname, "")}"
  description = "Online Boutique URL"
}