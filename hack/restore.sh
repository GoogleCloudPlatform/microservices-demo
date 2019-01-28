#!/bin/bash

manifestfile="./release/kubernetes-manifests/demo.yaml"

# restore release/ manifest images to skaffold default, eg. "adservice"
for dir in ./src/*/    
do
    svcname=$(basename $dir)
    image="$DOCKER_REPO/$svcname:$TAG"

    pattern=".*image:.*$svcname.*"
    replace="        image: $svcname"
    sed -i '' "s|$pattern|$replace|g" $manifestfile 
done