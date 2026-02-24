output "cluster_name" {
  value       = module.gke.cluster_name
  description = "GKE cluster name for gcloud get-credentials and app-deploy"
}

output "cluster_location" {
  value       = module.gke.cluster_location
  description = "GKE cluster region"
}

output "cluster_endpoint" {
  value       = module.gke.cluster_endpoint
  description = "GKE API endpoint"
  sensitive   = true
}
