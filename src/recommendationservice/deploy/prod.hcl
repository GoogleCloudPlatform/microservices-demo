service_name    = "recommendation"
service_port    = 5050
service_repo    = "raquio/recommendationservice"
service_count   = 1

resources = {
    cpu    = 100
    memory = 450
}

upstreams = {
    "product-catalog" = 5051
}