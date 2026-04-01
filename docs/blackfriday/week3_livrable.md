# Week 3 Livrable - Pre-Black Friday (Budget cible: 600 EUR)

Source de reference: `BlackFriday_CahierDesCharges MT5.pdf`.

## 1) Objectif Week 3

Objectif global: preparer la plateforme pour la simulation finale Black Friday en validant:
1. Chaos engineering (injection de pannes controlees).
2. Optimisation des couts (Spot Instances + rightsizing).
3. Repetition generale a 70K utilisateurs.
4. Runbooks d'incident finalises.
5. Preparation de la War Room.

Budget cible:
- plafond de reference: `600 EUR` pour la semaine de pre-production.

## 2) Acronymes (mots complets)

- AWS: Amazon Web Services
- VPC: Virtual Private Cloud
- EKS: Elastic Kubernetes Service
- EC2: Elastic Compute Cloud
- HPA: Horizontal Pod Autoscaler
- CA: Cluster Autoscaler
- SLO: Service Level Objective
- SLA: Service Level Agreement
- MTTR: Mean Time To Recovery
- SEV: Severity (niveau de severite incident)
- IRSA: IAM Roles for Service Accounts
- FinOps: Financial Operations

---

## 3) Implementation par point (etape par etape)

### 3.1 Chaos engineering - injection de pannes controlees

#### Ce que nous avons implemente
- Script d'execution des drills:
  - `scripts/blackfriday/week3-chaos-drill.sh`
- Scenarios supportes:
  - suppression controlee de pod (`pod-delete`)
  - redemarrage controle d'un deployment (`rollout-restart`)
  - baisse puis retour des replicas (`scale-pulse`)

#### Commandes (pas a pas)
```bash
cd /home/naxxer/Videos/microservices-project

# Drill 1: supprimer 1 pod frontend
NAMESPACE=onlineboutique ./scripts/blackfriday/week3-chaos-drill.sh pod-delete frontend 1

# Drill 2: redemarrer recommendationservice
NAMESPACE=onlineboutique ./scripts/blackfriday/week3-chaos-drill.sh rollout-restart recommendationservice

# Drill 3: couper puis remettre frontend
NAMESPACE=onlineboutique ./scripts/blackfriday/week3-chaos-drill.sh scale-pulse frontend 0 45
```

#### Problemes possibles et approche
- Probleme: perturbation trop large.
  - Approche: un seul drill a la fois, fenetre de test limitee, observation en temps reel.
- Probleme: faux negatif (incident non detecte).
  - Approche: suivre les metriques et evenements en parallele (`kubectl get events`, Grafana, logs).

#### Resultat
- Pre-check avant chaos:
  - `loadgenerator` scale a `0`
  - 3 nodes `Ready`
  - HPA actifs sur 7 services
- Drill 1 - `pod-delete frontend 1`:
  - horodatage injection: `2026-04-01T15:19:41Z`
  - resultat: nouveau pod frontend cree et pret
  - MTTR mesure: `30s`
  - interpretation: injection manuelle, recuperation automatique Kubernetes (auto-healing)
- Drill 2 - `rollout-restart recommendationservice`:
  - horodatage injection: `2026-04-01T15:20:17Z`
  - resultat: rollout termine avec succes, nouveaux pods `Running 1/1`
  - observation normale: anciens pods en `Terminating/Error` pendant le remplacement
  - interpretation: test de redemarrage controle (pilotage manuel + execution automatique du rollout par Kubernetes)
- Drill 3 - `scale-pulse frontend 0 45`:
  - horodatage injection: `2026-04-01T15:22:35Z`
  - remise a l'etat nominal: `2026-04-01T15:23:26Z`
  - MTTR mesure (global): `76s`
  - dont panne volontaire: `45s`
  - temps technique de reprise apres remise en service: `~31s`
  - interpretation: test de procedure runbook (pas un test auto-healing pur)
- Mesure impact HTTP:
  - tentative `curl` ayant retourne `403` non retenue comme KPI chaos car la commande etait malformed (`\\;`) et potentiellement influencee par proxy local.
  - commande valide recommandee: `curl -I --noproxy '*' "http://$ALB_HOST/"`

#### Conclusion partielle
- Le mecanisme d'injection de panne est en place et reutilisable.
- La recuperation automatique est validee sur le scenario de panne pod (`pod-delete`).
- Le scenario `scale-pulse` est conserve comme test de procedure incident (runbook), pas comme preuve principale d'auto-healing.

