# GitHub Actions Workflows

This page describes the CI/CD workflows for the Online Boutique app, which run in [Github Actions](https://github.com/GoogleCloudPlatform/microservices-demo/actions). 

## Infrastructure 

The CI/CD pipelines for Online Boutique run in Github Actions, using a pool of two [self-hosted runners]((https://help.github.com/en/actions/automating-your-workflow-with-github-actions/about-self-hosted-runners)). These runners are GCE instances (virtual machines) that, for every open Pull Request in the repo, run the code test pipeline, deploy test pipeline, and (on master) deploy the latest version of the app to [onlineboutique.dev](https://onlineboutique.dev)

We also host a test GKE cluster, which is where the deploy tests (functional, UI tests) run. Every PR has its own namespace in the cluster. 

## Workflows 

**Note**: In order for the current CI/CD setup to work on your pull request, you must branch directly off the repo (no forks). This is because the Github secrets necessary for these tests aren't copied over when you fork.   

### Code Tests - [ci.yaml](ci.yaml)

These tests run on every commit for every open PR, as well as any commit to master / any release branch. This workflow: 

1. Runs Java (`mvn`) and Python (`pylint`) style checks on all the source code.
2. Runs all Java service unit tests, with test coverage reporting (`jacoco`)
3. Runs all Python service unit tests, with test coverage reporting (`pytest --cov`)


### Deploy Tests- [ci.yaml](ci.yaml)

These tests run on every commit for every open PR, as well as any commit to master / any release branch. This workflow: 

1. Creates a dedicated GKE namespace for that PR, if it doesn't already exist, in the PR GKE cluster. 
2. Uses `skaffold run` to build and push the images specific to that PR commit. Then skaffold deploys those images, via `dev-kubernetes-manifests`, to the PR namespace in the test cluster. 
3. Tests to make sure all the pods start up and become ready.
4. Gets the LoadBalancer IP for the frontend service.
5. Runs the [end-to-end UI tests](ui-tests/) using Cypress, against that frontend IP. These tests ensure that the expected Online Boutique functionality (account creation, depositing money) continues to work with the changes introduced by this commit. 

### Push and Deploy Latest - [push-deploy](push-deploy.yml)

This is the Continuous Deployment workflow, and it runs on every commit to the master branch. This workflow:

1. Builds the contaner images for every service, tagging as `latest`. 
2. Pushes those images to Google Container Registry.   
3. Deploys the latest images to the GKE cluster hosting [bank-of-anthos.xyz](https://bank-of-anthos.xyz).   

Note that this workflow does not update the image tags used in the public-facing `kubernetes-manifests/` - these release manifests are tied to a stable `v0.x.x` release, and are set in the manual releasing process. 

### Cleanup - [cleanup.yaml](cleanup.yaml)

This workflow runs when a PR closes, regardless of whether it was merged into master. This workflow deletes the PR-specific GKE namespace in the test cluster. 

## Appendix - Creating a new Actions runner 

Should one of the two self-hosted Github Actions runners (GCE instances) fail, or you want to add more runner capacity, this is how to provision a new runner. Note that you need IAM access to the central Online Boutique GCP project in order to do this.  

1. Create a GCE instance.
    - VM should be at least n1-standard-4 with 50GB persistent disk
    - VM should use custom service account with only permissions to push images to GCR
2. SSH into new VM through Google Cloud Console
3. Follow the instructions to add a new runner on the [Actions Settings page](https://github.com/GoogleCloudPlatform/bank-of-anthos/settings/actions) to authenticate the new runner
4. Start GitHub Actions as a background service:
```
sudo ~/actions-runner/svc.sh install ; sudo ~/actions-runner/svc.sh start
```
5. Install project-specific dependencies, including docker, skaffold, and kubectl: 

```
wget -O - https://raw.githubusercontent.com/GoogleCloudPlatform/bank-of-anthos/master/.github/workflows/install-dependencies.sh | bash
```

