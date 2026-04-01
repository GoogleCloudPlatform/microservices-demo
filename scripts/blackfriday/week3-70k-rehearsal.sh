#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  week3-70k-rehearsal.sh start
  week3-70k-rehearsal.sh stop
  week3-70k-rehearsal.sh status
  week3-70k-rehearsal.sh logs

Environment variables:
  NAMESPACE      Kubernetes namespace (default: onlineboutique)
  DEPLOYMENT     Load generator deployment (default: loadgenerator)
  RATE_OVERRIDE  Optional RATE override for safer ramp-up (default: 100)

Examples:
  NAMESPACE=onlineboutique ./scripts/blackfriday/week3-70k-rehearsal.sh start
  ./scripts/blackfriday/week3-70k-rehearsal.sh status
  ./scripts/blackfriday/week3-70k-rehearsal.sh stop
USAGE
}

require_binary() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Error: required binary '$1' is not installed." >&2
    exit 1
  fi
}

start_rehearsal() {
  local namespace="$1"
  local deployment="$2"
  local rate_override="$3"

  echo "Applying week3-70k profile on ${namespace}/${deployment}"
  NAMESPACE="$namespace" DEPLOYMENT="$deployment" ./scripts/blackfriday/set-load-profile.sh week3-70k

  echo "Applying safer RATE=${rate_override} for progressive ramp-up"
  kubectl -n "$namespace" set env "deployment/${deployment}" RATE="$rate_override" FRONTEND_ADDR=frontend:80

  echo "Scaling load generator up"
  kubectl -n "$namespace" scale "deployment/${deployment}" --replicas=1
  kubectl -n "$namespace" rollout status "deployment/${deployment}" --timeout=600s

  cat <<EOF
Rehearsal started.

Suggested live monitoring:
  kubectl -n ${namespace} get hpa -w
  kubectl get nodes -w
  kubectl top nodes
  kubectl -n ${namespace} logs deploy/${deployment} -f --tail=120
EOF
}

stop_rehearsal() {
  local namespace="$1"
  local deployment="$2"

  kubectl -n "$namespace" scale "deployment/${deployment}" --replicas=0
  kubectl -n "$namespace" get "deployment/${deployment}" -o wide
}

status_rehearsal() {
  local namespace="$1"
  local deployment="$2"

  kubectl -n "$namespace" get "deployment/${deployment}" -o wide
  kubectl -n "$namespace" get hpa
  kubectl top nodes || true
}

logs_rehearsal() {
  local namespace="$1"
  local deployment="$2"
  local pod

  pod="$(kubectl -n "$namespace" get pods -l app=loadgenerator -o jsonpath='{.items[0].metadata.name}')"
  if [[ -z "$pod" ]]; then
    echo "No loadgenerator pod found in namespace ${namespace}" >&2
    exit 1
  fi

  kubectl -n "$namespace" logs "$pod" -c main --since=5m
}

main() {
  require_binary kubectl

  if [[ $# -ne 1 ]]; then
    usage
    exit 1
  fi

  local namespace="${NAMESPACE:-onlineboutique}"
  local deployment="${DEPLOYMENT:-loadgenerator}"
  local rate_override="${RATE_OVERRIDE:-100}"
  local action="$1"

  case "$action" in
    start)
      start_rehearsal "$namespace" "$deployment" "$rate_override"
      ;;
    stop)
      stop_rehearsal "$namespace" "$deployment"
      ;;
    status)
      status_rehearsal "$namespace" "$deployment"
      ;;
    logs)
      logs_rehearsal "$namespace" "$deployment"
      ;;
    *)
      usage
      exit 1
      ;;
  esac
}

main "$@"
