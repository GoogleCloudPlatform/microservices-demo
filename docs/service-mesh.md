# Deploying to an Istio-enabled cluster 

This repository provides an [`istio-manifests`](/istio-manifests) directory containing ingress resources (an Istio `Gateway` and `VirtualService`) needed to expose the app frontend running inside a Kubernetes cluster.

You can apply these resources to your cluster in addition to the `kubernetes-manifests`, then use the Istio IngressGateway's external IP to view the app frontend. See the following instructions for Istio steps.   

## Steps
 
1. Create a GKE cluster with at least 4 nodes, machine type `e2-standard-4`. 

```
PROJECT_ID="<your-project-id>"
ZONE="<your-GCP-zone>"

gcloud container clusters create onlineboutique \
    --project=${PROJECT_ID} --zone=${ZONE} \
    --machine-type=e2-standard-4 --num-nodes=4
```

2. [Install Istio](https://istio.io/latest/docs/setup/getting-started/) on your cluster. 

3. Enable Istio sidecar proxy injection in the `default` Kubernetes namespace. 

   ```sh
   kubectl label namespace default istio-injection=enabled
   ```

4. Apply all the manifests in the `/release` directory. This includes the Istio and Kubernetes manifests. 

   ```sh
   kubectl apply -f ./release 
   ```

5. Run `kubectl get pods` to see pods are in a healthy and ready state.

6. Find the IP address of your Istio gateway Ingress or Service, and visit the
   application frontend in a web browser.

   ```sh
   INGRESS_HOST="$(kubectl -n istio-system get service istio-ingressgateway \
      -o jsonpath='{.status.loadBalancer.ingress[0].ip}')"
   echo "$INGRESS_HOST"
   ```

   ```sh
   curl -v "http://$INGRESS_HOST"
   ```


## Additional service mesh demos using OnlineBoutique 

- [Canary deployment](https://github.com/GoogleCloudPlatform/istio-samples/tree/master/istio-canary-gke)
- [Security (mTLS, JWT, Authorization)](https://github.com/GoogleCloudPlatform/istio-samples/tree/master/security-intro)
- [Cloud Operations (Stackdriver)](https://github.com/GoogleCloudPlatform/istio-samples/tree/master/istio-stackdriver)
- [Stackdriver metrics (Open source Istio)](https://github.com/GoogleCloudPlatform/istio-samples/tree/master/stackdriver-metrics)

