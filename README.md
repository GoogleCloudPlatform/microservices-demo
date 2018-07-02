# Microservices demo

This project contains a 10-tier microservices application. The application is a
web-based e-commerce app called “Hipster Shop” where users can browse items,
add them to the cart, and purchase them.

### Setup on GKE

0. Make sure you have a Google Kubernetes Engine cluster and enabled Google
   Container Registry (GCR) on your GCP project:

       gcloud services enable containerregistry.googleapis.com

1. Edit `skaffold.yaml`, prepend your GCR registry host (`gcr.io/YOUR_PROJECT/`)
   to all `imageName:` fields.

2. Edit the Deployment manifests at `kubernetes-manifests` directory and update
   the `image` fields to match the changes you made in the previous step.

3. Install [Skaffold] and `skaffold run`. This builds the container
   images, pushes them to GFR, and deploys the application to Kubernetes.

4.  Find the IP address of your application:

        kubectl get service frontend-external

    then visit the application on your browser to confirm
    installation.

[Skaffold]: https://github.com/GoogleContainerTools/skaffold/#installation
