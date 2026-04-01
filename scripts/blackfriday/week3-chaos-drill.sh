#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  week3-chaos-drill.sh pod-delete <app> [count]
  week3-chaos-drill.sh rollout-restart <deployment>
  week3-chaos-drill.sh scale-pulse <deployment> [down_replicas] [sleep_seconds]

Environment variables:
  NAMESPACE  Kubernetes namespace (default: onlineboutique)

Examples:
  NAMESPACE=onlineboutique ./scripts/blackfriday/week3-chaos-drill.sh pod-delete frontend 1
  ./scripts/blackfriday/week3-chaos-drill.sh rollout-restart recommendationservice
  ./scripts/blackfriday/week3-chaos-drill.sh scale-pulse frontend 0 60
USAGE
}

require_binary() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Error: required binary '$1' is not installed." >&2
    exit 1
  fi
}

timestamp() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

pod_delete() {
  local namespace="$1"
  local app="$2"
  local count="$3"

  mapfile -t pods < <(kubectl -n "$namespace" get pods -l "app=${app}" -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}')

  if [[ "${#pods[@]}" -eq 0 ]]; then
    echo "No pod found for app=${app} in namespace=${namespace}" >&2
    exit 1
  fi

  local i=0
  for pod in "${pods[@]}"; do
    echo "[$(timestamp)] deleting pod ${pod}"
    kubectl -n "$namespace" delete pod "$pod" --wait=false
    i=$((i + 1))
    if [[ "$i" -ge "$count" ]]; then
      break
    fi
  done

  echo "[$(timestamp)] current pods for app=${app}:"
  kubectl -n "$namespace" get pods -l "app=${app}" -o wide
}

rollout_restart() {
  local namespace="$1"
  local deployment="$2"

  echo "[$(timestamp)] rollout restart deployment/${deployment}"
  kubectl -n "$namespace" rollout restart "deployment/${deployment}"
  kubectl -n "$namespace" rollout status "deployment/${deployment}" --timeout=300s
}

scale_pulse() {
  local namespace="$1"
  local deployment="$2"
  local down_replicas="$3"
  local sleep_seconds="$4"

  local original
  original="$(kubectl -n "$namespace" get deployment "$deployment" -o jsonpath='{.spec.replicas}')"
  original="${original:-1}"

  echo "[$(timestamp)] scale deployment/${deployment} from ${original} to ${down_replicas}"
  kubectl -n "$namespace" scale "deployment/${deployment}" --replicas="$down_replicas"
  sleep "$sleep_seconds"
  echo "[$(timestamp)] scale deployment/${deployment} back to ${original}"
  kubectl -n "$namespace" scale "deployment/${deployment}" --replicas="$original"
  kubectl -n "$namespace" rollout status "deployment/${deployment}" --timeout=300s
}

main() {
  require_binary kubectl

  if [[ $# -lt 2 ]]; then
    usage
    exit 1
  fi

  local namespace="${NAMESPACE:-onlineboutique}"
  local action="$1"
  shift

  case "$action" in
    pod-delete)
      local app="$1"
      local count="${2:-1}"
      pod_delete "$namespace" "$app" "$count"
      ;;
    rollout-restart)
      local deployment="$1"
      rollout_restart "$namespace" "$deployment"
      ;;
    scale-pulse)
      local deployment="$1"
      local down_replicas="${2:-0}"
      local sleep_seconds="${3:-45}"
      scale_pulse "$namespace" "$deployment" "$down_replicas" "$sleep_seconds"
      ;;
    *)
      usage
      exit 1
      ;;
  esac
}

main "$@"
