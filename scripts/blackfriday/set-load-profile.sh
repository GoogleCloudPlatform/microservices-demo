#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<USAGE
Usage:
  $(basename "$0") <profile>
  $(basename "$0") custom <users> <rate>

Profiles:
  week1-1k, week2-5k, week2-20k, week2-50k, week3-70k, demo-90k

Environment variables:
  NAMESPACE   Kubernetes namespace (default: default)
  DEPLOYMENT  Load generator deployment name (default: loadgenerator)
USAGE
}

require_binary() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Error: required binary '$1' is not installed." >&2
    exit 1
  fi
}

profile_to_values() {
  case "$1" in
    week1-1k)  echo "1000 25" ;;
    week2-5k)  echo "5000 125" ;;
    week2-20k) echo "20000 500" ;;
    week2-50k) echo "50000 1250" ;;
    week3-70k) echo "70000 1750" ;;
    demo-90k)  echo "90000 2250" ;;
    *) return 1 ;;
  esac
}

main() {
  require_binary kubectl

  if [[ $# -lt 1 ]]; then
    usage
    exit 1
  fi

  local namespace="${NAMESPACE:-default}"
  local deployment="${DEPLOYMENT:-loadgenerator}"
  local profile="$1"
  local users
  local rate

  if [[ "$profile" == "custom" ]]; then
    if [[ $# -ne 3 ]]; then
      usage
      exit 1
    fi
    users="$2"
    rate="$3"
  else
    if ! read -r users rate < <(profile_to_values "$profile"); then
      echo "Error: unknown profile '$profile'." >&2
      usage
      exit 1
    fi
  fi

  echo "Applying load profile to ${namespace}/${deployment}: USERS=${users}, RATE=${rate}"

  kubectl -n "$namespace" set env deployment/"$deployment" USERS="$users" RATE="$rate"
  kubectl -n "$namespace" rollout status deployment/"$deployment"

  echo "Current loadgenerator env values:"
  kubectl -n "$namespace" get deployment "$deployment" -o jsonpath='{range .spec.template.spec.containers[?(@.name=="main")].env[*]}{.name}={.value}{"\n"}{end}' | grep -E '^(USERS|RATE)='
}

main "$@"
