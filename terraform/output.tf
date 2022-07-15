output "cluster_location" {
    description = "Location of the cluster"
    value = resource.google_container_cluster.cluster.location
}

output "cluster_name" {
    description = "Name of the cluster"
    value = resource.google_container_cluster.cluster.name
}
