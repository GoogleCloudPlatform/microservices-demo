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

if [ -n "$3" ]; then
    BRANCH=$3
else
    echo "Must provide a git branch."
    exit 
fi

# build and push images 
./build-push.sh $DOCKER_REPO $TAG


# update yaml 
./inject-yaml.sh $DOCKER_REPO $TAG


# git tag 
echo "Pushing git tag..."
git tag $TAG 
git push --tags

# push updated manifests 
echo "Commiting to $BRANCH..."
git add .
git commit -m "Tagged release $TAG"
git push origin $BRANCH

echo "✅ Successfully tagged release $TAG"
