#!/usr/bin/env bash
# Sample script for creating a cluster for the app to test with Cloud Run for Anthos

CLUSTER="${CLUSTER:-cluster-1}"
ZONE="${ZONE:-us-central1-c}"
NODES="${NODES:-3}"
MACHINE="${MACHINE:-n1-standard-2}"
CHANNEL="${CHANNEL:-regular}"

gcloud beta container clusters create "${CLUSTER}" \
  --addons CloudRun,HttpLoadBalancing \
  --zone "${ZONE}" --num-nodes "${NODES}" --machine-type "${MACHINE}" \
  --release-channel "${CHANNEL}" \
  --enable-ip-alias \
  --enable-stackdriver-kubernetes
