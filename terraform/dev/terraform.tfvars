## Project
project_id = "cloudcover-sandbox"
region     = "asia-southeast1"
zone       = "asia-southeast1-a"

## Network
network_name = "microservice-demo"

## GKE
### Subnet
gke_subnet_name                = "gke-subnet"
gke_subnet_cidr_range          = "10.10.10.0/24"
gke_subnet_cidr_range_pod      = "192.168.0.0/22"
gke_subnet_cidr_range_services = "192.168.4.0/22"
### Config
gke_name              = "microservices-demo-gke"
gke_cidr_range_master = "172.16.0.0/28"
