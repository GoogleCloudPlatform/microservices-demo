# Use Kustomize to deploy Online Boutique with variants
This page walks you through the deployment options for the [Online Boutique](https://github.com/GoogleCloudPlatform/microservices-demo) sample application on a [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine) cluster using Kustomize.

## What is Kustomize
Kustomize is a Kubernetes native configuration management tool that allows users to customize their manifest configurations without having to copy entire files multiple times. Its commands are built into `kubectl` as `apply -k`. This repo uses Kustomize to enable the deployment variants found [here](https://github.com/GoogleCloudPlatform/microservices-demo#other-deployment-options). More information can be found on the official [Kustomize website](https://kustomize.io/).
