SHELL := /bin/bash #--rcfile ~/.bash_profile

# COLORS
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)
TARGET_MAX_CHAR_NUM=20

CLUSTER_NAME=o11y-ob
PROJECTID=tonyh-gke-o11y-anz-openbanking
ZONE=australia-southeast1-a
ISTIO_VERSION=1.5.0

a: help
all: all.cluster all.istio default.app

all.cluster: cluster.create get.creds

all.istio: ns.create.istio-system istio.init crd.wait ns.istio.enabled istio.template istio.deploy

default.app: crd.wait skaffold.run.gcp.istio hipster.istio.rules

crd.wait:
	@kubectl -n istio-system wait --for=condition=complete job --all

## Use Istio Version 1.5.0
istio150:
	PATH=`echo $PATH | sed -e 's/istio-1.3.5/istio-1.5.0/g'`

## Use Istio Version 1.3.5
istio135:
	PATH=`echo $\PATH | sed -e 's/istio-1.5.0/istio-1.3.5/g'`

## Create GKE Cluster with istio enabled
cluster.create.istio:
 	@gcloud container clusters create ${CLUSTER_NAME} --enable-autoupgrade \
	--enable-autoscaling --min-nodes=1 --max-nodes=10 --num-nodes=6 --zone=${ZONE} \
	--addons=Istio --istio-config=auth=MTLS_PERMISSIVE \
	--machine-type=n1-standard-2

## Enable Istio on exisiting cluster
cluster.enable.istio:
	@gcloud beta container clusters update ${CLUSTER_NAME} \
	--update-addons=Istio=ENABLED \
	--zone=${ZONE}

## Increase Cluster Size
cluster.resize:
	@gcloud container clusters resize o11y-ob --node-pool default-pool --num-nodes 6 --zone australia-southeast1-a


## Create GKE Cluster
cluster.create:
	@gcloud container clusters create ${CLUSTER_NAME} --enable-autoupgrade \
	--enable-autoscaling --min-nodes=1 --max-nodes=10 --num-nodes=6 --zone=${ZONE} \
	--machine-type=n1-standard-2

## Get Cluster Creds
get.creds:
	@gcloud container clusters get-credentials ${CLUSTER_NAME} \
	--zone ${ZONE} \
	--project ${PROJECTID}

## Create istio-system namespace
ns.create.istio-system:
	@kubectl create -f istio-manifests/namespace.yaml

## default ns istio enabled
ns.istio.enabled:
	@kubectl label namespace default istio-injection=enabled --overwrite
## default ns istio disabled
ns.istio.disabled:
	@kubectl label namespace default istio-injection=disabled --overwrite

## Installs Istio CRDS
istio.init:
	@helm template istio-${ISTIO_VERSION}/install/kubernetes/helm/istio-init --name istio-init --namespace istio-system | kubectl apply -f -


## Generate Istio Template
istio.template:
	@helm template istio-${ISTIO_VERSION}/install/kubernetes/helm/istio --name istio --namespace istio-system \
	--values istio-${ISTIO_VERSION}/install/kubernetes/helm/istio/values-istio-demo.yaml > istio-manifests/istio-demo.yaml

## Deploy Istio Config
istio.deploy:
	@kubectl apply -f istio-manifests/istio-demo.yaml

## Check if prometheus-stackdriver-sidecar has been deployed
prom.sidecar.exist:
	@kubectl -n istio-system get deployment prometheus -o=go-template='{{$output := "stackdriver-prometheus-sidecar does not exists."}}{{range .spec.template.spec.containers}}{{if eq .name "sidecar"}}{{$output = (print "stackdriver-prometheus-sidecar exists. Image: " .image)}}{{end}}{{end}}{{printf $output}}{{"\n"}}'

## Delete Istio Config
istio.delete:
	@kubectl delete -f istio-manifests/istio-demo.yaml

#####################################################

## Scale Loadgenartor to 0
loadgen.off:
	@kubectl scale deployment loadgenerator --replicas 0

## Scale Loadgenartor to 1
loadgen.on:
	@kubectl scale deployment loadgenerator --replicas 1

## Skaffold GCB
skaffold.dev.gcp:
	@skaffold dev --default-repo=asia.gcr.io/${PROJECTID} -p gcb --tail=false

## Skaffold GCB Istio
skaffold.dev.gcp.istio:
	@skaffold dev --default-repo=asia.gcr.io/${PROJECTID} -p gcb-istio --tail=false

## Skaffold GCB
skaffold.run.gcp:
	@skaffold run --default-repo=asia.gcr.io/${PROJECTID} -p gcb --tail=false

## Skaffold GCB Istio
skaffold.run.gcp.istio:
	@skaffold run --default-repo=asia.gcr.io/${PROJECTID} -p gcb-istio --tail=false

## Skaffold GCB Tracing
skaffold.run.gcp.tracing:
	@skaffold run --default-repo=asia.gcr.io/${PROJECTID} -p gcb-tracing --tail=false

## Skaffold GCB Build
skaffold.build.gcp:
	@skaffold run --default-repo=asia.gcr.io/${PROJECTID} -p gcb --tail=false

## Delete the GKE Cluster
cluster.delete:
	@gcloud container clusters delete ${CLUSTER_NAME} --zone ${ZONE}

## Application Istio Rules
hipster.istio.rules:
	@kubectl apply -f istio-manifests/frontend.yaml
	@kubectl apply -f istio-manifests/frontend-gateway.yaml
	@kubectl apply -f istio-manifests/whitelist-egress-googleapis.yaml

istio.init.delete:
	@helm template istio-${ISTIO_VERSION}/install/kubernetes/helm/istio-init --name istio-init --namespace istio-system | kubectl delete -f -

help:
	@echo ''
	@echo 'Usage:'
	@echo '  $(YELLOW)make$(RESET) $(GREEN)<target>$(RESET)'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\.\_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")-1); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
		} \
	} \
	{ lastLine = $$0 }' $(MAKEFILE_LIST)