resource "google_cloud_run_service" "checkoutservice" {
  name     = "checkoutservice"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.internal_boutique.email

      containers {
        image = "gcr.io/google-samples/microservices-demo/checkoutservice:v0.3.2"
        ports {
          container_port = local.ports["checkoutservice"]
        }
        env {
          name  = "DISABLE_TRACING"
          value = "1"
        }
        env {
          name  = "DISABLE_PROFILER"
          value = "1"
        }
        env {
          name  = "PRODUCT_CATALOG_SERVICE_ADDR"
          value = "${substr(google_cloud_run_service.productcatalogservice.status[0].url, 8, -1)}:443"
        }
        env {
          name  = "SHIPPING_SERVICE_ADDR"
          value = "${substr(google_cloud_run_service.shippingservice.status[0].url, 8, -1)}:443"
        }
        env {
          name  = "PAYMENT_SERVICE_ADDR"
          value = "${substr(google_cloud_run_service.paymentservice.status[0].url, 8, -1)}:443"
        }
        env {
          name  = "EMAIL_SERVICE_ADDR"
          value = "${substr(google_cloud_run_service.emailservice.status[0].url, 8, -1)}:443"
        }
        env {
          name  = "CURRENCY_SERVICE_ADDR"
          value = "${substr(google_cloud_run_service.currencyservice.status[0].url, 8, -1)}:443"
        }
        env {
          name  = "CART_SERVICE_ADDR"
          value = "${substr(google_cloud_run_service.cartservice.status[0].url, 8, -1)}:443"
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
