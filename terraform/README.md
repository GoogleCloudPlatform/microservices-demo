<!-- Copyright 2022 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License. -->

# Deploy Online Boutique sample application on a GKE cluster

This page walks you through the steps required to deploy the [Online Boutique](https://github.com/GoogleCloudPlatform/microservices-demo) sample application on a [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine) cluster using Terraform.

## Prerequisites

1. [Create a new project or use an existing project](https://cloud.google.com/resource-manager/docs/creating-managing-projects#console) on Google Cloud Platform (GCP), and ensure [billing is enabled](https://cloud.google.com/billing/docs/how-to/verify-billing-enabled) on the project.

## Deploy the sample application

1. Clone the Github repository.
    ```
    git clone https://github.com/GoogleCloudPlatform/microservices-demo.git
    ```

1. Move into the `terraform/` directory which contains the Terraform installation scripts.
    ```
    cd microservices-demo/terraform
    ```

1. Open the `terraform.tfvars` file and replace `<project_id_here>` with the [GCP Project ID](https://cloud.google.com/resource-manager/docs/creating-managing-projects?hl=en#identifying_projects) for the `gcp_project_id` variable.

1. Initialize Terraform.
    ```
    terraform init
    ```

1. See what resources will be created.
    ```
    terraform plan
    ```

1. Create the resources and deploy the sample.
    ```
    terraform apply
    ```

    1. If there is a confirmation prompt, type `yes` and hit Enter/Return.

    Note: This step can take about 10 minutes. Do not interrupt the process.

Once the Terraform script has finished, you can locate the frontend's external IP address to access the sample application.

- Option 1:
    ```
    kubectl get service frontend-external | awk '{print $4}'
    ```

- Option 2: On Google Cloud Console, navigate to "Kubernetes Engine" and then "Services & Ingress" to locate the Endpoint associated with "frontend-external".

## Cleanup

To avoid incurring charges to your Google Cloud account for the resources used in this sample application, either delete the project that contains the resources, or keep the project and delete the individual resources.

To remove the individual resources created for by Terraform without deleting the project:

1. Navigate to the `terraform/` directory.

1. Run the following command:
    ```
    terraform destroy
    ```

    1. If there is a confirmation prompt, type `yes` and hit Enter/Return.
