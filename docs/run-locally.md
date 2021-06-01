# Run the application locally

The following guide explains how you can run this **Online Boutique** application in a local Kubernetes cluster. We use the [kind](https://kind.sigs.k8s.io/) opensource tool to emulate Kubernetes nodes in the local machine. **kind** emulates the nodes using docker containers.

## Prerequisites
- [Docker for Desktop](https://www.docker.com/products/docker-desktop).
- kubectl (can be installed via `gcloud components install kubectl`)
- [skaffold]( https://skaffold.dev/docs/install/), a tool that builds and deploys Docker images in bulk.
- A Google Cloud Project with Google Container Registry enabled.
- Enable GCP APIs for Cloud Monitoring, Tracing, Debugger, Profiler:
```
gcloud services enable monitoring.googleapis.com \
    cloudtrace.googleapis.com \
    clouddebugger.googleapis.com \
    cloudprofiler.googleapis.com
```
- [Minikube](https://minikube.sigs.k8s.io/docs/start/) (optional - see Local Cluster)
- [Kind](https://kind.sigs.k8s.io/) (optional - see Local Cluster)



1. **Set up Workload Identity** on your GKE cluster [using the instructions here](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity#enable_on_new_cluster). These instructions create the Kubernetes Service Account (KSA) and Google Service Account (GSA) that the OnlineBoutique pods will use to authenticate to GCP. Take note of what Kubernetes `namespace` you use during setup.

2. **Add IAM Roles** to your GSA. These roles allow workload identity-enabled OnlineBoutique pods to send traces and metrics to GCP.

```bash
PROJECT_ID=<your-gcp-project-id>
GSA_NAME=<your-gsa>

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member "serviceAccount:${GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role roles/cloudtrace.agent

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member "serviceAccount:${GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role roles/monitoring.metricWriter

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member "serviceAccount:${GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role roles/cloudprofiler.agent

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
  --member "serviceAccount:${GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role roles/clouddebugger.agent
```

3. **Generate OnlineBoutique manifests** using your KSA as the Pod service account. In `kubernetes-manifests/`, replace `serviceAccountName: default` with the name of your KSA. (**Note** - sample below is Bash.)

```bash

KSA_NAME=<your-ksa>
sed "s/serviceAccountName: default/serviceAccountName: ${KSA_NAME}/g" release/kubernetes-manifests.yaml > release/wi-kubernetes-manifests.yaml
done
```

4. **Deploy OnlineBoutique** to your GKE cluster using the install instructions above, except make sure that instead of the default namespace, you're deploying the manifests into your KSA namespace:

```bash
NAMESPACE=<your-ksa-namespace>
kubectl apply -n ${NAMESPACE} -f release/wi-kubernetes-manifests.yaml
```
