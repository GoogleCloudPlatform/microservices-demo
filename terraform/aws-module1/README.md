# Module 1 - Architecture Cloud, IaC et Automatisation (AWS)

Ce dossier couvre la partie 1 du cahier des charges:
- Terraform (modules, state management, workspaces)
- Kubernetes/EKS (deploiement, Helm, namespaces, RBAC)
- CI/CD (GitHub Actions + Argo CD)
- Multi-AZ (3 zones)

## 1. Prerequis

- AWS CLI configure (`aws configure` ou SSO)
- Terraform >= 1.6
- kubectl + helm
- IAM permissions pour VPC, EKS, IAM, EC2, ELB, CloudWatch

## 2. State management (S3 + DynamoDB) - Step 1

Creer le backend Terraform avec le bootstrap infra dedie:

```bash
cd bootstrap-state
terraform init
terraform apply -var='state_bucket_name=blackfriday-terraform-state-<suffix-unique>'
cd ..
```

Recuperer les valeurs et completer `backend.hcl`:
- `bucket = <state_bucket_name>`
- `dynamodb_table = <lock_table_name>`

## 3. Initialisation du backend distant - Step 2

Initialiser Terraform Module 1 avec le backend distant:

```bash
cp backend.hcl.example backend.hcl
terraform init -backend-config=backend.hcl
```

## 4. Workspaces - Step 3

Utiliser un workspace par environnement:

```bash
terraform workspace new dev
terraform workspace new stage
terraform workspace new prod
terraform workspace select dev
```

## 5. Variables - Step 4

```bash
cp terraform.tfvars.example terraform.tfvars
```

Adapter au besoin:
- `aws_region`
- tailles de node group
- tags FinOps
- `enable_cluster_bootstrap` (laisser `false` au premier apply)

## 6. Provisionner Module 1 - Step 5

Phase 1 (infra AWS uniquement):

```bash
terraform fmt -recursive
terraform validate
terraform plan -var-file=terraform.tfvars -out=tfplan
terraform apply tfplan
```

Phase 2 (Kubernetes bootstrap namespaces/RBAC/Helm):

```bash
terraform apply -var-file=terraform.tfvars -var='enable_cluster_bootstrap=true'
```

Resultat attendu:
- VPC multi-AZ (3 AZ, subnets publics/prives)
- Cluster EKS
- Namespaces: `onlineboutique`, `observability`, `argocd` (phase 2)
- RBAC lecture seule (`blackfriday-observers`) (phase 2)
- Helm releases: `metrics-server`, `ingress-nginx`, `argocd` (phase 2)

## 7. Acces cluster - Step 6

```bash
aws eks update-kubeconfig --name "$(terraform output -raw cluster_name)" --region "${AWS_REGION:-eu-west-3}"
kubectl get nodes
kubectl get ns
```

Puis deployer l'app avec kustomize:

```bash
kubectl apply -k ../../kustomize
```

## 8. GitOps avec Argo CD

Les manifests Argo CD sont dans:
- `gitops/argocd/projects/blackfriday.yaml`
- `gitops/argocd/applications/online-boutique.yaml`

Avant application, remplacer `repoURL` dans l'Application Argo CD avec l'URL Git de votre fork/repository.

Appliquer apres installation Argo CD:

```bash
kubectl apply -f ../../gitops/argocd/projects/blackfriday.yaml
kubectl apply -f ../../gitops/argocd/applications/online-boutique.yaml
```

## 9. CI/CD

Workflow dedie:
- `.github/workflows/aws-module1-terraform.yaml`

Fonctionnement:
- PR: `fmt`, `validate`, puis `plan` si role AWS OIDC configure
- `main`: validation continue sur les changements Module 1

Variables GitHub a definir:
- `AWS_ROLE_TO_ASSUME`
- `AWS_REGION`
