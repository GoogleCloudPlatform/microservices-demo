## Overview
This document describes building and deploying the microservices demo application(`Online Boutique`) to Cloud Run.

Some objectives:

- Minimize code changes.
- Ensure the internal microservices are private and keep the network traffic inside the Google network (serverless VPC connectors will be used).
- Redis cache will be deployed to [Memorystore(Redis)](https://cloud.google.com/memorystore/docs/redis).
- Use Infrastructure-as-code([CDKTF](https://www.terraform.io/cdktf)) to deploy the solution.

## Architecture after deployment

![Architecture](../pulumi/microservices-cloudrun-arch.svg)

## Clone the repository

```
git clone -b pulumi-cloudrun-one-ilb git@github.com:shenxiang-demo/microservices-demo.git
```

## Install CDKTF and libraries

```
cd microservices-demo/serverless/cdktf
npm install --global cdktf-cli@latest
npm install
```

Please read [CDKTF doc](https://learn.hashicorp.com/tutorials/terraform/cdktf-install) for more details.

## Config project

```
export PROJECT_ID=<YOUR GCP PROJECT ID>
gcloud config set project $PROJECT_ID
gcloud auth application-default login
gcloud auth configure-docker
```
## Create the stack
```
cdktf apply --auto-approve
```

By default, the service deployments will use the container images listed in the [release/kubernetes-manifests.yaml](../../release/kubernetes-manifests.yaml) file.

If you want to build the container images from the source code, you can set the flag `buildImageFromSrc` to true in the [cdktf.json](./cdktf.json) file.

__Note:__ However, this step will __NOT__ work in CloudShell since CloudShell doesn't have sufficient disk space to build all the container images.

## Clean up

If you don't want to delete the whole project, run the following command to delete the resources:

```
cdktf destroy --auto-approve
```