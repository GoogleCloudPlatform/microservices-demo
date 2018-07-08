# Microservices demo

This project contains a 10-tier microservices application. The application is a
web-based e-commerce app called “Hipster Shop” where users can browse items,
add them to the cart, and purchase them.

### Setup on GKE

1. Install:

   - [gcloud](https://cloud.google.com/sdk/) + sign in to your account/project.
   - kubectl (can be installed via `gcloud components install kubectl`)
   - Docker (on Mac/Windows, install Docker for Desktop CE)
   - [Skaffold](https://github.com/GoogleContainerTools/skaffold/#installation)

1. Create a Google Kubernetes Engine cluster and make sure `kubectl` is pointing
   to the cluster.

1. Enable Google Container Registry (GCR) on your GCP project:

       gcloud services enable containerregistry.googleapis.com
    
1. Configure docker to authenticate to GCR:

       gcloud auth configure-docker -q

1. Edit `skaffold.yaml`, prepend your GCR registry host (`gcr.io/YOUR_PROJECT/`)
   to all `imageName:` fields (or update the existing project name).

1. Edit the Deployment manifests at `kubernetes-manifests` directory and update
   the `image` fields to match the changes you made in the previous step.

1. Run `skaffold run`. This builds the container
   images, pushes them to GFR, and deploys the application to Kubernetes.

1.  Find the IP address of your application:

        kubectl get service frontend-external

    then visit the application on your browser to confirm
    installation.

### Istio Deployment

1. Create a GKE cluster.

2. Install Istio **without mutual TLS** enablement.

3. Install the automatic sidecar injection (annotate the `default` namespace
   with the label):

       kubectl label namespace default istio-injection=enabled

4. Deploy the application.

5. Apply the manifests in [`./istio-manifests`](./istio-manifests) directory.

       kubectl apply -f ./istio-manifests
