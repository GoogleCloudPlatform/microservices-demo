service_name     = "redis"
service_port     = 6379
service_protocol = "tcp"
service_repo     = "redis"
service_version  = "alpine"
service_count    = 1

resources = {
  cpu    = 100
  memory = 128
}