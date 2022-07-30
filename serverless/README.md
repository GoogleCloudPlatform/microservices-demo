## Overview
This document describes building and deploying the microservices demo application(`Online Boutique`) to Cloud Run. 

[Pulumi](https://www.pulumi.com/) is used to create the infrastructure, build and deploy the application.

You can find the Pulumi code under this directory. Minor code changes have been made to allow gRPC with TLS since Cloud Run only supports HTTPS. You can see a code diff [here](https://github.com/GoogleCloudPlatform/microservices-demo/compare/main...shenxiang-demo:microservices-demo:cloudrun-pulumi-direct).

__Note:__ The steps described in the doc will __NOT__ work in CloudShell since CloudShell doesn't have sufficient disk space to build all the container images.

## Clone the repository

```
git clone -b cloudrun-pulumi-direct https://github.com/shenxiang-demo/microservices-demo
```

## Install pulumi

```
cd microservices-demo/serverless/pulumi
npm install
curl -fsSL https://get.pulumi.com | sh
export PATH=$PATH:$HOME/.pulumi/bin
```

## Config project

```
export PROJECT_ID=<YOUR GCP PROJECT ID>
gcloud config set project $PROJECT_ID
gcloud auth application-default login
gcloud auth configure-docker
```

## Create a bucket as a [backend](https://www.pulumi.com/docs/intro/concepts/state/#logging-into-the-google-cloud-storage-backend)

```
gsutil mb gs://pulumi-${PROJECT_ID}

pulumi login gs://pulumi-${PROJECT_ID}
pulumi config set gcp:project $PROJECT_ID
```

## Create a new dev stack
```
pulumi stack init dev
```
You can press `return` to skip the passphrase.

## Create the stack
```
pulumi up -y
```