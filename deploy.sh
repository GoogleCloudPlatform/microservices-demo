#!/bin/bash
WORKDIR=$(pwd)

# provision infrastructure
cd terraform
terraform injt
terrafrom apply

# setup kubectx
git clone https://github.com/ahmetb/kubectx $WORKDIR/kubectx
export PATH=$PATH:$WORKDIR/kubectx

# get cluster credentials
gcloud container clusters get-credentials --zone=europe-west1-b cluster-europe-west1;
gcloud container clusters get-credentials --zone=europe-north1-b cluster-europe-north1;

# change context names
kubectx west=gke_co-libry-services_europe-west1-b_cluster-europe-west1
kubectx north=gke_co-libry-services_europe-north1-b_cluster-europe-north1

# configure istio certificates on both clusters
cd ${WORKDIR}
export ISTIO_VERSION=1.10.0
curl -L https://istio.io/downloadIstio | ISTIO_VERSION=${ISTIO_VERSION} TARGET_ARCH=x86_64 sh -
cd istio-${ISTIO_VERSION}
export PATH=$PWD/bin:$PATH
cd ..

clusters=( "north" "west" )
for cluster in "${clusters[@]}"
do
    echo "${cluster}"
    kubectl --context $cluster create namespace istio-system
    kubectl --context $cluster create secret generic cacerts -n istio-system \
    --from-file=${WORKDIR}/istio-${ISTIO_VERSION}/samples/certs/ca-cert.pem \
    --from-file=${WORKDIR}/istio-${ISTIO_VERSION}/samples/certs/ca-key.pem \
    --from-file=${WORKDIR}/istio-${ISTIO_VERSION}/samples/certs/root-cert.pem \
    --from-file=${WORKDIR}/istio-${ISTIO_VERSION}/samples/certs/cert-chain.pem;
done

# install istio for west cluster
kubectl --context=west label namespace istio-system topology.istio.io/network=network1
istioctl install --context=west -f istio-manifests/istio-west.yaml -y
kubectl --context=west apply -n istio-system -f \
    ${WORKDIR}/istio-${ISTIO_VERSION}/samples/multicluster/expose-services.yaml

# install istio for east cluster
kubectl --context=north label namespace istio-system topology.istio.io/network=network2
istioctl install --context=north -f istio-manifests/istio-north.yaml -y
kubectl --context=north apply -n istio-system -f \
    ${WORKDIR}/istio-${ISTIO_VERSION}/samples/multicluster/expose-services.yaml

# enable endpoint discovery
istioctl x create-remote-secret \
    --context=north \
    --name=north | \
    kubectl apply -f - --context=west

istioctl x create-remote-secret \
    --context=west \
    --name=west | \
    kubectl apply -f - --context=north


# create namespace on clusters
kubectl --context north create namespace online-boutique
kubectl --context west create namespace online-boutique

# label namespace for automatic sidecar injection
kubectl --context north label namespace online-boutique istio-injection=enabled
kubectl --context west label namespace online-boutique istio-injection=enabled

# deploy application
kubectl --context north -n online-boutique apply -f $WORKDIR/istio-manifests/multi-primary/north
kubectl --context west -n online-boutique apply -f $WORKDIR/istio-manifests/multi-primary/west/
