resource "google_redis_instance" "redisservice" {
  name               = "redisservice"
  tier               = "BASIC"
  authorized_network = module.serverless_vpc.network_name
  memory_size_gb     = 1
}
