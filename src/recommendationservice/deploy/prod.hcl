service_name    = "recommendation"
service_port    = 5050
service_repo    = "raquio/demo-recommendationservice"
service_version = "v0.0.2"
service_count   = 1

resources = {
    cpu    = 100
    memory = 450
}

upstreams = {
    "product-catalog" = 5051
}