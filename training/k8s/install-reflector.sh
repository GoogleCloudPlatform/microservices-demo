#!/usr/bin/env bash
# Install emberstack/reflector into the training-system namespace.
# Idempotent: re-running is a no-op upgrade.
#
# Reflector watches Secrets/ConfigMaps annotated with reflection-* and
# copies them into every matching namespace. We use it to replicate the
# wildcard TLS secret into each attendee-<name> namespace without paying
# 30x the Let's Encrypt cert quota.
set -euo pipefail

helm repo add emberstack https://emberstack.github.io/helm-charts >/dev/null
helm repo update emberstack >/dev/null

helm upgrade --install reflector emberstack/reflector \
  --namespace training-system \
  --create-namespace \
  --version 7.1.288 \
  --set resources.requests.cpu=20m \
  --set resources.requests.memory=64Mi \
  --set resources.limits.cpu=100m \
  --set resources.limits.memory=128Mi
