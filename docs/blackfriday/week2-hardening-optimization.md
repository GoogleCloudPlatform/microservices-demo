# Black Friday Survival - Week 2 (Hardening & Optimization)

Week 2 objective from the cahier des charges:
- secure the platform
- deploy full observability
- activate autoscaling
- validate progressive load tests (5K -> 20K -> 50K)

## 1. Security Hardening Baseline

Enable pod-to-pod traffic control:

```bash
cd kustomize
kustomize edit add component components/network-policies
kubectl apply -k .
kubectl get networkpolicy
```

Run continuous vulnerability scanning in CI:
- workflow: `.github/workflows/blackfriday-security-scans.yaml`
- includes Trivy filesystem and IaC/manifests scans
- optional OWASP ZAP baseline via `workflow_dispatch`

## 2. Autoscaling (HPA)

Enable the dedicated autoscaling component:

```bash
cd kustomize
kustomize edit add component components/blackfriday-autoscaling
kubectl apply -k .
kubectl get hpa
```

This component creates HPAs for critical services (`frontend`, `checkoutservice`, `cartservice`, `recommendationservice`, `productcatalogservice`, `currencyservice`, `paymentservice`).

## 3. Cluster Autoscaling (EKS nodes)

In `terraform/aws-module1/terraform.tfvars`, keep `ON_DEMAND` for Week 2 stability tests:

```hcl
node_capacity_type = "ON_DEMAND"
```

Apply infra changes from `terraform/aws-module1/`:

```bash
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

## 4. Observability Stack

Minimum target:
- dashboard for latency / error rate / saturation
- alerts for p95 latency, error burst, CPU saturation

Recommended install on AWS EKS:

```bash
kubectl create namespace observability --dry-run=client -o yaml | kubectl apply -f -
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
helm repo update

helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack -n observability
helm upgrade --install jaeger jaegertracing/jaeger -n observability
```

## 5. Progressive Load Campaign

Use the profile script from repository root:

```bash
./scripts/blackfriday/set-load-profile.sh week2-5k
./scripts/blackfriday/set-load-profile.sh week2-20k
./scripts/blackfriday/set-load-profile.sh week2-50k
```

For each step, collect:
- p95 latency
- error rate
- pod replica evolution (HPA)
- node count evolution (Cluster Autoscaler)

## 6. Week 2 Exit Criteria

- multi-AZ infra stable
- network policies active
- vulnerability scans integrated in CI
- observability dashboards and alerts available
- 50K load rehearsal completed with documented metrics
