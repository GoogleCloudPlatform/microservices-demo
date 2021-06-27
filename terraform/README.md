# Terraform Online Boutique demo

## Overview

This Terraform template deploys the Online Boutique [microservices demo](https://github.com/GoogleCloudPlatform/microservices-demo) using Terraform. The original Google project was forked and the `terraform` folder was added.

The template creates a VPC network, a GKE cluster and deploys the application using the deployment description from the original project. This makes this project very easy to keep up to date.

The GKE cluster will put nodes, pods and services in different networks which are configurable. The minimum and maximum number of nodes in the node pool is also configurable.

## Pre-Requisites

You will need to have the [gcloud CLI](https://cloud.google.com/sdk/gcloud) and Terraform installed. To quickly get started you can also just use [Google Cloud Shell](https://shell.cloud.google.com).

The Terraform template uses:
* [Terraform 1.0.0](https://www.hashicorp.com/blog/announcing-hashicorp-terraform-1-0-general-availability)
* [Google Cloud Platform Provider 3.72.0](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
* [Gavin Bunney's kubectl Provider 1.11.1](https://registry.terraform.io/providers/gavinbunney/kubectl/latest/docs)

## Terraform Variables

The following variables are defined in `variables.tf`.

| Variable | Description | Default |
|----------|-------------|---------|
| `app_name` | Application name | "onlineboutique" |
| `project_id` | GCP project id | |
| `region` | GCP region | |
| `machine_type` |  [Machine type](https://cloud.google.com/compute/docs/machine-types) for GKE cluster nodes | "e2-standard-2" |
| `preemptible` |  [Preemptible VMs](https://cloud.google.com/compute/docs/instances/preemptible) are cheaper however they might be stopped | true |
| `min_node_count` | Minimum number of GKE nodes per zone | 1 |
| `max_node_count` | Maximum number of GKE nodes per zone | 2 |
| `gke_nodes_cidr` | CIDR range for the GKE Nodes subnet | "10.0.0.0/16" |
| `gke_pods_cidr` | CIDR range for the GKE Pods subnet | "10.1.0.0/16" |
| `gke_services_cidr` | CIDR range for the GKE Services subnet | "10.2.0.0/16" |

## Using the Template

Clone the project and change to the `terraform` folder,
```sh
git clone https://github.com/compalmanel/microservices-demo.git
cd microservices-demo/terraform
```

Set your Cloud Platform project,
```sh
gcloud config set project [project_id]
```

Initialize Terraform,
```sh
terraform init
```

Make sure you uodate `terraform.tfvars` with the values for your `project_id` and preferred `region`. You can also override any of the default values for the variables described above.

Plan the deployment,
```sh
terraform plan -out "demo.tfplan"
```

After reviewing the plan you can apply it,
```sh
terraform apply "demo.tfplan"
```

After the deployment finishes you will be presented with some data about your cluster. You can retrieve the endpoint for the application as well,
```sh
gcloud container clusters get-credentials [app_name] --region [region] --project [project_id]
kubectl get service frontend-external | awk '{print $4}'
```