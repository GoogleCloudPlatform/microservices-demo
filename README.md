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
   to all `imageName:` fields.

1. Edit the Deployment manifests at `kubernetes-manifests` directory and update
   the `image` fields to match the changes you made in the previous step.

1. Run `skaffold run`. This builds the container
   images, pushes them to GFR, and deploys the application to Kubernetes.

1.  Find the IP address of your application:

        kubectl get service frontend-external

    then visit the application on your browser to confirm
    installation.
