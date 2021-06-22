# Get deployment manifests
data "kubectl_path_documents" "manifests" {
    pattern = "${path.module}/../release/kubernetes-manifests.yaml"
}

# Retrieve an access token as the Terraform runner
data "google_client_config" "provider" {}

# Authenticate to the GKE cluster
provider "kubectl" {
  load_config_file       = false
  host                   = "https://${google_container_cluster.primary.endpoint}"
  token                  = data.google_client_config.provider.access_token
  cluster_ca_certificate = "${base64decode(google_container_cluster.primary.master_auth.0.cluster_ca_certificate)}"
}

# Apply the application manifests
resource "kubectl_manifest" "application" {
  count     = length(data.kubectl_path_documents.manifests.documents)
  yaml_body = element(data.kubectl_path_documents.manifests.documents, count.index)
}