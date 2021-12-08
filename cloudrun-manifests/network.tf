module "serverless_vpc" {
  source     = "terraform-google-modules/network/google"
  version    = "~> 4.0.1"
  project_id = var.project_id

  network_name = "serverless-network"
  mtu          = 1460
  subnets = [
    {
      subnet_name   = "boutique-subnet"
      subnet_ip     = "10.10.10.0/28"
      subnet_region = var.region
    }
  ]
}

resource "google_vpc_access_connector" "serverless" {
  provider = google-beta

  name           = "central-boutique"
  machine_type   = "e2-standard-4"
  min_instances  = 2
  max_instances  = 4
  max_throughput = 400
  subnet {
    name = module.serverless_vpc.subnets_names[0]
  }
}
