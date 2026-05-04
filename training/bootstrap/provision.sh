#!/usr/bin/env bash
# Provision a training cohort.
#
#   ./provision.sh attendees.csv
#
# Idempotent. Re-runs are safe; existing namespaces, releases, and
# branches are upgraded in place. CSV format: name,bug_id
#
# Prerequisites:
#   - kubectl pointing at the training cluster
#   - helm 3.x
#   - git remote 'origin' set to the fork
#   - training/k8s/training-system.yaml already applied
#   - training/k8s/install-reflector.sh already run
#   - main branch up to date with the fork remote
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
TRAINING_DIR="$REPO_ROOT/training"
DOMAIN="training.gcp.re-cinq.com"
TLS_SECRET="wildcard-training-tls"
CLUSTER_ISSUER="letsencrypt-prod"
INGRESS_CLASS="nginx"
BASE_BRANCH="main"

if [[ $# -ne 1 ]]; then
  echo "usage: $0 <attendees.csv>" >&2
  exit 2
fi
CSV="$1"
[[ -f "$CSV" ]] || { echo "no such file: $CSV" >&2; exit 2; }

mkdir -p "$TRAINING_DIR/handouts"

log() { printf '\033[1;34m[bootstrap]\033[0m %s\n' "$*"; }

# Validate every row first - fail before we mutate anything
log "validating $CSV"
while IFS=, read -r name bug; do
  [[ "$name" == "name" ]] && continue
  [[ -z "$name" || -z "$bug" ]] && { echo "empty name or bug in row: $name,$bug" >&2; exit 1; }
  [[ -d "$TRAINING_DIR/bugs/$bug" ]] || { echo "unknown bug id: $bug (no such dir under training/bugs/)" >&2; exit 1; }
  [[ "$name" =~ ^[a-z][a-z0-9-]{1,30}$ ]] || { echo "invalid attendee name (must be lowercase, alphanumeric+dash, <=31 chars): $name" >&2; exit 1; }
done < "$CSV"

# Process each attendee
while IFS=, read -r name bug; do
  [[ "$name" == "name" ]] && continue

  ns="attendee-$name"
  branch="attendee/$name"
  host="${name}.${DOMAIN}"

  log "==== $name (bug=$bug, namespace=$ns) ===="

  # 1. Namespace + quotas + network policy
  kubectl apply -f - <<EOF
apiVersion: v1
kind: Namespace
metadata:
  name: $ns
  labels:
    purpose: training
    attendee: $name
    cohort: $(date +%Y-%m-%d)
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: training-quota
  namespace: $ns
spec:
  hard:
    requests.cpu: "1"
    requests.memory: 2Gi
    limits.cpu: "3"
    limits.memory: 4Gi
    pods: "20"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: training-defaults
  namespace: $ns
spec:
  limits:
  - type: Container
    default:
      cpu: 200m
      memory: 256Mi
    defaultRequest:
      cpu: 50m
      memory: 64Mi
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny
  namespace: $ns
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
---
# Allow within-namespace traffic, DNS, and HTTPS egress (for image pulls,
# external APIs, etc). Block lateral movement to other namespaces.
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-internal-and-egress
  namespace: $ns
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
  ingress:
  - from:
    - podSelector: {}
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: ingress-nginx
  egress:
  - to:
    - podSelector: {}
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
    ports:
    - port: 53
      protocol: UDP
    - port: 53
      protocol: TCP
  - to:
    - ipBlock:
        cidr: 0.0.0.0/0
        except: [10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16]
EOF

  # 2. Helm install/upgrade the boutique
  helm upgrade --install boutique "$REPO_ROOT/helm-chart" \
    --namespace "$ns" \
    -f "$TRAINING_DIR/values-training.yaml" \
    --wait --timeout 5m

  # 3. Ingress (external-dns picks up host -> Cloud DNS A record;
  #    reflector replicated the wildcard TLS secret into this namespace
  #    so we just reference it by name)
  kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: boutique
  namespace: $ns
  annotations:
    external-dns.alpha.kubernetes.io/hostname: "$host"
spec:
  ingressClassName: $INGRESS_CLASS
  tls:
    - hosts: ["$host"]
      secretName: $TLS_SECRET
  rules:
    - host: $host
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend
                port:
                  number: 80
EOF

  # 4. Branch + bug injection
  git fetch origin "$BASE_BRANCH" >/dev/null
  if git ls-remote --exit-code --heads origin "$branch" >/dev/null 2>&1; then
    log "branch $branch already exists on origin, skipping"
  else
    log "creating branch $branch from origin/$BASE_BRANCH"
    git worktree add --quiet --detach /tmp/training-$name "origin/$BASE_BRANCH"
    (
      cd /tmp/training-$name
      git checkout -b "$branch"
      git apply "$TRAINING_DIR/bugs/$bug/PATCH.diff"
      cp "$TRAINING_DIR/bugs/$bug/BUG_REPORT.md" ./BUG_REPORT.md
      git add -A
      GIT_AUTHOR_NAME="training-bot" GIT_AUTHOR_EMAIL="bot@training.local" \
      GIT_COMMITTER_NAME="training-bot" GIT_COMMITTER_EMAIL="bot@training.local" \
        git commit --quiet -m "training: seed bug ($bug)" -m "Customer ticket in BUG_REPORT.md."
      git push --quiet -u origin "$branch"
    )
    git worktree remove --force /tmp/training-$name
  fi

  # 5. Handout
  cat > "$TRAINING_DIR/handouts/$name.md" <<EOF
# Training handout — $name

## Your environment

| field         | value                                           |
|---------------|-------------------------------------------------|
| URL           | https://$host                                   |
| Repo          | https://github.com/re-cinq/microservices-demo   |
| Your branch   | \`$branch\`                                     |
| Your bug ID   | \`$bug\` (don't share — see what your neighbours got) |

## What we want from you

A customer just opened a ticket about your URL. The ticket is in
\`BUG_REPORT.md\` on your branch. Your job today:

1. Reproduce the issue at $host
2. Use Claude Code to triage it: find the suspected file, understand
   what's wrong, and write an engineer-ready ticket
   (\`ENGINEERING_TICKET.md\` on your branch) with:
   - exact steps to reproduce
   - suspected service + file
   - severity rationale
3. Fix the bug locally, verify in browser at $host after deploying
4. Open a PR from a fix branch into \`$branch\`. Auto-merge will
   redeploy your namespace. Verify the fix went live.

## Local workflow

\`\`\`bash
git clone https://github.com/re-cinq/microservices-demo
cd microservices-demo
git checkout $branch
git checkout -b $branch-fix
# ... use Claude Code to triage, write ticket, fix ...
git push -u origin $branch-fix
gh pr create --base $branch --title "fix: <one line>" --body "Closes ticket. See ENGINEERING_TICKET.md."
\`\`\`

The PR auto-merges on green CI. Watch the GitHub Actions run for the
deploy. Re-test at https://$host once it's green.
EOF

  log "done with $name"
done < "$CSV"

log "all attendees provisioned. handouts written to training/handouts/"
