# Black Friday Survival - Partie 1 (Semaine 1)

Ce guide couvre la premiere partie du cahier des charges: **Setup & Fondations**.

Objectif de la semaine:
- plateforme deployee et stable
- premier test de charge a 1 000 utilisateurs
- documentation de base des choix techniques

## 1. Baseline locale (validation applicative)

Depuis la racine du repo:

```bash
kind create cluster --name blackfriday || true
skaffold run
kubectl get pods
kubectl port-forward deployment/frontend 8080:8080
```

Validation:
- ouvrir `http://localhost:8080`
- verifier que toutes les pages principales repondent

## 2. Premier test de charge 1K users

Activer le composant kustomize dedie:

```bash
cd kustomize
kustomize edit add component components/blackfriday-week1-loadtest
kubectl apply -k .
kubectl get deploy loadgenerator -o yaml | grep -E "USERS|RATE|value"
kubectl logs deploy/loadgenerator --tail=50 -f
```

Validation:
- `USERS=1000` et `RATE=25` dans la spec
- absence d'erreurs massives dans les logs

## 3. Migration AWS (fondations IaC)

Le repo actuel est Google Cloud-first. Pour etre conforme au projet AWS:
- creer un dossier `terraform/aws/` pour les modules VPC/EKS de base
- definir state distant (S3 + DynamoDB lock)
- decrire les variables d'environnement (`AWS_PROFILE`, `AWS_REGION`)

## 4. Monitoring de base

Pour la Semaine 1, viser un niveau minimal:
- metriques cluster (CPU/RAM pods/noeuds)
- taux d'erreur HTTP frontend
- latence p95 frontend

Sortie attendue:
- 1 dashboard operationnel
- 3 alertes simples (latence, erreurs, saturation CPU)

## 5. Livrable Semaine 1

- architecture deployee
- test 1K documente (captures + valeurs)
- decisions initiales tracees (README/ADR)
