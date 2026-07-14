# Development Guide 

This doc explains how to build and run the Online Boutique source code locally using the `skaffold` command-line tool.  

## Prerequisites

- [Docker for Desktop](https://www.docker.com/products/docker-desktop)
- [kubectl](https://kubernetes.io/docs/tasks/tools/) (can be installed via `gcloud components install kubectl` for Option 1 - GKE)
- [skaffold **2.0.2+**](https://skaffold.dev/docs/install/) (latest version recommended), a tool that builds and deploys Docker images in bulk.
  
  **Install skaffold:**
  ```sh
  # Linux
  curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64
  chmod +x skaffold
  sudo mv skaffold /usr/local/bin/
  
  # macOS
  brew install skaffold
  
  # Or download from: https://skaffold.dev/docs/install/
  ```

- Clone the repository.
    ```sh
    git clone https://github.com/GoogleCloudPlatform/microservices-demo
    cd microservices-demo/
    ```
- A Google Cloud project with Google Container Registry enabled. (for Option 1 - GKE)
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) (optional for Option 2 - Local Cluster)
- [Kind](https://kind.sigs.k8s.io/) (optional for Option 2 - Local Cluster)
- [k3d](https://k3d.io/) (optional for Option 2 - Local Cluster)

### Verify Prerequisites

Before starting, verify all required tools are installed:

```sh
docker --version         # Should show Docker 20.10+
kubectl version --client # Should show kubectl 1.19+
skaffold version        # Should show skaffold 2.0.2+
```

If any command fails, install the missing tool using the links above.

## Option 1: Google Kubernetes Engine (GKE)

> 💡 Recommended if you're using Google Cloud and want to try it on
> a realistic cluster. **Note**: If your cluster has Workload Identity enabled, 
> [see these instructions](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity#enable)

1.  Create a Google Kubernetes Engine cluster and make sure `kubectl` is pointing
    to the cluster.

    ```sh
    gcloud services enable container.googleapis.com
    ```

    ```sh
    gcloud container clusters create-auto demo --region=us-central1
    ```

    ```
    kubectl get nodes
    ```

2.  Enable Artifact Registry (AR) on your GCP project and configure the
    `docker` CLI to authenticate to AR:

    ```sh
    gcloud services enable artifactregistry.googleapis.com
    ```

    ```sh
    gcloud artifacts repositories create microservices-demo \
      --repository-format=docker \
      --location=us \
    ```

    ```sh
    gcloud auth configure-docker -q 
    ```

3.  In the root of this repository, run:

    ```
    skaffold run --default-repo=us-docker.pkg.dev/PROJECT_ID/microservices-demo
    ```
    
    Where `PROJECT_ID` is replaced by your Google Cloud project ID.

    This command:

    - Builds the container images.
    - Pushes them to AR.
    - Applies the `./kubernetes-manifests` deploying the application to
      Kubernetes.

    **Troubleshooting:** If you get "No space left on device" error on Google
    Cloud Shell, you can build the images on Google Cloud Build: [Enable the
    Cloud Build
    API](https://console.cloud.google.com/flows/enableapi?apiid=cloudbuild.googleapis.com),
    then run `skaffold run -p gcb --default-repo=us-docker.pkg.dev/[PROJECT_ID]/microservices-demo` instead.

4.  Find the IP address of your application, then visit the application on your
    browser to confirm installation.

        kubectl get service frontend-external

5.  Navigate to `http://EXTERNAL-IP` to access the web frontend.

## Option 2 - Local Cluster 

1. Launch a local Kubernetes cluster with one of the following tools:

    - To launch **Minikube** (tested with Ubuntu Linux). Please, ensure that the
       local Kubernetes cluster has at least:
        - 4 CPUs
        - 4.0 GiB memory
        - 32 GB disk space

      ```shell
      minikube start --cpus=4 --memory 4096 --disk-size 32g
      ```

    - To launch **Docker for Desktop** (tested with Mac/Windows). Go to Preferences:
        - choose “Enable Kubernetes”,
        - set CPUs to at least 3, and Memory to at least 6.0 GiB
        - on the "Disk" tab, set at least 32 GB disk space

    - To launch a **Kind** cluster:

      ```shell
      kind create cluster
      ```

2. Run `kubectl get nodes` to verify you're connected to the respective control plane.

3. Run `skaffold run` (first time will be slow, it can take ~20 minutes).
   This will build and deploy the application. If you need to rebuild the images
   automatically as you refactor the code, run `skaffold dev` command.

   **If you encounter build errors** (see Troubleshooting section below), use pre-built images instead:
   ```shell
   kubectl apply -f ./release/kubernetes-manifests.yaml
   ```

4. Run `kubectl get pods` to verify the Pods are ready and running.

   After a few minutes, you should see output similar to:
   ```
   NAME                                     READY   STATUS    RESTARTS   AGE
   adservice-xxx                            1/1     Running   0          2m
   cartservice-xxx                          1/1     Running   0          2m
   checkoutservice-xxx                      1/1     Running   0          2m
   currencyservice-xxx                      1/1     Running   0          2m
   emailservice-xxx                         1/1     Running   0          2m
   frontend-xxx                             1/1     Running   0          2m
   loadgenerator-xxx                        1/1     Running   0          2m
   paymentservice-xxx                       1/1     Running   0          2m
   productcatalogservice-xxx                1/1     Running   0          2m
   recommendationservice-xxx                1/1     Running   0          2m
   redis-cart-xxx                           1/1     Running   0          2m
   shippingservice-xxx                      1/1     Running   0          2m
   ```

5. Run `kubectl port-forward deployment/frontend 8080:8080` to forward a port to the frontend service.

6. Navigate to `http://localhost:8080` to access the web frontend.

## Adding a new microservice

In general, the set of core microservices for Online Boutique is fairly complete and unlikely to change in the future, but it can be useful to add an additional optional microservice that can be deployed to complement the core services.

See the [Adding a new microservice](adding-new-microservice.md) guide for instructions on how to add a new microservice.

## Cleanup

If you've deployed the application with `skaffold run` command, you can run
`skaffold delete` to clean up the deployed resources.

If you used `kubectl apply`, run:
```shell
kubectl delete -f ./release/kubernetes-manifests.yaml
```

To delete your local cluster:
```shell
# k3d
k3d cluster delete mycluster

# Minikube
minikube delete

# Kind
kind delete cluster
```
