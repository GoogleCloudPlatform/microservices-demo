# Runbook get demo up and running

1. Update Variables in Makefile

## GKE Cluster
2. Create a cluster that isn't using Istio enabled.

    `make cluster.create`

> Takes a few minutes

3. Get Cluster creds and set kubeconfig

    `make get.creds`

4.  Confirm connection to the cluster

    `kubectl get nodes`

### Istio Setup

5. Create istio-system namespace

   `make ns.create.istio-system`

6. Initliase Istio

    `make istio.init`

7. Enable istio sidecar injection to default namesapce

    `make ns.istio.enabled`

8. Create Istio template (if no istio-demo.yaml)

    `make istio.template`

9. Deploy Istio

    `make istio.deploy`
> Wait for containers for istio to be deployed.

    `kubectl get pods -n istio-system`

## Application

10. Deploy Istio configured app with tracing turned on

     `make skaffold.run.gcp.istio`