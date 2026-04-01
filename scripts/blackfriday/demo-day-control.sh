#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage:
  demo-day-control.sh start
  demo-day-control.sh set-rate <rate>
  demo-day-control.sh status
  demo-day-control.sh logs
  demo-day-control.sh stop
  demo-day-control.sh ramp-plan

Environment variables:
  NAMESPACE   Kubernetes namespace (default: onlineboutique)
  DEPLOYMENT  Load generator deployment name (default: loadgenerator)
  USERS       Target concurrent users (default: 90000)
  START_RATE  Initial safe RATE for start (default: 100)

Examples:
  ./scripts/blackfriday/demo-day-control.sh start
  ./scripts/blackfriday/demo-day-control.sh set-rate 500
  ./scripts/blackfriday/demo-day-control.sh status
  ./scripts/blackfriday/demo-day-control.sh stop
USAGE
}

require_binary() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Error: required binary '$1' is not installed." >&2
    exit 1
  fi
}

now_utc() {
  date -u +"%Y-%m-%dT%H:%M:%SZ"
}

print_ramp_plan() {
  cat <<'PLAN'
Recommended 8h progressive ramp (manual checkpoints):
  Phase 1  (0h00-0h45): RATE=100
  Phase 2  (0h45-1h30): RATE=250
  Phase 3  (1h30-2h15): RATE=500
  Phase 4  (2h15-3h00): RATE=800
  Phase 5  (3h00-3h45): RATE=1100
  Phase 6  (3h45-4h30): RATE=1450
  Phase 7  (4h30-5h15): RATE=1800
  Phase 8  (5h15-8h00): RATE=2250 (target 90K profile)

At each phase:
  1) set RATE
  2) observe HPA + nodes for 10-15 minutes
  3) if unstable, hold current RATE and apply mitigation
PLAN
}

start_demo() {
  local namespace="$1"
  local deployment="$2"
  local users="$3"
  local start_rate="$4"

  echo "[$(now_utc)] apply demo-90k baseline (USERS=${users})"
  kubectl -n "$namespace" set env "deployment/${deployment}" USERS="$users" RATE="$start_rate" FRONTEND_ADDR=frontend:80

  echo "[$(now_utc)] scale load generator to 1 replica"
  kubectl -n "$namespace" scale "deployment/${deployment}" --replicas=1
  kubectl -n "$namespace" rollout status "deployment/${deployment}" --timeout=600s

  echo
  echo "Demo Day started with safe RATE=${start_rate}."
  print_ramp_plan
}

set_rate() {
  local namespace="$1"
  local deployment="$2"
  local rate="$3"

  echo "[$(now_utc)] set RATE=${rate} on ${namespace}/${deployment}"
  kubectl -n "$namespace" set env "deployment/${deployment}" RATE="$rate"
  kubectl -n "$namespace" rollout status "deployment/${deployment}" --timeout=600s
}

status_demo() {
  local namespace="$1"
  local deployment="$2"

  echo "=== Deployment ==="
  kubectl -n "$namespace" get "deployment/${deployment}" -o wide
  echo
  echo "=== HPA ==="
  kubectl -n "$namespace" get hpa
  echo
  echo "=== Nodes ==="
  kubectl get nodes -L capacity-type,workload-tier
  echo
  echo "=== Pending/Error Pods (onlineboutique) ==="
  kubectl -n "$namespace" get pods | egrep "Pending|CrashLoopBackOff|Error|OOMKilled" || true
}

logs_demo() {
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

stop_demo() {
  local namespace="$1"
  local deployment="$2"

  echo "[$(now_utc)] scale load generator to 0"
  kubectl -n "$namespace" scale "deployment/${deployment}" --replicas=0
  kubectl -n "$namespace" get "deployment/${deployment}" -o wide
}

main() {
  require_binary kubectl

  if [[ $# -lt 1 ]]; then
    usage
    exit 1
  fi

  local namespace="${NAMESPACE:-onlineboutique}"
  local deployment="${DEPLOYMENT:-loadgenerator}"
  local users="${USERS:-90000}"
  local start_rate="${START_RATE:-100}"
  local action="$1"

  case "$action" in
    start)
      start_demo "$namespace" "$deployment" "$users" "$start_rate"
      ;;
    set-rate)
      if [[ $# -ne 2 ]]; then
        usage
        exit 1
      fi
      set_rate "$namespace" "$deployment" "$2"
      ;;
    status)
      status_demo "$namespace" "$deployment"
      ;;
    logs)
      logs_demo "$namespace" "$deployment"
      ;;
    stop)
      stop_demo "$namespace" "$deployment"
      ;;
    ramp-plan)
      print_ramp_plan
      ;;
    *)
      usage
      exit 1
      ;;
  esac
}

main "$@"
