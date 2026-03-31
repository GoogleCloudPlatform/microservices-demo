# AWS Web App Access - Command Runbook

This README is a copy/paste command flow to deploy infra and access the web app on AWS.

It is optimized for this repo and your current setup:
- region: `eu-south-1`
- module path: `terraform/aws-module1`
- app namespace: `onlineboutique`

## 0) Prerequisites

```bash
aws --version
terraform -version
kubectl version --client
```

Check AWS identity:

```bash
export AWS_REGION=eu-south-1
aws sts get-caller-identity
```

---

## 1) (First time only) Create Terraform backend resources

Choose a globally unique bucket name:

```bash
export TF_STATE_BUCKET=blackfriday-terraform-state-mah-groupe1-eus1-20260306
export TF_LOCK_TABLE=blackfriday-terraform-locks-mah-groupe1
```

Create S3 + DynamoDB lock table:

```bash
cd /home/naxxer/Videos/microservices-demo/terraform/aws-module1/bootstrap-state
terraform init -reconfigure
terraform apply -lock=false \
  -var="aws_region=eu-south-1" \
  -var="state_bucket_name=${TF_STATE_BUCKET}" \
  -var="lock_table_name=${TF_LOCK_TABLE}"
```

---

## 2) Configure main backend and deploy infrastructure

From `terraform/aws-module1`:

```bash
cd /home/naxxer/Videos/microservices-demo/terraform/aws-module1
```

Set `backend.hcl`:

```bash
cat > backend.hcl <<EOF
bucket         = "${TF_STATE_BUCKET}"
key            = "module1/terraform.tfstate"
region         = "eu-south-1"
dynamodb_table = "${TF_LOCK_TABLE}"
encrypt        = true
EOF
```

Initialize and apply:

```bash
terraform init -backend-config=backend.hcl -reconfigure
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

Check naming variables in `terraform.tfvars`:

```bash
grep -E '^(project_name|name_suffix|aws_region)' terraform.tfvars
```

---

## 3) Connect kubectl to EKS

```bash
cd /home/naxxer/Videos/microservices-demo/terraform/aws-module1
aws eks update-kubeconfig \
  --name "$(terraform output -raw cluster_name)" \
  --region eu-south-1 \
  --alias blackfriday-dev

kubectl config use-context blackfriday-dev
kubectl get nodes
```

If you get auth error (`server has asked for credentials`):

```bash
aws sts get-caller-identity
aws eks get-token --cluster-name "$(terraform output -raw cluster_name)" --region eu-south-1 > /dev/null && echo TOKEN_OK
```

If token works but kubectl still fails, IAM principal needs EKS access entry/policy.

---

## 4) Deploy the web app

```bash
kubectl create namespace onlineboutique --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -k /home/naxxer/Videos/microservices-demo/kustomize -n onlineboutique
```

Cost-safe baseline:

```bash
kubectl -n onlineboutique scale deployment/loadgenerator --replicas=0
kubectl -n onlineboutique set env deployment/frontend ENV_PLATFORM=aws
```

Watch rollout:

```bash
kubectl -n onlineboutique get pods -w
```

---

## 5) Get the public URL and open the app

```bash
kubectl -n onlineboutique get ingress frontend-alb
```

Open:
- `http://<ALB-DNS>`

Quick test:

```bash
HOST=$(kubectl -n onlineboutique get ingress frontend-alb -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
echo "$HOST"
curl -I "http://$HOST"
```

If browser shows `403` but curl is `200`:
- use incognito/private window
- force `http://` (not `https://`)
- disable HTTPS-only/forced HTTPS for this domain

---

## 6) Run 1K users load test

```bash
kubectl -n onlineboutique set env deployment/loadgenerator USERS=1000 RATE=25 FRONTEND_ADDR=frontend:80
kubectl -n onlineboutique scale deployment/loadgenerator --replicas=1
kubectl -n onlineboutique logs deploy/loadgenerator -f --tail=100
```

Stop load test:

```bash
kubectl -n onlineboutique scale deployment/loadgenerator --replicas=0
```

---

## 7) Common fixes

### Pods stuck in `Pending`

Check one pod events:

```bash
kubectl -n onlineboutique describe pod $(kubectl -n onlineboutique get pods | awk '/Pending/{print $1; exit}') | tail -n 40
```

If message contains `Too many pods`, increase nodegroup size/type in `terraform.tfvars`, then:

```bash
cd /home/naxxer/Videos/microservices-demo/terraform/aws-module1
terraform apply -var-file=terraform.tfvars
```

### Ingress has no external hostname

```bash
kubectl -n onlineboutique get ingress frontend-alb -w
```

Wait until ALB hostname appears.

---

## 8) Stop everything (budget-safe)

Destroy main infra:

```bash
cd /home/naxxer/Videos/microservices-demo/terraform/aws-module1
terraform destroy -var-file=terraform.tfvars -lock=false
```

Destroy backend resources:

```bash
cd /home/naxxer/Videos/microservices-demo/terraform/aws-module1/bootstrap-state
terraform destroy -lock=false \
  -var='aws_region=eu-south-1' \
  -var="state_bucket_name=${TF_STATE_BUCKET}"
```

If S3 bucket not empty:

```bash
aws s3 rm s3://${TF_STATE_BUCKET} --recursive --region eu-south-1
```
