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
- A Google Cloud Project with the GCP APIs for Cloud Monitoring, Tracing, Debugger, Profiler and Container Registry enabled:
```
gcloud services enable monitoring.googleapis.com \
    cloudtrace.googleapis.com \
    clouddebugger.googleapis.com \
    cloudprofiler.googleapis.com \
    containerregistry.googleapis.com
```

One of the following for _Local cluster_ setup:
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) _(optional - [see Local Cluster](#option-2---local-cluster))_
- [Kind](https://kind.sigs.k8s.io/) _(optional - [see Local Cluster](#option-2---local-cluster))_
---

## Option 1: Google Kubernetes Engine (GKE)

> 🎯 &nbsp;&nbsp;**Recommended** Use Google Cloud Platform if you want to try it on
> a realistic cluster. <br>
> 🎯 &nbsp;&nbsp;**Note**: If your cluster has Workload Identity enabled,
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

- Builds the container images
- Pushes them to GCR
- Applies the `./kubernetes-manifests` deploying the application to Kubernetes.

> 🎯 &nbsp;&nbsp;**Troubleshooting:** If you get `"No space left on device"` error on Google
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
  - Use the basic cluster configuration provided at `extras/kind-cluster.yaml`
    ```shell
    kind create cluster --config ./extras/kind-cluster.yaml
    kind get clusters
    kubectl config use-context kind-hipster
    ```

#### 2. Run `kubectl get nodes` to verify you're connected to the respective control plane.

#### 3. Create a _GCP IAM Service Account_ in your Google Cloud Project
- Set the environment variable `PROJECT_ID` with the ID of the GCP project
you are using.
- For `SERVICE_ACCOUNT_NAME` you can use any meaningful string.
```sh
export PROJECT_ID=<YOUR_PROJECT_ID>
export SERVICE_ACCOUNT_NAME=<A_NAME_FOR_THE_SERVICE_ACCOUNT>
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME
  ```
> 🎯 &nbsp;&nbsp;These variables will be used in the following steps; thus steps
3 to 6 must be run on the same shell window

#### 4. Add the required _IAM Roles_ to the created Service Account
```sh
# Role bindings for the following roles are added:
#   - Cloud Trace Agent
#   - Cloud Profiler Agent
#   - Cloud Debugger Agent
#   - Monitoring Metric Writer

gcloud projects add-iam-policy-binding hip-v2 \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/cloudtrace.agent"

gcloud projects add-iam-policy-binding hip-v2 \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/cloudprofiler.agent"

gcloud projects add-iam-policy-binding hip-v2 \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/clouddebugger.agent"

gcloud projects add-iam-policy-binding hip-v2 \
    --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/monitoring.metricWriter"
```

#### 5. Download the **service account key file** to your local computer
```sh\
gcloud iam service-accounts keys create sa-key.json --iam-account=${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
```

#### 6. Update the `gcp-service-account.yaml` secret with the downloaded key file data
  ```sh
  # to be run from the root diectory of this repository
  ENCODED=$(base64 sa-key.json)
  sed -i '' -e "s/KEY_FILE_CONTENT/"$ENCODED"/" local/gcp-service-account.yaml
  ```
#### 7. Run skaffold
- The following will build and deploy the application. If you need to rebuild
the images automatically as you refactor the code, run `skaffold dev` command.
```sh
skaffold run -p local
```
> 🎯 &nbsp;&nbsp;When run the first time, it can take ~20 minutes. This
is because, none of the image layers have been cached. DUring the first run
Docker will build these from scratch.<br><br>
> 🎯 &nbsp;&nbsp;If you see an error at the end of skaffold run (something similar to
`9/12 deployment(s) failed`), give it some time. This can happen due to some
resources depend on others being created first.

#### 8. Verify that the Pods are ready anbd running
```sh
# use the -w (watch) flag to keep monitoring as the pods gets spawned
kubectl get pods
```

#### 9. Access the web frontend through your browser
- **Minikube** requires you to run a command to access the frontend service:
  ```shell
  minikube service frontend-external
  ```

- **Docker For Desktop** should automatically provide the frontend at http://localhost:80

- **Kind** cluster should expose the `frontend` via http://localhost:8080
> 🎯 &nbsp;&nbsp;**Note:** The above is possible because, in this setup the
 `frontend` is exposed via a _NodePort_ service on port **30001**. This port is
  then associated to the host port **8080** via the kind cluster configuration
   `kind-cluster.yaml`.
---

## Cleanup

If you've deployed the application with `skaffold run -p local` command,
you can run `skaffold delete -p local` to clean up the deployed resources.
