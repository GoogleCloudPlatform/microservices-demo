# Deploy Bank of Anthos sample application on an Anthos cluster

This page walks you through the steps required to deploy the [Online Boutique](https://github.com/GoogleCloudPlatform/microservices-demo) sample application on a GKE cluster using Terraform.

## Pre-requisites

Setting up the sample requires that you have a [Google Cloud Platform (GCP) project](https://cloud.google.com/resource-manager/docs/creating-managing-projects#console), connected to your billing account.

## Deploy the sample

Once you have ensured that all the pre-requisites are met, follow the steps below to create a GKE cluster and deploy the sample application.

1. Clone the repo:
`git clone https://github.com/GoogleCloudPlatform/microservices-demo.git`
1. Set $TF_VAR_project enviornment variable to a project that has billing enabled:
`export TF_VAR_project=<your project id>`
1. Move into the terraform directory that has the installation scripts:
`cd terraform`
1. Enter the variables.tf file and set gcp_project_id variable to your project id
`default = "<project_id_here>"`
1. Initialize Terraform:
`terraform init`
1. See what resources will be created:
    `terraform plan`
1. Create the resources and deploy the sample:
    `terraform apply`
    This may take a while, do not interrupt the process.

## Delete the sample and the cluster

Once you have finished working with the sample, you can tear down the sample application and the cluster 

1. Run `terraform destroy` from the `terraform` directory.

Please note that this does not delete the project where the GKE cluster was created.