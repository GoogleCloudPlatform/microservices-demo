ROOT=$(pwd)
sed -i.tmp  "s/project_id/gcp_project_id/" $ROOT/terraform/terraform.tfvars