# Black Friday - Jours 1-2 Demo (Budget cible: 200 EUR)

Objectif: executer la simulation finale en conditions reelles, gerer les incidents en War Room, puis produire un post-mortem exploitable.

## 1) Perimetre et objectifs

- Jour 1:
  - montee en charge progressive jusqu'a 90K utilisateurs
  - gestion des incidents injectes en temps reel
  - pilotage War Room pendant 8 heures
- Jour 2:
  - analyse des incidents
  - post-mortem
  - presentation des resultats

## 2) Acronymes utilises

- HPA: Horizontal Pod Autoscaler
- MTTR: Mean Time To Recovery
- SLO: Service Level Objective
- SLA: Service Level Agreement
- SEV: Severity (niveau de gravite)

## 3) Prerequis avant le Jour 1

1. Runbook War Room finalise: `docs/blackfriday/demo-war-room-runbook.md`
2. Roles assignes: Incident Commander, Platform Lead, App Lead, Observability Lead, Scribe
3. Dashboards ouverts: HPA, nodes, pods pending, latence, erreurs
4. Cluster Autoscaler sans erreur IAM bloquante (`AccessDenied`)
5. Commandes de mitigation pretes (scale, rollout restart, stop charge)
6. Canal de communication incident actif (cadence de mise a jour: 15 min)

## 4) Jour 1 - Simulation 8h (90K)

### 4.1 Demarrage

```bash
cd /home/naxxer/Videos/microservices-project
./scripts/blackfriday/demo-day-control.sh start
```

### 4.2 Plan de montee progressive (recommande)

- Phase 1 (0h00-0h45): `RATE=100`
- Phase 2 (0h45-1h30): `RATE=250`
- Phase 3 (1h30-2h15): `RATE=500`
- Phase 4 (2h15-3h00): `RATE=800`
- Phase 5 (3h00-3h45): `RATE=1100`
- Phase 6 (3h45-4h30): `RATE=1450`
- Phase 7 (4h30-5h15): `RATE=1800`
- Phase 8 (5h15-8h00): `RATE=2250` (profil 90K)

Commandes:

```bash
./scripts/blackfriday/demo-day-control.sh set-rate 250
./scripts/blackfriday/demo-day-control.sh set-rate 500
./scripts/blackfriday/demo-day-control.sh set-rate 800
./scripts/blackfriday/demo-day-control.sh set-rate 1100
./scripts/blackfriday/demo-day-control.sh set-rate 1450
./scripts/blackfriday/demo-day-control.sh set-rate 1800
./scripts/blackfriday/demo-day-control.sh set-rate 2250
```

### 4.3 Monitoring live pendant chaque phase

```bash
kubectl -n onlineboutique get hpa -w
kubectl get nodes -L capacity-type,workload-tier -w
kubectl -n onlineboutique get pods -w
kubectl -n kube-system logs deployment/cluster-autoscaler-aws-cluster-autoscaler --since=10m | egrep -i "AccessDenied|No expansion options|backoff" || true
```

### 4.4 Gestion des incidents injectes (formateur)

Boucle standard:
1. Detecter et classer SEV
2. Assigner owner et action
3. Communiquer l'impact et ETA
4. Mitiger
5. Verifier retour stable
6. Enregistrer timeline + MTTR

Exemples de mitigation:

```bash
# Arret charge (stabilisation d'urgence)
./scripts/blackfriday/demo-day-control.sh stop

# Redemarrage service cible
kubectl -n onlineboutique rollout restart deployment/<service>

# Observation rapide
kubectl -n onlineboutique get pods
kubectl -n onlineboutique get hpa
```

### 4.5 Cloture Jour 1

```bash
./scripts/blackfriday/demo-day-control.sh stop
./scripts/blackfriday/demo-day-control.sh status
```

A archiver:
- timeline incidents (heure, impact, action, resultat)
- MTTR par incident
- screenshots/captures HPA et dashboards
- erreurs critiques et resolution

## 5) Jour 2 - Post-mortem et presentation

### 5.1 Structure post-mortem

1. Resume executif (1 page)
2. Chronologie des incidents
3. Impact metier et technique
4. Causes racines
5. Ce qui a bien fonctionne
6. Ce qui a echoue
7. Actions correctives immediates
8. Actions preventives long terme

### 5.2 Resultats minimaux a presenter

- capacite atteinte (objectif 90K)
- stabilite pendant incidents injectes
- MTTR global et par type d'incident
- etat des reserves (ex: `No expansion options`)
- position finale: `PASS` ou `PASS_WITH_RESERVATIONS`

## 6) Budget demo (200 EUR) - garde-fous

- `loadgenerator` a `0` hors fenetre de test
- pas de surprovisionnement permanent apres demo
- suppression des ressources temporaires non necessaires
- verification des nodes Spot inutilises en fin de session

## 7) Livrable attendu (fin Jours 1-2)

- simulation 8h executee et tracee
- incidents geres via War Room
- post-mortem documente
- decision finale de readiness pour Black Friday
