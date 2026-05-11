#!/usr/bin/env bash
# Tear down a training cohort.
#
#   ./teardown.sh attendees.csv         # reads same CSV used to provision
#   ./teardown.sh --all                 # nuke every attendee-* namespace
#
# Deletes namespaces (which cascades to Helm releases, Ingresses, secrets)
# and the attendee/* git branches on origin. Leaves training-system,
# reflector, and the wildcard cert in place.
set -euo pipefail

confirm() {
  read -r -p "${1:-Are you sure?} [y/N] " ans
  [[ "$ans" =~ ^[Yy]$ ]]
}

if [[ "${1:-}" == "--all" ]]; then
  namespaces=$(kubectl get ns -l purpose=training -o jsonpath='{.items[*].metadata.name}')
  branches=$(git ls-remote --heads origin 'attendee/*' | awk '{print $2}' | sed 's|refs/heads/||')
  echo "Will delete namespaces: $namespaces"
  echo "Will delete branches:   $branches"
  confirm "Proceed?" || exit 1
  for ns in $namespaces; do kubectl delete ns "$ns" --wait=false; done
  for br in $branches; do git push origin --delete "$br" || true; done
  exit 0
fi

CSV="${1:-}"
[[ -f "$CSV" ]] || { echo "usage: $0 <attendees.csv> | --all" >&2; exit 2; }

while IFS=, read -r name _bug; do
  [[ "$name" == "name" ]] && continue
  echo "deleting attendee-$name and origin/attendee/$name"
  kubectl delete ns "attendee-$name" --wait=false --ignore-not-found
  git push origin --delete "attendee/$name" 2>/dev/null || true
done < "$CSV"
