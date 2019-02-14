# Hipster Shop: Cloud-Native Microservices Demo Application

This project contains a 10-tier microservices application. The application is a
web-based e-commerce app called **“Hipster Shop”** where users can browse items,
add them to the cart, and purchase them.

**Google uses this application to demonstrate use of technologies like
Kubernetes/GKE, Istio, Stackdriver, gRPC and OpenCensus**. This application
works on any Kubernetes cluster (such as a local one), as well as Google
Kubernetes Engine. It’s **easy to deploy with little to no configuration**.

If you’re using this demo, please **★Star** this repository to show your interest!

> 👓**Note to Googlers:** Please fill out the form at
[go/microservices-demo](http://go/microservices-demo) if you are using this
application.

## Screenshots

| Home Page | Checkout Screen |
|-----------|-----------------|
| [![Screenshot of store homepage](./docs/img/hipster-shop-frontend-1.png)](./docs/img/hipster-shop-frontend-1.png) | [![Screenshot of checkout screen](./docs/img/hipster-shop-frontend-2.png)](./docs/img/hipster-shop-frontend-2.png) |

## Service Architecture

**Hipster Shop** is composed of many microservices written in different
languages that talk to each other over gRPC.

[![Architecture of
microservices](./docs/img/architecture-diagram.png)](./docs/img/architecture-diagram.png)

Find **Protocol Buffers Descriptions** at the [`./pb` directory](./pb).

| Service | Language | Description |
|---------|----------|-------------|
| [frontend](./src/frontend) | Go | Exposes an HTTP server to serve the website. Does not require signup/login and generates session IDs for all users automatically. |
| [cartservice](./src/cartservice) |  C# | Stores the items in the user's shipping cart in Redis and retrieves it. |
| [productcatalogservice](./src/productcatalogservice) | Go | Provides the list of products from a JSON file and ability to search products and get individual products. |
| [currencyservice](./src/currencyservice) | Node.js | Converts one money amount to another currency.  Uses real values fetched from European Central Bank. It's the highest QPS service. |
| [paymentservice](./src/paymentservice) | Node.js | Charges the given credit card info (mock) with the given amount and returns a transaction ID. |
| [shippingservice](./src/shippingservice) | Go | Gives shipping cost estimates based on the shopping cart. Ships items to the given address (mock) |
| [emailservice](./src/emailservice) | Python | Sends users an order confirmation email (mock). |
| [checkoutservice](./src/checkoutservice) | Go | Retrieves user cart, prepares order and orchestrates the payment, shipping and the email notification. |
| [recommendationservice](./src/recommendationservice) | Python | Recommends other products based on what's given in the cart. |
| [adservice](./src/adservice) | Java | Provides text ads based on given context words. |
| [loadgenerator](./src/loadgenerator) | Python/Locust | Continuously sends requests imitating realistic user shopping flows to the frontend. |


## Features

- **[Kubernetes](https://kubernetes.io)/[GKE](https://cloud.google.com/kubernetes-engine/):**
  The app is designed to run on Kubernetes (both locally on "Docker for
  Desktop", as well as on the cloud with GKE).
- **[gRPC](https://grpc.io):** Microservices use a high volume of gRPC calls to
  communicate to each other.
- **[Istio](https://istio.io):** Application works on Istio service mesh.
- **[OpenCensus](https://opencensus.io/) Tracing:** Most services are
  instrumented using OpenCensus trace interceptors for gRPC/HTTP.
- **[Stackdriver APM](https://cloud.google.com/stackdriver/):** Many services
  are instrumented with **Profiling**, **Tracing** and **Debugging**. In
  addition to these, using Istio enables features like Request/Response
  **Metrics** and **Context Graph** out of the box. When it is running out of
  Google Cloud, this code path remains inactive.
- **[Skaffold](https://github.com/GoogleContainerTools/skaffold):** Application
  is deployed to Kubernetes with a single command using Skaffold.
- **Synthetic Load Generation:** The application demo comes with a background
  job that creates realistic usage patterns on the website using
  [Locust](https://locust.io/) load generator.

## Installation

> **Note:** that the first build can take up to 20-30 minutes. Consequent builds
> will be faster.

### Option 1: Running locally with “Docker for Desktop”

> 💡 Recommended if you're planning to develop the application.

1. Install tools to run a Kubernetes cluster locally:

   - kubectl (can be installed via `gcloud components install kubectl`)
   - Docker for Desktop (Mac/Windows): It provides Kubernetes support as [noted
     here](https://docs.docker.com/docker-for-mac/kubernetes/).
   - [skaffold](https://github.com/GoogleContainerTools/skaffold/#installation)
     (ensure version ≥v0.20)

1. Launch “Docker for Desktop”. Go to Preferences:
   - choose “Enable Kubernetes”,
   - set CPUs to at least 3, and Memory to at least 6.0 GiB

3. Run `kubectl get nodes` to verify you're connected to “Kubernetes on Docker”.

4. Run `skaffold run` (first time will be slow, it can take ~20-30 minutes).
   This will build and deploy the application. If you need to rebuild the images
   automatically as you refactor he code, run `skaffold dev` command.

5. Run `kubectl get pods` to verify the Pods are ready and running. The
   application frontend should be available at http://localhost:80 on your
   machine.

### Option 2: Running on Google Kubernetes Engine (GKE)

> 💡  Recommended for demos and making it available publicly.

1. Install tools specified in the previous section (Docker, kubectl, skaffold)

1. Create a Google Kubernetes Engine cluster and make sure `kubectl` is pointing
   to the cluster.

        gcloud services enable container.googleapis.com

        gcloud container clusters create demo --enable-autoupgrade \
            --enable-autoscaling --min-nodes=3 --max-nodes=10 --num-nodes=5 --zone=us-central1-a

        kubectl get nodes

1. Enable Google Container Registry (GCR) on your GCP project and configure the
   `docker` CLI to authenticate to GCR:

       gcloud services enable containerregistry.googleapis.com

       gcloud auth configure-docker -q

1. In the root of this repository, run `skaffold run --default-repo=gcr.io/[PROJECT_ID]`,
   where [PROJECT_ID] is your GCP project ID.

   This command:
   - builds the container images
   - pushes them to GCR
   - applies the `./kubernetes-manifests` deploying the application to
     Kubernetes.

   **Troubleshooting:** If you get "No space left on device" error on Google
   Cloud Shell, you can build the images on Google Cloud Build: [Enable the
   Cloud Build
   API](https://console.cloud.google.com/flows/enableapi?apiid=cloudbuild.googleapis.com),
   then run `skaffold run -p gcb  --default-repo=gcr.io/[PROJECT_ID]` instead.

1.  Find the IP address of your application, then visit the application on your
    browser to confirm installation.

        kubectl get service frontend-external

    **Troubleshooting:** A Kubernetes bug (will be fixed in 1.12) combined with
    a Skaffold [bug](https://github.com/GoogleContainerTools/skaffold/issues/887)
    causes load balancer to not to work even after getting an IP address. If you
    are seeing this, run `kubectl get service frontend-external -o=yaml | kubectl apply -f-`
    to trigger load balancer reconfiguration.

### Option 3: Using Static Images 

> 💡 Recommended for test-driving the application on an existing cluster. 

**Prerequisite**: a running Kubernetes cluster. 

1. Clone this repository.
1. Deploy the application: `kubectl apply -f ./release/kubernetes-manifests`  
1. Run `kubectl get pods` to see pods are in a healthy and ready state.
1.  Find the IP address of your application, then visit the application on your
    browser to confirm installation.

        kubectl get service frontend-external


### (Optional) Deploying on a Istio-installed GKE cluster

> **Note:** you followed GKE deployment steps above, run `skaffold delete` first
> to delete what's deployed.

1. Create a GKE cluster (described above).

2. Use [Istio on GKE add-on](https://cloud.google.com/istio/docs/istio-on-gke/installing)
   to install Istio to your existing GKE cluster.

       gcloud beta container clusters update demo \
           --zone=us-central1-a \
           --update-addons=Istio=ENABLED \
           --istio-config=auth=MTLS_PERMISSIVE

   > NOTE: If you need to enable `MTLS_STRICT` mode, you will need to update
   > several manifest files:
   >
   > - `kubernetes-manifests/frontend.yaml`: delete "livenessProbe" and
   >   "readinessProbe" fields.
   > - `kubernetes-manifests/loadgenerator.yaml`: delete "initContainers" field.

3. (Optional) Enable Stackdriver Tracing/Logging with Istio Stackdriver Adapter
   by [following this guide](https://cloud.google.com/istio/docs/istio-on-gke/installing#enabling_tracing_and_logging).

4. Install the automatic sidecar injection (annotate the `default` namespace
   with the label):

       kubectl label namespace default istio-injection=enabled

5. Apply the manifests in [`./istio-manifests`](./istio-manifests) directory.

       kubectl apply -f ./istio-manifests

    This is required only once.

6. Deploy the application with `skaffold run --default-repo=gcr.io/[PROJECT_ID]`.

7. Run `kubectl get pods` to see pods are in a healthy and ready state.

8. Find the IP address of your istio gateway Ingress or Service, and visit the
   application.

       INGRESS_HOST="$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"

       echo "$INGRESS_HOST"

       curl -v "http://$INGRESS_HOST"

## Conferences featuring Hipster Shop

- [Google Cloud Next'18 London – Keynote](https://youtu.be/nIq2pkNcfEI?t=3071)
  showing Stackdriver Incident Response Management
- Google Cloud Next'18 SF
  - [Day 1  Keynote](https://youtu.be/vJ9OaAqfxo4?t=2416) showing GKE On-Prem
  - [Day 3 – Keynote](https://youtu.be/JQPOPV_VH5w?t=815) showing Stackdriver
    APM (Tracing, Code Search, Profiler, Google Cloud Build)
  - [Introduction to Service Management with Istio](https://www.youtube.com/watch?v=wCJrdKdD6UM&feature=youtu.be&t=586)

---

This is not an official Google project. 
