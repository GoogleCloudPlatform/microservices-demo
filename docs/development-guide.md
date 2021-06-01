# Development Guide

This doc explains how to build and run the OnlineBoutique source code locally
using the `skaffold` command-line tool.

## Prerequisites

- [Docker for Desktop](https://www.docker.com/products/docker-desktop).
- kubectl (can be installed via `gcloud components install kubectl`)
- [skaffold](https://skaffold.dev/docs/install/), a tool that builds and deploys
Docker images in bulk.
- [kustomize](https://kubectl.docs.kubernetes.io/installation/kustomize/), an
open source tool that enables maintaining multiple flavors of yaml definiton
for different environments.
- A Google Cloud Project with Google Container Registry enabled.
- Enable GCP APIs for Cloud Monitoring, Tracing, Debugger, Profiler:
```
gcloud services enable monitoring.googleapis.com \
    cloudtrace.googleapis.com \
    clouddebugger.googleapis.com \
    cloudprofiler.googleapis.com
```

One of the following for _Local cluster_ setup:
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) _(optional - see Local Cluster)_
- [Kind](https://kind.sigs.k8s.io/) _(optional - see Local Cluster)_
---

## Option 1: Google Kubernetes Engine (GKE)

> 🎯 **Recommended** Use Google Cloud Platform if you want to try it on
> a realistic cluster. <br>
> 🎯 **Note**: If your cluster has Workload Identity enabled,
> [see these instructions](/docs/workload-identity.md)

#### 1.  Create a Google Kubernetes Engine cluster and make sure `kubectl` is pointing to the cluster.
```sh
gcloud services enable container.googleapis.com
```

```sh
gcloud container clusters create demo --enable-autoupgrade \
    --enable-autoscaling --min-nodes=3 --max-nodes=10 --num-nodes=5 --zone=us-central1-a
```

```
kubectl get nodes
```

#### 2.  Enable Google Container Registry (GCR) on your GCP project and configure the `docker` CLI to authenticate to GCR:####

```sh
gcloud services enable containerregistry.googleapis.com
```

```sh
gcloud auth configure-docker -q
```

#### 3.  In the root of this repository, run `skaffold run --default-repo=gcr.io/[PROJECT_ID]`, where [PROJECT_ID] is your GCP project ID.

This command:

- builds the container images
- pushes them to GCR
- applies the `./kubernetes-manifests` deploying the application to Kubernetes.

> 🎯 **Troubleshooting:** If you get `"No space left on device"` error on Google
Cloud Shell, you can build the images on Google Cloud Build: [Enable the
Cloud Build
API](https://console.cloud.google.com/flows/enableapi?apiid=cloudbuild.googleapis.com),
then run `skaffold run -p gcb --default-repo=gcr.io/[PROJECT_ID]` instead.

#### 4.  Find the IP address of your application, then visit the application on your browser to confirm installation.
```sh
kubectl get service frontend-external
```
---

## Option 2 - Local Cluster

#### 1. A local Kubernetes cluster can be launched with one of the following tools:

- **Minikube** (tested with Ubuntu Linux).
  - Please, ensure that the local Kubernetes cluster has at least:
    - 4 CPUs
    - 4.0 GiB memory
    - 32 GB disk space

    ```shell
    minikube start --cpus=4 --memory 4096 --disk-size 32g
    ```

- **Docker for Desktop** (tested with Mac/Windows).
  - Go to Preferences:
    - Choose “Enable Kubernetes”,
    - Set CPUs to at least 3, and Memory to at least 6.0 GiB
    - On the "Disk" tab, set at least 32 GB disk space

- **Kind** cluster:
  - Use the basic cluster configuration provided at `local/kind-cluster.yaml`
    ```shell
    kind create cluster --config ./local/kind-cluster.yaml
    kind get clusters
    kubectl config use-context kind-hipster
    ```

#### 2. Run `kubectl get nodes` to verify you're connected to the respective control plane.

#### 3. Create a _GCP IAM Service Account_ in your Google Cloud Project
- Create a new service account
- Make sure the service account has the following roles _([see this image](img/service-account.png))_
  ```sh
  Cloud Trace Agent
  Cloud Profiler Agent
  Cloud Debugger Agent
  Monitoring Metric Writer
  ```
- Download the **service account key file** to your local computer

#### 4. Update the `gcp-service-account.yaml` secret with the downloaded key file data
- Replace the `PATH_TO_DOWNLOADED_SERVICE_ACCOUNT_KEY_FILE` placeholder with the
to the downloaded file and execute the following commands:
  ```sh
  # to be run from the root diectory of this repository
  ENCODED=$(base64 <PATH_TO_DOWNLOADED_SERVICE_ACCOUNT_KEY_FILE>)
  sed -i -e "s/KEY_FILE_CONTENT/"$ENCODED"/" local/gcp-service-account.yaml
  ```
#### 5. Run `skaffold run -p local`
> 🎯 First time will be slow; it can take ~20 minutes. <br>
> 🎯 If you see an error at the end of skaffold run (something similar to
`9/12 deployment(s) failed`), give it some time. This can happen due to some
resources depend on others being created first

- This will build and deploy the application. If you need to rebuild the images
   automatically as you refactor the code, run `skaffold dev` command.

#### 6. Run `kubectl get pods` to verify the Pods are ready and running.

#### 7. Access the web frontend through your browser
- **Minikube** requires you to run a command to access the frontend service:
  ```shell
  minikube service frontend-external
  ```

- **Docker For Desktop** should automatically provide the frontend at http://localhost:80

- **Kind** cluster should expose the `frontend` via http://localhost:8080
> 🎯 **Note:** The above is possible because, the `frontend` is exposed via a
_NodePort_ service on port **30001**. This port is then associated to the host
port **8080** via the kind cluster configuration `kind-cluster.yaml`.
---

## Cleanup

If you've deployed the application with `skaffold run -p local` command,
you can run `skaffold delete -p local` to clean up the deployed resources.
