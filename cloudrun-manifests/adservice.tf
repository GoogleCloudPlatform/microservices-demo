resource "google_cloud_run_service" "adservice" {
  name     = "adservice"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.internal_boutique.email

      containers {
        image = "gcr.io/google-samples/microservices-demo/adservice:v0.3.2"
        ports {
          container_port = local.ports["adservice"]
        }
        env {
          name  = "DISABLE_TRACING"
          value = "1"
        }
        env {
          name  = "DISABLE_PROFILER"
          value = "1"
        }
        resources {
          requests = {
            cpu    = "1.0"
            memory = "64Mi"
          }

          limits = {
            cpu    = "2.0"
            memory = "128Mi"
          }
        }
      }
    }

    metadata {
      annotations = {
        "run.googleapis.com/vpc-access-connector" = google_vpc_access_connector.serverless.name
        "run.googleapis.com/egress"               = "all"
        "run.googleapis.com/ingress"              = "internal"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}
