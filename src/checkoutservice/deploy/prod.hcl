service_name    = "checkout"
service_port    = 5050
service_repo    = "raquio/demo-checkoutservice"
service_version = "v0.0.2"
service_count   = 1

resources = {
    cpu    = 100
    memory = 128
}

upstreams = {
    "product-catalog" = 5051
    "shipping"        = 5052
    "payment"         = 5053
    "email"           = 5054
    "currency"        = 5055
    "cart"            = 5056
}