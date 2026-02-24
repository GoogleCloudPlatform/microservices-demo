#!/usr/bin/env bash
set -e

ACTION="${1:-apply}"
ENVS="${2:-all}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENVS_DIR="$SCRIPT_DIR/environments"

run_terraform() {
  local env="$1"
  local action="$2"
  echo ""
  echo "========== $env: terraform $action =========="
  cd "$ENVS_DIR/$env"
  terraform init -input=false
  terraform "$action" -auto-approve
}

if [ "$ACTION" = "apply" ]; then
  if [ "$ENVS" = "all" ] || [ "$ENVS" = "cluster" ]; then
    run_terraform cluster apply
  fi
  if [ "$ENVS" = "all" ] || [ "$ENVS" = "staging" ]; then
    run_terraform staging apply
  fi
  if [ "$ENVS" = "all" ] || [ "$ENVS" = "production" ]; then
    run_terraform production apply
  fi

  echo ""
  echo "========== Done =========="
  echo "Frontend URLs (may take 1-2 min for IP):"
  echo "  Staging:    kubectl get svc frontend-external -n staging -o jsonpath='{.status.loadBalancer.ingress[0].ip}'"
  echo "  Production: kubectl get svc frontend-external -n production -o jsonpath='{.status.loadBalancer.ingress[0].ip}'"

elif [ "$ACTION" = "destroy" ]; then
  if [ "$ENVS" = "all" ] || [ "$ENVS" = "staging" ]; then
    run_terraform staging destroy
  fi
  if [ "$ENVS" = "all" ] || [ "$ENVS" = "production" ]; then
    run_terraform production destroy
  fi
  if [ "$ENVS" = "all" ] || [ "$ENVS" = "cluster" ]; then
    run_terraform cluster destroy
  fi

  echo ""
  echo "========== Destroy complete =========="

else
  echo "Usage: $0 [apply|destroy] [all|cluster|staging|production]"
  echo ""
  echo "Examples:"
  echo "  $0 apply              # apply all (cluster -> staging -> production)"
  echo "  $0 apply staging      # apply only staging"
  echo "  $0 destroy            # destroy all (staging -> production -> cluster)"
  echo "  $0 destroy production # destroy only production"
  exit 1
fi
