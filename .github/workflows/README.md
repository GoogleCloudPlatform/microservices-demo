# GitHub Actions Workflows

This page describes the CI/CD workflows for the Online Boutique app, which run in [Github Actions](https://github.com/GoogleCloudPlatform/microservices-demo/actions).

## Infrastructure

The CI/CD pipelines for Online Boutique run on standard GitHub-hosted runners (Ubuntu). 

We also host a test GKE cluster, which is where the deploy tests run. Every PR has its own namespace in the cluster.

## Workflows

**Note**: In order for the current CI/CD setup to work on your pull request, you must branch directly off the repo (no forks). This is because the Github secrets necessary for these tests aren't copied over when you fork.

### Code Tests - [ci-pr.yaml](ci-pr.yaml)

These tests run on every commit for every open PR, as well as any commit to main / any release branch. Currently, this workflow runs only Go unit tests.


### Deploy Tests- [ci-pr.yaml](ci-pr.yaml)

These tests run on every commit for every open PR, as well as any commit to main / any release branch. This workflow:

1. Creates a dedicated GKE namespace for that PR, if it doesn't already exist, in the PR GKE cluster.
2. Uses `skaffold run` to build and push the images specific to that PR commit. Then skaffold deploys those images, via `kubernetes-manifests`, to the PR namespace in the test cluster.
3. Tests to make sure all the pods start up and become ready.
4. Gets the LoadBalancer IP for the frontend service.
5. Comments that IP in the pull request, for staging.

### Push and Deploy Latest - [push-deploy](push-deploy.yml)

This is the Continuous Deployment workflow, and it runs on every commit to the main branch. This workflow:

1. Builds the container images for every service, tagging as `latest`.
2. Pushes those images to Google Container Registry.

Note that this workflow does not update the image tags used in `release/kubernetes-manifests.yaml` - these release manifests are tied to a stable `v0.x.x` release.

### Cleanup - [cleanup.yaml](cleanup.yaml)

This workflow runs when a PR closes, regardless of whether it was merged into main. This workflow deletes the PR-specific GKE namespace in the test cluster.
