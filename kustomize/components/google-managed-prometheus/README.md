# Google Managed Prometheus

## Overview
This `kustomize` component enables a [pod monitoring](https://cloud.google.com/stackdriver/docs/managed-prometheus/setup-managed#gmp-pod-monitoring) resource for clusters with [Google Managed Prometheus](https://cloud.google.com/stackdriver/docs/managed-prometheus) enabled.

The pod monitoring resource will then scrape Prometheus metrics endpoints on configured microservices.  Note that metrics are not exported by default, but can be enabled using the [Google Cloud Operations](../google-cloud-operations/) `kustomize` component.

## Enabling Google Managed Prometheus
[Google Managed Prometheus](https://cloud.google.com/stackdriver/docs/managed-prometheus) can be enabled on [new or existing clusters](https://cloud.google.com/stackdriver/docs/managed-prometheus/setup-managed#config-mgd-collection), and is enabled by default on GKE autopilot 1.25 and later.

To create a new cluster with Google Managed Prometheus enabled, pass the `--enable-managed-prometheus` flag, for example:

```
ZONE=us-central1-b
gcloud container clusters create onlineboutique \
    --project=${PROJECT_ID} --zone=${ZONE} \
    --machine-type=e2-standard-2 --num-nodes=4 \
   --enable-managed-prometheus 
```

To enable Google Managed Prometheus on an existing cluster, find the option in the [GKE clusters dashboard](https://cloud.google.com/stackdriver/docs/managed-prometheus/setup-managed#gke-clusters-dashboard) or use the `gcloud` CLI:

```
gcloud container clusters update ${CLUSTER_NAME} --enable-managed-prometheus --zone ${ZONE}
```

When the custom pod monitoring resource in this component is applied, Managed Prometheus will automatically scrape metrics from Online Boutique, which you can then see in the [Metrics Explorer](https://console.cloud.google.com/monitoring/metrics-explorer), or query using PromQL.