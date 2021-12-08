# resource "google_cloud_run_service" "loadgenerator" {
#   name     = "loadgenerator"
#   location = var.region

#   template {
#     spec {
#       containers {
#         image = "gcr.io/google-samples/microservices-demo/loadgenerator:v0.3.2"
#         env {
#           name  = "FRONTEND_ADDR"
#           value = "${substr(google_cloud_run_service.frontendservice.status[0].url, 8, -1)}:443"
#         }
#         env {
#           name  = "USERS"
#           value = 10
#         }

#         resources {
#           requests = {
#             cpu    = "1.0"
#             memory = "64Mi"
#           }

#           limits = {
#             cpu    = "2.0"
#             memory = "128Mi"
#           }
#         }
#       }
#     }
#   }

#   traffic {
#     percent         = 100
#     latest_revision = true
#   }
# }
