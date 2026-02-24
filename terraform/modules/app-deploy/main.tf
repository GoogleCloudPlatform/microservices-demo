locals {
  cluster_name = var.cluster_name
}

module "gcloud" {
  source  = "terraform-google-modules/gcloud/google"
  version = "~> 4.0"

  platform              = "linux"
  additional_components = ["kubectl", "beta"]

  create_cmd_entrypoint = "gcloud"
  create_cmd_body       = "container clusters get-credentials ${local.cluster_name} --region=${var.region} --project=${var.project_id}"
}

resource "null_resource" "create_namespace" {
  provisioner "local-exec" {
    interpreter = ["bash", "-exc"]
    command     = "kubectl create namespace ${var.namespace} --dry-run=client -o yaml | kubectl apply -f -"
  }

  depends_on = [module.gcloud]
}

resource "null_resource" "apply_deployment" {
  provisioner "local-exec" {
    interpreter = ["bash", "-exc"]
    command     = <<-EOT
      echo "Repo root: ${var.repo_root}"
      echo "Overlay: ${var.filepath_manifest}"
      cd "${var.repo_root}" && kubectl apply -k "${var.filepath_manifest}"
      echo "Apply finished. Deployments in namespace ${var.namespace}:"
      kubectl get deployment -n ${var.namespace} --no-headers 2>/dev/null || true
    EOT
  }

  depends_on = [null_resource.create_namespace]
}

resource "null_resource" "wait_conditions" {
  provisioner "local-exec" {
    interpreter = ["bash", "-exc"]
    command     = <<-EOT
      set -e
      kubectl wait --for=condition=AVAILABLE apiservice/v1beta1.metrics.k8s.io --timeout=60s 2>/dev/null || true
      echo "Waiting for deployments to appear in namespace ${var.namespace}..."
      for i in $(seq 1 24); do
        if [ "$(kubectl get deployment -n ${var.namespace} --no-headers 2>/dev/null | wc -l)" -ge 1 ]; then
          echo "Deployments found, waiting for rollout..."
          break
        fi
        if [ "$i" -eq 24 ]; then
          echo "ERROR: No deployments in namespace ${var.namespace}. Check: kubectl get all -n ${var.namespace}"
          exit 1
        fi
        sleep 5
      done
      if ! kubectl wait --for=condition=available deployment --all -n ${var.namespace} --timeout=900s; then
        echo "WARNING: Some deployments did not become ready within 900s (first image pull on GKE can be slow)."
        echo "Terraform will still succeed. Check status: kubectl get pods -n ${var.namespace}"
        exit 0
      fi
    EOT
  }

  depends_on = [null_resource.apply_deployment]
}
