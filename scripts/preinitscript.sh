echo "called"
ROOT=$(pwd)
echo $ROOT
mv $ROOT/terraform.tfvars $ROOT/terraform/terraform.tfvars 
sed -i.txt  "s/project_name/gcp_project_id/" $ROOT/terraform/terraform.tfvars


