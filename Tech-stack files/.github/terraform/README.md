This folder contains the Terraform for some of the infrastructure used by the CICD (continuous integration and continuous delivery/continuous deployment) of this repository.

## Update this Terraform

To make changes to this Terraform, follow these steps:

1. Make sure you have access to the `online-boutique-ci` Google Cloud project.
1. Move into this folder: `cd .github/terraform`
1. Set the PROJECT_ID environment variable: `export PROJECT_ID=online-boutique-ci`
1. Prepare Terraform and download the necessary Terraform dependencies (such as the "hashicorp/google" Terraform provider): `terraform init`
1. Apply the Terraform: `terraform apply -var project_id=${PROJECT_ID}`
    * Ideally, you would see `Apply complete! Resources: 0 added, 0 changed, 0 destroyed.` in the output.
1. Make your desired changes to the Terraform code.
1. Apply the Terraform: `terraform apply -var project_id=${PROJECT_ID}`
    * This time, Terraform will prompt you confirm your changes before applying them.
