# Allow unauthenticated users to invoke the service
resource "google_service_account" "serve_boutique" {
  account_id = "serve-boutique"
}

resource "google_cloud_run_service_iam_binding" "frontendservice" {
  service  = google_cloud_run_service.frontendservice.name
  location = google_cloud_run_service.frontendservice.location
  role     = "roles/run.invoker"
  members  = ["allUsers"]
}

# Deny unauthenticated users to invoke the service
resource "google_service_account" "internal_boutique" {
  account_id = "internal-boutique"
}

resource "google_cloud_run_service_iam_binding" "backendservice" {
  for_each = toset(
    [
      google_cloud_run_service.adservice.name,
      google_cloud_run_service.cartservice.name,
      google_cloud_run_service.checkoutservice.name,
      google_cloud_run_service.currencyservice.name,
      google_cloud_run_service.emailservice.name,
      google_cloud_run_service.paymentservice.name,
      google_cloud_run_service.productcatalogservice.name,
      google_cloud_run_service.recommendationservice.name,
      google_cloud_run_service.shippingservice.name
    ]
  )

  service  = each.value
  location = var.region
  role     = "roles/run.invoker"
  members = [
    "serviceAccount:${google_service_account.serve_boutique.email}",
    "serviceAccount:${google_service_account.internal_boutique.email}",
  ]
}
