service_name      = "frontend"
service_protocol  = "http"
service_port      = 8080
service_repo      = "raquio/frontend"
service_count     = 1
service_is_public = true

resources = {
    cpu    = 100
    memory = 128
}

upstreams = {
    "product-catalog" = 5051
    "currency"        = 5052
    "cart"            = 5053
    "recommendation"  = 5054
    "shipping"        = 5055
    "checkout"        = 5056
    "ad"              = 5057
}

env_vars = {
    "ENV_PLATFORM" = "nomad"
}
