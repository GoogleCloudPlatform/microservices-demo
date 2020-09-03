module "vpc" {
  source  = "terraform-google-modules/network/google"
  version = "~> 2.5"

  project_id   = var.project_id
  network_name = var.network_name
  routing_mode = "GLOBAL"

  subnets = [
    {
      subnet_name           = var.gke_subnet_name
      subnet_ip             = var.gke_subnet_cidr_range
      subnet_region         = var.region
      subnet_private_access = "true"
      subnet_flow_logs      = "true"
      description           = "Gke subnet for microservices demo"
    },
  ]

  secondary_ranges = {
    "${var.gke_subnet_name}" = [
      {
        range_name    = "secondary-range-pods"
        ip_cidr_range = var.gke_subnet_cidr_range_pod
      },
      {
        range_name    = "secondary-range-services"
        ip_cidr_range = var.gke_subnet_cidr_range_services
      },
    ]
  }
}
