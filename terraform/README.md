# Terraform Online Boutique demo

## Overview

This Terraform template deploys the Online Boutique [microservices demo](https://github.com/GoogleCloudPlatform/microservices-demo) using Terraform. The original Google project was forked and the `terraform` folder was added.

The template creates a VPC network, a GKE cluster and deploys the application using the deployment descriptor from the original project. This makes this project very easy to keep up to date.

The cluster is created using security good practices:

* nodes are [private](https://cloud.google.com/kubernetes-engine/docs/concepts/private-cluster-concept), only the cluster endpoint is public
* nodes use [Shielded VMs](https://cloud.google.com/kubernetes-engine/docs/how-to/shielded-gke-nodes) with secure boot and integrity monitoring enabled
* [Workload identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity) is enabled

## Pre-Requisites

You will need the [gcloud CLI](https://cloud.google.com/sdk/gcloud) and [Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli) installed. To quickly get started you can also just use [Google Cloud Shell](https://shell.cloud.google.com).

The Terraform template uses:

* [Terraform](https://www.hashicorp.com/blog/announcing-hashicorp-terraform-1-0-general-availability) 1.0.0
* [Google Cloud Platform Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs) 4.6.0
* [Gavin Bunney's kubectl Provider](https://registry.terraform.io/providers/gavinbunney/kubectl/latest/docs) 1.13.1

## Terraform Variables

The following variables are defined in `variables.tf`.

| Variable | Description | Default |
|----------|-------------|---------|
| `app_name` | Application name | "onlineboutique" |
| `project_id` | GCP project id | |
| `region` | GCP region | |
| `machine_type` |  [Machine type](https://cloud.google.com/compute/docs/machine-types) for GKE cluster nodes | "e2-standard-2" |
| `preemptible` |  [Preemptible VMs](https://cloud.google.com/compute/docs/instances/preemptible) are instances that you can create and run at a much lower price than normal instances. However, Compute Engine might stop (preempt) these instances if it requires access to those resources for other tasks. They're suitable for a GKE development instance. | true |
| `min_node_count` | Minimum number of GKE nodes per zone | 1 |
| `max_node_count` | Maximum number of GKE nodes per zone | 2 |
| `gke_nodes_cidr` | The IP range in CIDR notation to use for the nodes network. This range will be used for assigning private IP addresses to cluster nodes. This range must not overlap with any other ranges in use within the cluster's network. | "10.0.0.0/16" |
| `gke_pods_cidr` | The IP range in CIDR notation to use for the pods network. This range will be used for assigning private IP addresses to pods deployed in the cluster. This range must not overlap with any other ranges in use within the cluster's network. | "10.1.0.0/16" |
| `gke_services_cidr` | The IP range in CIDR notation to use for the services network. This range will be used for assigning private IP addresses to services deployed in the cluster. This range must not overlap with any other ranges in use within the cluster's network. | "10.2.0.0/16" |
| `gke_master_cidr` | The IP range in CIDR notation to use for the hosted master network. This range will be used for assigning private IP addresses to the cluster master(s) and the ILB VIP. This range must not overlap with any other ranges in use within the cluster's network, and it must be a /28 subnet. | "10.3.0.0/28" |

## Quickstart

[![Open in Cloud Shell](https://gstatic.com/cloudssh/images/open-btn.svg)](https://ssh.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https://github.com/compalmanel/microservices-demo&cloudshell_workspace=.&cloudshell_open_in_editor=terraform/terraform.tfvars&cloudshell_tutorial=terraform/tutorial.md)