---

### 3.2 Optimisation des couts (Spot Instances + rightsizing)

#### Ce que nous avons implemente
1. Strategie EKS mixte (stabilite + cout):
   - node group `ON_DEMAND` pour les workloads critiques (socle stable),
   - node group `SPOT` optionnel pour les workloads non critiques.
   - fichiers modifies:
     - `terraform/aws-module1/variables.tf`
     - `terraform/aws-module1/main.tf`
     - `terraform/aws-module1/modules/eks/variables.tf`
     - `terraform/aws-module1/modules/eks/main.tf`
     - `terraform/aws-module1/terraform.tfvars.example`
2. Ciblage des workloads non critiques vers Spot (sans rigidite):
   - component `kustomize/components/blackfriday-spot-workloads/`
   - services cibles: `loadgenerator`, `recommendationservice`
   - mecanisme:
     - `tolerations` pour accepter le taint Spot,
     - `nodeAffinity` en mode `preferred` vers `capacity-type=spot`.
3. Rightsizing applicatif:
   - component `kustomize/components/blackfriday-capacity-tuning/`
   - tuning CPU/RAM sur `frontend`, `loadgenerator`, `currencyservice`, `recommendationservice`.

#### Pourquoi cela reduit les couts
- Spot Instances: baisse du cout unitaire des noeuds EC2.
- Rightsizing: moins de gaspillage CPU/RAM reserve, meilleure densite de pods.
- Effet combine: moins de noeuds * et des noeuds moins chers.

#### Commandes (pas a pas)
```bash
cd /home/naxxer/Videos/microservices-project/terraform/aws-module1

# 1) Activer Spot pour workloads non critiques
# Dans terraform.tfvars:
# enable_spot_node_group = true
# spot_node_instance_types = ["m6i.large"]
# spot_node_group_min_size = 0
# spot_node_group_max_size = 10
# spot_node_group_desired_size = 1

terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

```bash
cd /home/naxxer/Videos/microservices-project

# 2) Appliquer les composants kustomize (rightsizing + placement Spot)
kubectl -n onlineboutique apply -k ./kustomize

# 3) Verifier les labels/taints de noeuds
kubectl get nodes --show-labels | grep -E "NAME|capacity-type"
kubectl describe node <spot-node-name> | grep -A3 Taints

# 4) Verifier le placement des workloads non critiques
kubectl -n onlineboutique get pods -o wide | egrep "loadgenerator|recommendationservice"
```

Rollback (retour 100% on-demand):
```bash
cd /home/naxxer/Videos/microservices-project/terraform/aws-module1

# enable_spot_node_group = false
terraform apply -var-file=terraform.tfvars
```

#### Problemes possibles et approche
- Probleme: interruption Spot (reclaim AWS).
  - Approche: garder le coeur applicatif sur `ON_DEMAND`, Spot reserve aux workloads non critiques.
- Probleme: Spot indisponible temporairement.
  - Approche: `nodeAffinity preferred` (pas `required`), les pods peuvent revenir sur on-demand.
- Probleme: OOM/latence apres rightsizing.
  - Approche: ajustement progressif base metriques (`kubectl top`, Grafana, HPA).

#### Resultat
- Node Spot actif confirme: `ip-10-40-99-249` avec labels `capacity-type=spot` et `workload-tier=best-effort`.
- Configuration workloads non critiques validee: `loadgenerator` et `recommendationservice` exposent bien `tolerations` Spot + `nodeAffinity preferred`.
- Validation de placement Spot executee: `loadgenerator` force temporairement via `nodeSelector` puis pods observes sur le node Spot.
- Rollback operationnel valide: suppression du `nodeSelector` + redemarrage, puis retour au mode normal (preference Spot non stricte).
- Etat final stable de test: `loadgenerator` remis a `replicas=0` apres verification.

#### Conclusion partielle
- Le design cout est en place: stable pour le critique, optimise pour le non critique.

---

### 3.3 Repetition generale 70K utilisateurs

#### Ce que nous avons implemente
- Script de repetition 70K:
  - `scripts/blackfriday/week3-70k-rehearsal.sh`
- Ce script:
  - applique le profil `week3-70k`
  - force un `RATE` progressif (par defaut `100`) pour eviter un ramp-up brutal
  - propose commandes de monitoring et d'arret

#### Commandes (pas a pas)
```bash
cd /home/naxxer/Videos/microservices-project

