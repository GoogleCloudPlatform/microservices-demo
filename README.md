# Microservices demo

This project contains a 10-tier microservices application. The application is a
web-based e-commerce app called “Hipster Shop” where users can browse items,
add them to the cart, and purchase them.

Google has used this application to demonstrate Kubernetes, GKE, Istio,
Stackdriver, gRPC and similar cloud-native technologies.

### Running locally

1. Install tools to run a Kubernetes cluster locally:

   - kubectl (can be installed via `gcloud components install kubectl`)
   - Docker for Desktop (Mac/Windows): It provides Kubernetes support as [noted
     here](https://docs.docker.com/docker-for-mac/kubernetes/).
   - [skaffold](https://github.com/GoogleContainerTools/skaffold/#installation)

1. Launch “Docker for Desktop”. Go to Preferences and choose “Enable Kubernetes”.

1. Run `kubectl get nodes` to verify you're connected to “Kubernetes on Docker”.

1. Run `skaffold run` (first time will be slow). This will build and deploy the
   application. If you need to rebuild the images automatically as you refactor
   the code, run `skaffold dev` command.

1. Run `kubectl get pods` to verify the Pods are ready and running. The
   application frontend should be available at http://localhost:80 on your
   machine.

### Setup on GKE

1. Install tools specified in the previous section (Docker, kubectl, skaffold)

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
   images, pushes them to GCR, and deploys the application to Kubernetes.

1.  Find the IP address of your application:

        kubectl get service frontend-external

    then visit the application on your browser to confirm
    installation.

### Istio Deployment

1. Create a GKE cluster.

2. Install Istio **without mutual TLS** option. (Istio mTLS is not yet supported
   on this demo.)

3. Install the automatic sidecar injection (annotate the `default` namespace
   with the label):

       kubectl label namespace default istio-injection=enabled

4. Deploy the application with.

5. Apply the manifests in [`./istio-manifests`](./istio-manifests) directory.

       kubectl apply -f ./istio-manifests

6. Run `kubectl get pods` to see pods are in a healthy and ready state.

---

This is not an official Google project.
