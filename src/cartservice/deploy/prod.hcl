service_name    = "cart"
service_port    = 7070
service_repo    = "gcr.io/google-samples/microservices-demo/cartservice"
service_version = "v0.3.8"
service_count   = 1

resources = {
    cpu    = 100
    memory = 128
}

upstreams = {
    "redis" = 5051
}

env_vars = {
    "REDIS_ADDR" = "$${NOMAD_UPSTREAM_ADDR_redis}"
}