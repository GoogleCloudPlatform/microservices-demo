#!/bin/bash

# set vars 
if [ -n "$1" ]; then
    DOCKER_REPO=$1
else
    echo "Must provide a docker repo"
    exit 
fi

if [ -n "$2" ]; then
    TAG=$2
else
    echo "Must provide a version tag."
    exit 
fi

# inject new tag into the relevant k8s manifest
manifestfile="./release/kubernetes-manifests/demo.yaml"

for dir in ./src/*/    
do
    svcname=$(basename $dir)
    image="$DOCKER_REPO/$svcname:$TAG"

    pattern=".*image:.*$svcname.*"
    replace="        image: $image"
    sed -i '' "s|$pattern|$replace|g" $manifestfile 
done