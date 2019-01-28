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


for dir in ./src/*/    
do
    # build image  
    svcname=$(basename $dir)
    image="$DOCKER_REPO/$svcname:$TAG"
    echo "Building and pushing $image..." 
    docker build -t $image -f $dir/Dockerfile $dir 

    # push image 
    docker push $image 
done