# Demarrer la repetition
NAMESPACE=onlineboutique DEPLOYMENT=loadgenerator RATE_OVERRIDE=100 \
  ./scripts/blackfriday/week3-70k-rehearsal.sh start

# Etat en direct
./scripts/blackfriday/week3-70k-rehearsal.sh status

# Logs loadgenerator
./scripts/blackfriday/week3-70k-rehearsal.sh logs

# Arret
./scripts/blackfriday/week3-70k-rehearsal.sh stop
```

#### Problemes possibles et approche
- Probleme: OOMKilled du loadgenerator.
  - Approche: limiter `RATE`, augmenter ressources loadgenerator, relancer proprement.
- Probleme: CrashLoopBackOff services sous pic.
  - Approche: rightsizing cible, verification probes, analyse post-run.

#### Resultat
- [A renseigner] replicas HPA au pic, erreurs applicatives, latence, stabilite post-charge.

#### Conclusion partielle
- Le run 70K est industrialise avec script et procedure de pilotage.

---

### 3.4 Runbooks et procedures d'incident

#### Ce que nous avons implemente
- Runbook War Room present et utilisable:
  - `docs/blackfriday/demo-war-room-runbook.md`
- Contenu cle:
  - roles (Incident Commander, Platform Lead, App Lead, Observability Lead, Scribe)
  - niveaux de severite (`SEV-1`, `SEV-2`, `SEV-3`)
  - boucle standard de gestion d'incident
  - template de communication
  - template de post-mortem

#### Commandes/usage (pas a pas)
1. Ouvrir le runbook avant chaque repetition.
2. Assigner 1 responsable par role.
3. Demarrer un journal d'incident des la premiere alerte.
4. Publier un point de situation toutes les 15 minutes.

#### Problemes possibles et approche
- Probleme: confusion de responsabilites.
  - Approche: role unique, escalation explicite par SEV.
- Probleme: manque de trace temporelle.
  - Approche: scribe dedie + timeline obligatoire.

#### Resultat
- [A renseigner] runbook execute, roles confirmes, cadence de communication tenue.

#### Conclusion partielle
- La procedure incident est standardisee et prete pour la simulation finale.

---

### 3.5 Preparation de la War Room

#### Ce que nous avons implemente
- Cadre operationnel War Room:
  - roles definis
  - severites definies
  - metriques minimales imposees
  - cadence de communication imposee

#### Checklist operationnelle
1. Dashboards ouverts (Grafana, logs, HPA, nodes).
2. Canal de communication incident actif.
3. Commandes de mitigation preparees.
4. Template de communication pre-rempli.
5. Post-mortem template disponible.

#### Problemes possibles et approche
- Probleme: decisions tardives.
  - Approche: seuils d'alerte et criteres d'escalade pre-definis.

#### Resultat
- [A renseigner] War Room executee sans blocage organisationnel.

#### Conclusion partielle
- L'organisation est prete pour une gestion d'incident en charge elevee.

---

## 4) Recap technique des livrables implementes

### Fichiers scripts
- `scripts/blackfriday/week3-chaos-drill.sh`
- `scripts/blackfriday/week3-70k-rehearsal.sh`

### Fichiers Terraform modifies (optimisation cout)
- `terraform/aws-module1/variables.tf`
- `terraform/aws-module1/main.tf`
- `terraform/aws-module1/modules/eks/variables.tf`
- `terraform/aws-module1/modules/eks/main.tf`
- `terraform/aws-module1/terraform.tfvars.example`

### Fichiers runbook / docs
- `docs/blackfriday/demo-war-room-runbook.md`
- `docs/blackfriday/week3-pre-blackfriday.md`
- `docs/blackfriday/week3_livrable.md`

---

## 5) Conclusion Week 3

### Statut propose
- `PASS_WITH_RESERVATIONS` (a confirmer apres execution complete des drills et du 70K final de validation)

### Pourquoi
- Les moyens techniques sont en place (chaos, cout, repetition 70K, runbook, war room).
- Les procedures sont formalisees.
- Les scripts rendent l'execution reproductible.

### Reserves a lever
1. Stabilite post-charge sur certains services critiques.
2. Mesure chifree definitive du cout sous repetition.
3. Validation finale des KPI SLO/SLA pendant le 70K.

### Decision finale Week 3
- [A renseigner en fin de semaine]
