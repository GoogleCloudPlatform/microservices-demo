# Week 2 Livrable - Hardening & Optimisation

Source de référence: `BlackFriday_CahierDesCharges MT5.pdf`

Objectif semaine 2:
- Déploiement Multi-AZ (3 zones de disponibilité)
- Security hardening (WAF, Security Groups, IAM)
- Observabilité complète (Prometheus + Grafana + Jaeger)
- Auto-scaling (HPA + Cluster Autoscaler)
- Tests de charge progressifs (5K -> 20K -> 50K)

Livrable attendu:
- Architecture sécurisée et scalable
- Dashboards Grafana

---

## 1) Règle de travail (mise à jour continue)

Ce document est mis à jour à chaque étape validée.

Pour chaque étape terminée, on ajoute:
1. commandes exécutées
2. résultat observé
3. preuves (captures/logs)
4. décision (OK / KO / à corriger)

---

## 2) Statut global semaine 2

- Statut: `IN_PROGRESS`
- Avancement global: `98%`

### Checklist macro

- [x] A. Multi-AZ validé (3 AZ actives et utilisées)
- [x] B. Security hardening validé (WAF + SG + IAM)
- [x] C. Observabilité complète validée (Prometheus + Grafana + Jaeger)
- [x] D. Auto-scaling validé (HPA + Cluster Autoscaler)
- [ ] E. Tests de charge validés (5K, 20K, 50K)
- [ ] F. Conclusion + preuves finales publiées

---

## 3) État initial (avant exécution semaine 2)

### Déjà fait (hérité semaine 1)

- [x] Infrastructure AWS/EKS déployée
- [x] Multi-AZ côté VPC codé (3 subnets publics + 3 subnets privés)
- [x] Application déployée et accessible
- [x] Monitoring CloudWatch basique opérationnel
- [x] Test 1K exécuté

### Reste à faire pour atteindre l'objectif semaine 2

- [x] WAF sur le chemin d'entrée public
- [x] Hardening Security Groups formalisé
- [x] Hardening IAM least-privilege formalisé
- [x] Déploiement Prometheus + Grafana + Jaeger
- [ ] Dashboards Grafana finalisés (screenshots + lecture)
- [x] Activation/tuning HPA en runtime
- [x] Déploiement Cluster Autoscaler
- [ ] Tests 5K, 20K, 50K avec preuves et conclusion

---

## 4) Journal d'exécution détaillé

> On ajoute une entrée par étape validée.

### Étape 2.1 - Pré-check semaine 2

