output "cluster_name" {
  value       = google_container_cluster.main.name
  description = "GKE cluster name"
}

output "cluster_location" {
  value       = google_container_cluster.main.location
  description = "GKE cluster location (region)"
}

output "cluster_endpoint" {
  value       = google_container_cluster.main.endpoint
  description = "GKE API endpoint"
  sensitive   = true
}
