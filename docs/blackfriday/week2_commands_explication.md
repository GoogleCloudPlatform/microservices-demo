# Week 2 - Commands Explication (AWS + EKS + Observability + Load Tests)

Ce document regroupe les commandes utilisées pour:
- lancer l'infrastructure Kubernetes (EKS (Elastic Kubernetes Service)),
- déployer la web app Online Boutique,
- vérifier les pods,
- lancer Grafana, Prometheus et Jaeger,
- exécuter les tests de charge.

---

## 1) Prérequis locaux

```bash
aws --version
terraform version
kubectl version --client
helm version
eksctl version
```

Pourquoi:
- `aws`: accès API AWS.
- `terraform`: déploiement infra.
- `kubectl`: pilotage cluster Kubernetes.
- `helm`: installation charts (Prometheus/Grafana/Jaeger).
- `eksctl`: création de rôles IAM (Identity and Access Management) liés à Kubernetes si besoin.

---

## 2) Variables de travail

```bash
export AWS_REGION=eu-south-1
export REPO_DIR=/home/naxxer/Videos/microservices-demo
export TF_DIR="$REPO_DIR/terraform/aws-module1"
```

Pourquoi:
- éviter de répéter les chemins et la région dans chaque commande.

---

## 3) Lancer le cluster EKS avec Terraform

```bash
cd "$TF_DIR"
terraform init -backend-config=backend.hcl -reconfigure
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

Pourquoi:
- `init`: initialise provider + backend state.
- `plan`: prévisualise ce qui sera créé/modifié.
- `apply`: crée réellement le VPC, EKS, node group, etc.

Vérifier les outputs:

```bash
terraform output
```

---

## 4) Connecter kubectl au cluster

```bash
cd "$TF_DIR"
CLUSTER_NAME=$(terraform output -raw cluster_name)

aws eks update-kubeconfig \
  --name "$CLUSTER_NAME" \
  --region "$AWS_REGION" \
  --alias blackfriday-dev

kubectl config use-context blackfriday-dev
kubectl get nodes -o wide
```

Pourquoi:
- ajoute le contexte Kubernetes local.
- valide que les nœuds sont `Ready`.

---

## 5) Déployer la web app (tous les pods Online Boutique)

```bash
cd "$REPO_DIR"
kubectl create namespace onlineboutique --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -k "$REPO_DIR/kustomize" -n onlineboutique
kubectl -n onlineboutique scale deployment/loadgenerator --replicas=0
```

Pourquoi:
- applique tous les manifests applicatifs.
- garde le `loadgenerator` à 0 par défaut pour limiter le coût.

Vérifier les pods de l'app:

```bash
kubectl -n onlineboutique get pods
kubectl -n onlineboutique get pods -w
```

Vérifier tous les pods cluster:

```bash
kubectl get pods -A
```

---

## 6) Accès à la web app (ALB (Application Load Balancer))

```bash
kubectl -n onlineboutique get ingress frontend-alb
ALB_HOST=$(kubectl -n onlineboutique get ingress frontend-alb -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
echo "$ALB_HOST"
curl -I "http://$ALB_HOST"
```

Pourquoi:
- récupère l'URL publique.
- vérifie que l'app répond (`HTTP/1.1 200 OK` attendu).

---

## 7) Lancer Prometheus + Grafana + Jaeger

Créer namespace + ajouter repos Helm:

```bash
kubectl create namespace observability --dry-run=client -o yaml | kubectl apply -f -
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
helm repo update
```

Installer stack:

```bash
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack -n observability

helm upgrade --install jaeger jaegertracing/jaeger \
  -n observability \
  --set allInOne.enabled=true \
  --set storage.type=memory \
  --set provisionDataStore.cassandra=false \
  --set provisionDataStore.elasticsearch=false \
  --set provisionDataStore.kafka=false \
  --set agent.enabled=false
```

Vérifier:

```bash
kubectl -n observability get pods
kubectl -n observability get svc
helm list -n observability
```

---

## 8) Accès local aux outils d'observabilité

Grafana:

```bash
kubectl -n observability get secret kube-prometheus-stack-grafana -o jsonpath="{.data.admin-password}" | base64 -d ; echo
kubectl -n observability port-forward svc/kube-prometheus-stack-grafana 3000:80
```

URL:
- `http://127.0.0.1:3000`
- user: `admin`
- password: commande ci-dessus

Prometheus:

```bash
kubectl -n observability port-forward svc/kube-prometheus-stack-prometheus 9090:9090
```

URL:
- `http://127.0.0.1:9090`

Jaeger:

```bash
kubectl -n observability port-forward svc/jaeger 16686:16686
```

URL:
- `http://127.0.0.1:16686`

---

## 9) Activer les tests de charge

### 9.1 Profil 5K users (users)

```bash
cd "$REPO_DIR"
NAMESPACE=onlineboutique DEPLOYMENT=loadgenerator ./scripts/blackfriday/set-load-profile.sh week2-5k
kubectl -n onlineboutique scale deployment/loadgenerator --replicas=1
```

### 9.2 Profil 20K users (users)

```bash
cd "$REPO_DIR"
NAMESPACE=onlineboutique DEPLOYMENT=loadgenerator ./scripts/blackfriday/set-load-profile.sh week2-20k
kubectl -n onlineboutique scale deployment/loadgenerator --replicas=1
```

### 9.3 Profil 50K users (users)

```bash
cd "$REPO_DIR"
NAMESPACE=onlineboutique DEPLOYMENT=loadgenerator ./scripts/blackfriday/set-load-profile.sh week2-50k
kubectl -n onlineboutique scale deployment/loadgenerator --replicas=1
```

Observer pendant le test:

```bash
kubectl -n onlineboutique logs deploy/loadgenerator -f --tail=120
kubectl -n onlineboutique get hpa -w
kubectl get nodes -w
kubectl top nodes
kubectl top pods -n onlineboutique | head -n 20
```

Arrêter le test:

```bash
kubectl -n onlineboutique scale deployment/loadgenerator --replicas=0
kubectl -n onlineboutique get deploy loadgenerator
```

---

## 10) Commandes de vérification rapide (sanity checks)

```bash
kubectl get nodes
kubectl -n onlineboutique get pods
kubectl -n kube-system get pods
kubectl -n observability get pods
kubectl -n onlineboutique get ingress frontend-alb
```

---

## 11) Arrêt pour éviter le coût

Arrêt simple (juste la charge):

```bash
kubectl -n onlineboutique scale deployment/loadgenerator --replicas=0
```

Arrêt complet infra (détruit le cluster et ses ressources):

```bash
cd "$TF_DIR"
terraform destroy -var-file=terraform.tfvars
```

---

## 12) Résumé exécution minimale (ordre recommandé)

```bash
cd "$TF_DIR"
terraform init -backend-config=backend.hcl -reconfigure
terraform apply -var-file=terraform.tfvars

CLUSTER_NAME=$(terraform output -raw cluster_name)
aws eks update-kubeconfig --name "$CLUSTER_NAME" --region "$AWS_REGION" --alias blackfriday-dev
kubectl config use-context blackfriday-dev

cd "$REPO_DIR"
kubectl create namespace onlineboutique --dry-run=client -o yaml | kubectl apply -f -
kubectl apply -k "$REPO_DIR/kustomize" -n onlineboutique

kubectl -n onlineboutique get ingress frontend-alb
kubectl -n onlineboutique get pods
```