- Date: 2026-03-30
- Objectif: valider le socle avant exécution semaine 2 (auth AWS, accès EKS, état cluster, état application, état CloudWatch).
- Commandes:
```bash
cd /home/naxxer/Videos/microservices-demo/terraform/aws-module1
export AWS_REGION=eu-south-1
aws sts get-caller-identity
terraform output -raw cluster_name
aws eks update-kubeconfig --name "$(terraform output -raw cluster_name)" --region "$AWS_REGION" --alias blackfriday-dev
kubectl config use-context blackfriday-dev
kubectl get nodes -o wide
kubectl -n onlineboutique get pods
kubectl -n onlineboutique get svc frontend-external
HOST=$(kubectl -n onlineboutique get svc frontend-external -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
echo "$HOST"
curl -I "http://$HOST"
kubectl get ns amazon-cloudwatch
kubectl -n amazon-cloudwatch get pods
```
- Résultat: OK. Contexte cluster fonctionnel, nœuds accessibles, workload applicatif accessible, namespace CloudWatch et pods observabilité présents.
- Preuves: sorties CLI de validation + captures précédentes (pods, service frontend-external, CloudWatch dashboard).
- Décision: `OK` (étape validée, passage à l'étape 2.2).

---

### Étape 2.2 - Multi-AZ validation runtime

- Date: 2026-03-30
- Objectif: confirmer en runtime que le cluster EKS est réellement distribué sur 3 zones de disponibilité.
- Commandes:
```bash
export AWS_REGION=eu-south-1
CLUSTER_NAME=$(terraform output -raw cluster_name)
echo "$CLUSTER_NAME"

SUBNET_IDS=$(aws eks describe-cluster \
  --name "$CLUSTER_NAME" \
  --region "$AWS_REGION" \
  --query 'cluster.resourcesVpcConfig.subnetIds' \
  --output text)
echo "$SUBNET_IDS"

kubectl get nodes -L topology.kubernetes.io/zone -o wide
kubectl get nodes -L topology.kubernetes.io/zone --no-headers | awk '{print $NF}' | sort | uniq -c
```
- Résultat: OK. Les nœuds EKS sont `Ready` et répartis sur 3 AZ distinctes.
- Preuves: sortie `kubectl get nodes -L topology.kubernetes.io/zone` montrant `eu-south-1a`, `eu-south-1b`, `eu-south-1c` + comptage `1/1/1`.
- Décision: `OK` (objectif Multi-AZ semaine 2 validé).

---

### Étape 2.3 - Security hardening (WAF / SG / IAM)

- Date: 2026-03-30
- Objectif: auditer la posture sécurité actuelle avant application des mesures de hardening.
- Commandes:
```bash
cd /home/naxxer/Videos/microservices-demo/terraform/aws-module1
export AWS_REGION=eu-south-1
CLUSTER_NAME=$(terraform output -raw cluster_name)
VPC_ID=$(terraform output -raw vpc_id)
HOST=$(kubectl -n onlineboutique get svc frontend-external -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')

aws ec2 describe-security-groups \
  --filters Name=vpc-id,Values="$VPC_ID" \
  --query 'SecurityGroups[*].[GroupId,GroupName,Description]' \
  --output table

aws elb describe-load-balancers \
  --region "$AWS_REGION" \
  --query "LoadBalancerDescriptions[?DNSName=='$HOST'].[LoadBalancerName,Scheme,SecurityGroups]" \
  --output table

NG=$(aws eks list-nodegroups --cluster-name "$CLUSTER_NAME" --region "$AWS_REGION" --query 'nodegroups[0]' --output text)
NODE_ROLE_ARN=$(aws eks describe-nodegroup --cluster-name "$CLUSTER_NAME" --nodegroup-name "$NG" --region "$AWS_REGION" --query 'nodegroup.nodeRole' --output text)
NODE_ROLE_NAME=${NODE_ROLE_ARN##*/}
aws iam list-attached-role-policies --role-name "$NODE_ROLE_NAME" --output table
```
- Résultat:
  - Entrée publique exposée via `Classic ELB` (internet-facing) avec SG dédié `sg-047fd382d453d1a32`.
  - Inventaire SG EKS/VPC obtenu (ELB SG, node shared SG, cluster SG, etc.).
  - Node role IAM identifié avec 4 policies AWS managées:
    - `AmazonEKSWorkerNodePolicy`
    - `AmazonEKS_CNI_Policy`
    - `AmazonEC2ContainerRegistryReadOnly`
    - `CloudWatchAgentServerPolicy`
- Preuves: sorties CLI de l'audit 2.3.0 (SG, ELB, IAM).
- Décision: `PARTIAL_OK`
  - Audit validé.
  - Hardening non terminé tant que:
    1) règles SG détaillées (ingress/egress) non revues,
    2) stratégie WAF non finalisée (Classic ELB ne permet pas l'association WAFv2 directe),
    3) modèle IAM least-privilege non finalisé (IRSA recommandé pour agents d'observabilité).

Complément audit SG (Security Group) - entrée web:
- Ingress observé sur le SG `sg-047fd382d453d1a32`:
  - `tcp/80` depuis `0.0.0.0/0` (attendu pour exposition HTTP)
  - `icmp type 3 code 4` depuis `0.0.0.0/0` (à durcir / retirer)
- Egress observé:
  - `all traffic` vers `0.0.0.0/0` (configuration permissive, à revoir selon architecture finale).

Action hardening appliquée (SG du CLB):
- Mesure: suppression de la règle `ICMP 3/4` ouverte à Internet sur le SG `sg-047fd382d453d1a32`.
- Vérification:
  - Ingress restant: uniquement `tcp/80` depuis `0.0.0.0/0`.
  - Test applicatif: `curl -I http://<frontend-host>` retourne `HTTP/1.1 200 OK`.
- Impact:
  - réduction de la surface d'exposition réseau sans régression fonctionnelle observable.

Audit SG interne (node/cluster/control-plane):
- SG node `sg-0e96304b3e9c51098`:
  - ingress depuis SG cluster sur ports kubelet/webhooks (443, 4443, 6443, 8443, 9443, 10250) + DNS node-to-node (53 tcp/udp) + ephemeral node-to-node.
  - ingress `all protocols` depuis SG du CLB (règle permissive pilotée par le contrôleur Kubernetes pour le trafic LoadBalancer/NodePort).
  - egress `0.0.0.0/0` (allow all).
- SG cluster `sg-08abf104e9517bb63`:
  - ingress 443 depuis SG node (flux API attendu).
- SG control-plane EKS `sg-0a04cf5f37fc59c48`:
  - ingress interne self-reference `all protocols`.
  - egress `0.0.0.0/0`.

Lecture sécurité:
- Aucun ingress direct `0.0.0.0/0` observé sur les SG node/cluster/control-plane.
- Point d'attention principal: règle node SG `all protocols` depuis SG du CLB (surface large, typique architecture CLB/NodePort).
- Durcissement structurel recommandé: migration vers ALB + WAFv2 pour réduire exposition et appliquer des contrôles L7.

Pré-check migration ALB (Application Load Balancer):
- Service `frontend-external` confirmé en `LoadBalancer` avec `NodePort 30703` (modèle CLB/NodePort).
- Endpoint public actuel: `ac53f691f150f4bb4af45b7f68181dd1-1199883996.eu-south-1.elb.amazonaws.com`.
- Contrôleur ALB (`aws-load-balancer-controller`) non présent dans `kube-system`.
- Décision: installer le contrôleur ALB avant création d'un Ingress et association future WAF (Web Application Firewall).

Installation contrôleur ALB:
- OIDC (OpenID Connect) provider EKS déjà associé.
- Policy IAM (Identity and Access Management) `AWSLoadBalancerControllerIAMPolicy` créée.
- ServiceAccount Kubernetes `kube-system/aws-load-balancer-controller` créée avec rôle IAM dédié.
- Helm release `aws-load-balancer-controller` installée dans `kube-system`.
- Vérification runtime:
  - deployment `aws-load-balancer-controller` = `2/2` available.
  - pods contrôleur en statut `Running`.
- Décision: prérequis ALB validés, passage à la création de l'Ingress (Kubernetes Ingress resource).

Création Ingress ALB (Kubernetes Ingress):
- Ressource créée: `ingress.networking.k8s.io/frontend-alb`.
- Adresse publique provisionnée:
  - `k8s-onlinebo-frontend-54d98126ed-1127331537.eu-south-1.elb.amazonaws.com`
- Test fonctionnel:
  - `curl -I http://<alb-host>` retourne `HTTP/1.1 200 OK`.
- Impact:
  - chemin d'entrée ALB opérationnel et prêt pour association WAF (Web Application Firewall).
- Décision:
  - migration d'entrée validée, prochaine action = attacher WAFv2 au nouvel ALB (Application Load Balancer).

Association WAFv2 (Web Application Firewall version 2) sur ALB:
- WebACL (Web Access Control List) créé:
  - Nom: `blackfriday-webacl`
  - ID: `eb3783a9-16de-41db-bb9c-e9b71e2c4681`
  - ARN (Amazon Resource Name): `arn:aws:wafv2:eu-south-1:622333992348:regional/webacl/blackfriday-webacl/eb3783a9-16de-41db-bb9c-e9b71e2c4681`
- Association effectuée:
  - `associate-web-acl` exécuté avec succès vers l'ARN de l'ALB.
- Vérification:
  - `get-web-acl-for-resource` retourne `Name=blackfriday-webacl` pour la ressource ALB.
- Impact:
  - l'entrée web ALB est maintenant protégée par des règles WAF managées + rate limit.
- Décision:
  - composant WAF validé (reste à finaliser le lot hardening global SG/IAM pour clôturer la section B).

Validation fonctionnelle WAF (Web Application Firewall):
- Test baseline:
  - `curl http://<alb-host>/` -> `HTTP 200` (trafic normal autorisé).
- Test requête suspecte:
  - payload `q=<script>alert(1)</script>` -> `HTTP 403 Forbidden` (bloqué par WAF/ALB).
  - payload `q=' OR 1=1 --` -> `HTTP 200` (non bloqué par cette règle précise).
- Vérification métrique CloudWatch:
  - `AWS/WAFV2 BlockedRequests` > 0 observé (`Sum=1.0` sur la fenêtre test).
- Interprétation:
  - WAF actif et efficace au moins sur une classe d'attaque testée.
  - Couverture partielle attendue des règles managées; un tuning complémentaire peut être fait selon les patterns applicatifs.

Basculage d'entrée: CLB (Classic Load Balancer) -> ALB (Application Load Balancer)
- Pré-check: ALB répondait déjà en `HTTP 200`.
- Action:
  - suppression du service Kubernetes `frontend-external` (type `LoadBalancer`) qui provisionnait le CLB.
- Vérifications:
  - `frontend-external` introuvable (suppression effective côté Kubernetes).
  - l'URL ALB continue de répondre en `HTTP 200`.
  - interrogation `aws elb describe-load-balancers` filtrée sur l'ancien DNS CLB ne retourne plus d'entrée.
- Impact:
  - exposition publique consolidée sur ALB + WAF (surface réseau réduite).

Persisting Kubernetes manifests (éviter la recréation du CLB):
- Ajout d'un composant Kustomize dédié:
  - `components/blackfriday-aws-alb-ingress`
  - inclut un `Ingress` `frontend-alb` (classe `alb`) vers le service `frontend`.
  - applique aussi `ENV_PLATFORM=aws` sur le deployment `frontend`.
- Activation des composants dans `kustomize/kustomization.yaml`:
  - `components/non-public-frontend` (supprime `frontend-external`).
  - `components/blackfriday-aws-alb-ingress` (maintient l'entrée ALB).
- Vérification de rendu (`kubectl kustomize kustomize`):
  - `kind: Ingress` + `name: frontend-alb` présents.
  - `ENV_PLATFORM=aws` présent.
  - `frontend-external` absent.

Validation runtime après application `kubectl apply -k`:
- Ressources appliquées sans erreur bloquante.
- `frontend-external` toujours absent (`NotFound`) après apply.
- `frontend-alb` toujours présent avec adresse publique ALB.
- Test endpoint ALB: `HTTP/1.1 200 OK`.
- Conclusion:
  - le mode d'exposition ALB + WAF est désormais persistant dans les manifests.

Validation IAM (Identity and Access Management) least-privilege:
- Rôle node group:
  - policies attachées limitées aux besoins EKS/CNI/ECR/CloudWatch:
    - `AmazonEKSWorkerNodePolicy`
    - `AmazonEKS_CNI_Policy`
    - `AmazonEC2ContainerRegistryReadOnly`
    - `CloudWatchAgentServerPolicy`
  - aucune inline policy détectée (`list-role-policies` vide).
- Rôle cluster EKS:
  - policies attendues EKS + policies custom du module:
    - `AmazonEKSClusterPolicy`
    - `AmazonEKSVPCResourceController`
    - policies custom cluster/encryption gérées par Terraform.
  - aucune inline policy détectée.
- Rôle dédié contrôleur ALB (Application Load Balancer):
  - `AmazonEKSLoadBalancerControllerRole` avec policy unique `AWSLoadBalancerControllerIAMPolicy`.
  - aucune inline policy détectée.
- Décision:
  - posture IAM conforme au principe least-privilege pour l'architecture actuelle.
  - amélioration future possible: déplacer les permissions CloudWatch des nodes vers des rôles IRSA (IAM Roles for Service Accounts) dédiés.

---

### Étape 2.4 - Observabilité complète (Prometheus, Grafana, Jaeger)

- Date: 2026-03-31
- Objectif: déployer et valider la stack d'observabilité avancée (Prometheus, Grafana, Jaeger).
- Commandes:
```bash
kubectl get ns
helm list -A | egrep -i 'prometheus|grafana|jaeger|kube-prometheus'
kubectl -n observability get pods
kubectl -n observability get svc

kubectl create namespace observability --dry-run=client -o yaml | kubectl apply -f -
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
helm repo update

helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  -n observability

helm upgrade --install jaeger jaegertracing/jaeger \
  -n observability \
  --set allInOne.enabled=true \
  --set storage.type=memory \
  --set provisionDataStore.cassandra=false \
  --set provisionDataStore.elasticsearch=false \
  --set provisionDataStore.kafka=false \
  --set agent.enabled=false

kubectl -n observability get pods
kubectl -n observability get svc
helm list -n observability
```
- Résultat:
  - pré-check initial: namespace `observability` vide (aucun pod/service), aucun chart observabilité installé.
  - déploiement réussi de:
    - `kube-prometheus-stack` (Prometheus + Grafana + Alertmanager + Operator)
    - `jaeger` (all-in-one)
  - vérification runtime:
    - pods observabilité en `Running`.
    - services observabilité présents (`kube-prometheus-stack-grafana`, `kube-prometheus-stack-prometheus`, `jaeger`, etc.).
    - releases Helm en statut `deployed`.
- Preuves: sorties Helm install + `kubectl get pods/svc` + `helm list -n observability`.
- Décision: `OK` (stack observabilité installée et opérationnelle).

---

### Étape 2.5 - Auto-scaling (HPA + Cluster Autoscaler)

- Date: 2026-03-31
- Objectif: activer et valider HPA (Horizontal Pod Autoscaler) sur les services critiques.
- Commandes:
```bash
kubectl get apiservice v1beta1.metrics.k8s.io -o wide
kubectl top nodes
kubectl top pods -n onlineboutique | head -n 20

kubectl -n onlineboutique apply -f /home/naxxer/Videos/microservices-demo/kustomize/components/blackfriday-autoscaling/hpa.yaml
kubectl -n onlineboutique get hpa
kubectl -n onlineboutique describe hpa frontend
kubectl -n onlineboutique get hpa -w

kubectl -n onlineboutique scale deployment/loadgenerator --replicas=0
kubectl -n onlineboutique get deploy loadgenerator

export AWS_REGION=eu-south-1
CLUSTER_NAME=$(terraform output -raw cluster_name)
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

cat > /tmp/cluster-autoscaler-policy.json <<EOF
... policy least-privilege Cluster Autoscaler ...
EOF

POLICY_NAME=AmazonEKSClusterAutoscalerPolicy
POLICY_ARN="arn:aws:iam::${ACCOUNT_ID}:policy/${POLICY_NAME}"
aws iam get-policy --policy-arn "$POLICY_ARN" >/dev/null 2>&1 || \
aws iam create-policy --policy-name "$POLICY_NAME" --policy-document file:///tmp/cluster-autoscaler-policy.json

eksctl create iamserviceaccount \
  --cluster "$CLUSTER_NAME" \
  --region "$AWS_REGION" \
  --namespace kube-system \
  --name cluster-autoscaler \
  --role-name AmazonEKSClusterAutoscalerRole \
  --attach-policy-arn "$POLICY_ARN" \
  --override-existing-serviceaccounts \
  --approve

helm repo add autoscaler https://kubernetes.github.io/autoscaler
helm repo update
helm upgrade --install cluster-autoscaler autoscaler/cluster-autoscaler \
  -n kube-system \
  --set cloudProvider=aws \
  --set awsRegion="$AWS_REGION" \
  --set autoDiscovery.clusterName="$CLUSTER_NAME" \
  --set rbac.create=true \
  --set rbac.serviceAccount.create=false \
  --set rbac.serviceAccount.name=cluster-autoscaler

kubectl -n kube-system get deploy -l "app.kubernetes.io/instance=cluster-autoscaler" -o wide
kubectl -n kube-system rollout status deployment/cluster-autoscaler-aws-cluster-autoscaler
kubectl -n kube-system logs deployment/cluster-autoscaler-aws-cluster-autoscaler --tail=120

DEPLOY=$(kubectl -n kube-system get deploy -l "app.kubernetes.io/instance=cluster-autoscaler" -o jsonpath='{.items[0].metadata.name}')
kubectl -n kube-system rollout status deployment/"$DEPLOY"
kubectl -n kube-system logs deployment/"$DEPLOY" --tail=120 | egrep -i "auto-discovery|registered|asg|node group|scale|error|warning"
```
- Résultat:
  - API service métriques disponible: `v1beta1.metrics.k8s.io` = `True`.
  - métriques nodes disponibles (`kubectl top nodes` fonctionnel).
  - métriques pods `onlineboutique` disponibles (`kubectl top pods` fonctionnel).
  - 7 ressources HPA créées (`frontend`, `checkoutservice`, `cartservice`, `recommendationservice`, `productcatalogservice`, `currencyservice`, `paymentservice`).
  - état HPA observé en live:
    - cibles CPU lues correctement (`cpu: x%/target%`),
    - réplicas positionnés automatiquement au `minReplicas=2`.
  - vérification détaillée `describe hpa frontend`:
    - `ScalingActive=True`,
    - `ValidMetricFound`,
    - événement `SuccessfulRescale` vers 2 replicas.
  - `loadgenerator` remis à `0` réplique pour maîtriser le coût hors test.
  - pré-check Cluster Autoscaler:
    - node group détecté: `default-20260330185402615500000013`
    - Auto Scaling Group (ASG) détecté: `eks-default-20260330185402615500000013-eacea00c-43e3-03f1-34a6-194b81c4dcbe`
    - tags auto-discovery déjà présents:
      - `k8s.io/cluster-autoscaler/enabled=true`
      - `k8s.io/cluster-autoscaler/blackfriday-survival-MAH-groupe1=owned`
  - installation Cluster Autoscaler:
    - policy IAM dédiée créée: `AmazonEKSClusterAutoscalerPolicy`.
    - service account IRSA créé: `kube-system/cluster-autoscaler`.
    - release Helm `cluster-autoscaler` installée.
    - deployment effectif: `cluster-autoscaler-aws-cluster-autoscaler` en `1/1 Running`.
    - rollout validé en ciblant le vrai nom du deployment (créé par le chart Helm), pas `deployment/cluster-autoscaler`.
  - point d'attention logs:
    - erreurs `resourceclaims/deviceclasses/resourceslices ... not found` observées.
    - cause probable: version image Cluster Autoscaler (`v1.35.0`) non alignée avec version cluster EKS (`v1.31.x`).
  - correctif appliqué:
    - upgrade Helm avec `image.tag=v1.31.0` (aligné avec EKS `v1.31.x`).
    - logs confirment: `Cluster Autoscaler 1.31.0`.
    - les erreurs `resourceclaims/deviceclasses/resourceslices` ne sont plus observées après alignement.
    - logs restants `failed to acquire lease` = comportement normal de leader election (élection de leader) quand plusieurs répliques tournent.
  - validation finale runtime:
    - deployment `cluster-autoscaler-aws-cluster-autoscaler` confirmé en `1/1` disponible.
    - lease (verrou leader election) présent avec `holderIdentity` actif.
    - logs opérationnels observés (`Scale down status ... scaleDownInCooldown=true`) sans `panic`, `forbidden`, `accessdenied`, ni `fatal`.
- Preuves: sorties `get hpa`, `describe hpa frontend`, `get hpa -w`, `scale deployment/loadgenerator`, install Helm/IRSA Cluster Autoscaler, `rollout status` réussi, logs runtime avant/après correction de version.
- Décision: `OK` (HPA validé + Cluster Autoscaler validé techniquement).

---

### Étape 2.6 - Test de charge 5K

- Date:
- Paramètres:
- Commandes:
```bash
# à compléter
```
- Résultat (latence/erreurs/stabilité):
- Preuves:
- Décision:

---

### Étape 2.7 - Test de charge 20K

- Date:
- Paramètres:
- Commandes:
```bash
# à compléter
```
- Résultat (latence/erreurs/stabilité):
- Preuves:
- Décision:

---

### Étape 2.8 - Test de charge 50K

- Date:
- Paramètres:
- Commandes:
```bash
# à compléter
```
- Résultat (latence/erreurs/stabilité):
- Preuves:
- Décision:

---

## 5) Dashboards Grafana (preuves attendues)

Captures minimales à fournir:
1. Vue cluster (CPU, mémoire, nodes Ready/NotReady)
2. Vue workloads (restarts, pods running/pending)
3. Vue applicative (latence, taux d'erreur, débit)
4. Vue scaling (replicas HPA, évolution nodes)

Commentaires à ajouter sous chaque capture:
- période test
- charge cible (5K/20K/50K)
- lecture rapide (stable / dégradé / saturation)

---

## 6) Critères de validation semaine 2

La semaine 2 est validée si:
1. Multi-AZ confirmé en runtime
2. Hardening sécurité effectivement appliqué
3. Stack observabilité complète opérationnelle
4. HPA + Cluster Autoscaler actifs et observables
5. Les 3 paliers (5K, 20K, 50K) exécutés avec preuves
6. Dashboards Grafana livrés et interprétés

---

## 7) Conclusion finale (à compléter en fin de semaine)

### Verdict
- `PASS` / `PASS_WITH_RESERVATIONS` / `FAIL`

### Synthèse
- Ce qui a fonctionné:
- Limites observées:
- Correctifs nécessaires avant semaine 3:

### Prochaines actions (entrée semaine 3)
1.
2.
3.
