To install the microservices-demo on GKE using terraform do the following:

1. create a project with an active billing account, or use an existing one.
1. `export PROJECT='my-great-project'  # substitute with your project name`
1. `terraform init`
1. `terraform plan -var project=$PROJECT`
1. `terraform apply -auto-approve -var project=$PROJECT`