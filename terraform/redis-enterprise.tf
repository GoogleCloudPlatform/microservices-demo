#
# Provision for GCP MP subscription
#
# Ensure the following variables in your shell environment:
# export GOOGLE_APPLICATION_CREDENTIALS=<your Google APIs credentials>
# export REDISCLOUD_ACCESS_KEY=<your Redis Enterrpise Cloud api access key>
# export REDISCLOUD_SECRET_KEY=<your Redis Enterprise Cloud secret key>
#

resource "rediscloud_subscription" "mc-example" {

  # count specifies the number of instances to create;
  # if var.redis-enterprise is true then the resource is enabled
  count = var.redis-enterprise ? 1 : 0

  name           = "online-boutique-sub"
  memory_storage = "ram"

  cloud_provider {
    #Running in GCP on Redis resources
    provider         = "GCP"
    cloud_account_id = 1
    region {
      region                       = var.region
      networking_deployment_cidr   = "192.168.88.0/24"
      preferred_availability_zones = []
    }
  }

  creation_plan {
    average_item_size_in_bytes   = 1
    memory_limit_in_gb           = 1
    quantity                     = 1
    replication                  = false
    support_oss_cluster_api      = false
    throughput_measurement_by    = "operations-per-second"
    throughput_measurement_value = 25000
    modules                      = []
  }
}

resource "rediscloud_subscription_database" "mc-example" {

  # count specifies the number of instances to create;
  # if var.redis-enterprise is true then the resource is enabled
  count = var.redis-enterprise ? 1 : 0

  subscription_id              = rediscloud_subscription.mc-example[0].id
  name                         = "online-boutique-cart"
  protocol                     = "redis"
  memory_limit_in_gb           = 1
  replication                  = true
  data_persistence             = "aof-every-1-second"
  throughput_measurement_by    = "operations-per-second"
  throughput_measurement_value = 25000
  average_item_size_in_bytes   = 0
  depends_on                   = [rediscloud_subscription.mc-example]
}

data "google_compute_network" "network" {
  project = var.gcp_project_id
  name    = "default"
}

resource "rediscloud_subscription_peering" "mc-example-peering" {

  # count specifies the number of instances to create;
  # if var.redis-enterprise is true then the resource is enabled
  count = var.redis-enterprise ? 1 : 0

  subscription_id  = rediscloud_subscription.mc-example[0].id
  provider_name    = "GCP"
  gcp_project_id   = data.google_compute_network.network.project
  gcp_network_name = data.google_compute_network.network.name
}

resource "google_compute_network_peering" "mc-example-peering" {

  # count specifies the number of instances to create;
  # if var.redis-enterprise is true then the resource is enabled
  count = var.redis-enterprise ? 1 : 0

  name         = format("online-boutique-%s", rediscloud_subscription.mc-example[0].name)
  network      = data.google_compute_network.network.self_link
  peer_network = "https://www.googleapis.com/compute/v1/projects/${rediscloud_subscription_peering.mc-example-peering[0].gcp_redis_project_id}/global/networks/${rediscloud_subscription_peering.mc-example-peering[0].gcp_redis_network_name}"
}

# Edit contents of Redis Enterprise kustomization.yaml file to target the new fully managed Redis Enterprise database instance
resource "null_resource" "kustomization-update-redis-enterprise" {
  provisioner "local-exec" {
    interpreter = ["bash", "-exc"]
    command     = <<EOT
                  sed -i .bak "s/REDIS_CONNECTION_STRING/${rediscloud_subscription_database.mc-example[0].private_endpoint},user=default,password=${rediscloud_subscription_database.mc-example[0].password}/g" ../kustomize/components/redis-enterprise/kustomization.yaml
                  kubectl apply -k ../kustomize
    EOT
  }

  # count specifies the number of instances to create;
  # if var.redis-enterprise is true then the resource is enabled
  count = var.redis-enterprise ? 1 : 0

  depends_on = [
    google_compute_network_peering.mc-example-peering
  ]
}
