# Tutorial

## Set required variables 

**[Create a Google Cloud Platform project](https://cloud.google.com/resource-manager/docs/creating-managing-projects#creating_a_project)** or use an existing project. Make sure you update `terraform.tfvars` with the values for your `project_id` and preferred `region`. You can also override any of the default values for the variables described above.

## Initialize Terraform

```sh
terraform init
```

## Plan the deployment

```sh
terraform plan -out "demo.tfplan"
```

## Apply the deployment

After reviewing the plan you can apply it,

```sh
terraform apply "demo.tfplan"
```

# Interact with your cluster

After the deployment finishes you will be presented with some data about your cluster, and how You can retrieve the endpoint for the application.

```sh
gcloud container clusters get-credentials [app_name] --region [region] --project [project_id]
kubectl get service frontend-external | awk '{print $4}'
```