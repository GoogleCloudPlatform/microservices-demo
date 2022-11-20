# Oded + Nadav customize instructions for the demo


## GCloud 

In order to configure Autopilot GKE on in your GCP account

1. Run 

```
gcloud init
gcloud auth application-default login
```

2. Create a new project

```
gcloud projects create koala-ops-demo
```


## Terraform CLI

Make sure to override the existing values in `terraform/terraform.tfvars`

```
terraform init
terraform apply
```




