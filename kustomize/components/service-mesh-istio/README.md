# Service mesh with Istio

You can use [Istio](https://istio.io) to enable [service mesh features](https://cloud.google.com/service-mesh/docs/overview) such as traffic management, observability, and security. Istio can be provisioned using Cloud Service Mesh (CSM), the Open Source Software (OSS) istioctl tool, or via other Istio providers. You can then label individual namespaces for sidecar injection and configure an Istio gateway to replace the frontend-external load balancer.

# Setup

The following CLI tools needs to be installed and in the PATH:

- `gcloud`
- `kubectl`
- `kustomize`
- `istioctl` (optional)

1. Set-up some default environment variables.

   ```sh
   PROJECT_ID="<your-project-id>"
   REGION="<your-google-cloud-region"
   CLUSTER_NAME="online-boutique"
   gcloud config set project $PROJECT_ID
   ```

# Provision a GKE Cluster

1. Create an Autopilot GKE cluster.

   ```sh
   gcloud container clusters create-auto $CLUSTER_NAME \
     --location=$REGION
   ```

   To make the best use of our service mesh, we need to have [GKE Workload Identity](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity), and the [Kubernetes Gateway API resource definitions](https://cloud.google.com/kubernetes-engine/docs/how-to/deploying-gateways) enabled. Autopilot takes care of this for us.

1. Change our kubectl context for the newly created cluster.

   ```sh
   gcloud container clusters get-credentials $CLUSTER_NAME \
     --region $REGION
   ```

# Provision and Configure Istio Service Mesh

## (Option A) Provision managed Istio using Cloud Service Mesh

Cloud Service Mesh (CSM) provides a service mesh experience that includes a fully managed control plane and data plane. The recommended way to [install CSM](https://cloud.google.com/service-mesh/docs/onboarding/provision-control-plane) uses [fleet management](https://cloud.google.com/kubernetes-engine/fleet-management/docs/fleet-creation).

1. Enable the Cloud Service Mesh and GKE Enterprise APIs.

   ```sh
   gcloud services enable mesh.googleapis.com anthos.googleapis.com
   ```

1. Enable service mesh support fleet-wide.

   ```sh
   gcloud container fleet mesh enable
   ```

1. Register the GKE cluster to the fleet.

   ```sh
   gcloud container clusters update $CLUSTER_NAME \
     --location $REGION \
     --fleet-project $PROJECT_ID

1. Enable automatic management of the service mesh feature in the cluster.

   ```sh
   gcloud container fleet mesh update \
     --management automatic \
     --memberships $CLUSTER_NAME \
     --project $PROJECT_ID \
     --location $REGION
   ```

1. Add the Istio injection labels to the default namespace.

   ```sh
   kubectl label namespace default \
     istio.io/rev- istio-injection=enabled --overwrite
   ```

1. Verify that the service mesh is fully provisioned. It will take several minutes for both the control plane and data plane to be ready.

   ```sh
   gcloud container fleet mesh describe
   ```

   The output should be similar to:
   ```
   createTime: '2024-09-18T15:52:36.133664725Z'
   fleetDefaultMemberConfig:
     mesh:
       management: MANAGEMENT_AUTOMATIC
   membershipSpecs:
     projects/12345/locations/us-central1/memberships/online-boutique:
       mesh:
         management: MANAGEMENT_AUTOMATIC
       origin:
         type: USER
   membershipStates:
     projects/12345/locations/us-central1/memberships/online-boutique:
       servicemesh:
         conditions:
         - code: VPCSC_GA_SUPPORTED
           details: This control plane supports VPC-SC GA.
           documentationLink: http://cloud.google.com/service-mesh/docs/managed/vpc-sc
           severity: INFO
         controlPlaneManagement:
           details:
           - code: REVISION_READY
             details: 'Ready: asm-managed'
           implementation: TRAFFIC_DIRECTOR
           state: ACTIVE
         dataPlaneManagement:
           details:
           - code: OK
             details: Service is running.
           state: ACTIVE
       state:
         code: OK
         description: 'Revision ready for use: asm-managed.'
         updateTime: '2024-09-18T16:30:37.632583401Z'
   name: projects/my-project/locations/global/features/servicemesh
   resourceState:
     state: ACTIVE
   spec: {}
   updateTime: '2024-09-18T16:15:05.957266437Z'
   ```

1. (Optional) If you require Certificate Authority Service, you can configure it by [following these instructions](https://cloud.google.com/service-mesh/docs/security/certificate-authority-service).

## (Option B) Provision Istio using istioctl

1. Alternatively you can install the open source version of Istio by following the [getting started guide](https://istio.io/latest/docs/setup/getting-started/).

   ```sh
   # Install istio 1.17 or above
   istioctl install --set profile=minimal -y

   # Enable sidecar injection for Kubernetes namespace(s) where microservices-demo is deployed
   kubectl label namespace default istio-injection=enabled

   # Make sure the istiod injection webhook port 15017 is accessible via GKE master nodes
   # Otherwise your replicaset-controller may be blocked when trying to create new pods with: 
   #   Error creating: Internal error occurred: failed calling 
   #     webhook "namespace.sidecar-injector.istio.io" ... context deadline exceeded
   gcloud compute firewall-rules list --filter="name~gke-[0-9a-z-]*-master"
   NAME                          NETWORK  DIRECTION  PRIORITY  ALLOW              DENY  DISABLED
   gke-online-boutique-c94d71e8-master  gke-vpc  INGRESS    1000      tcp:10250,tcp:443        False

   # Update firewall rule (or create a new one) to allow webhook port 15017
   gcloud compute firewall-rules update gke-online-boutique-c94d71e8-master \
    --allow tcp:10250,tcp:443,tcp:15017
   ```

# Deploy Online Boutique with the Istio component

Once the service mesh and namespace injection are configured, you can then deploy the Istio manifests using Kustomize. You should also include the [service-accounts component](../service-accounts) if you plan on using AuthorizationPolicies.

1. Enable the service-mesh-istio component.

   ```sh
   cd kustomize/
   kustomize edit add component components/service-mesh-istio
   ```

   This will update the `kustomize/kustomization.yaml` file which could be similar to:
   ```yaml
   apiVersion: kustomize.config.k8s.io/v1beta1
   kind: Kustomization
   resources:
   - base
   components:
   - components/service-mesh-istio
   ```

   _Note: `service-mesh-istio` component includes the same delete patch as the `non-public-frontend` component. Trying to use both those components in your kustomization.yaml file will result in an error._

1. Deploy the manifests.

   ```sh
   kubectl apply -k
   ```

   The output should be similar to:
   ```
   serviceaccount/adservice created
   serviceaccount/cartservice created
   serviceaccount/checkoutservice created
   serviceaccount/currencyservice created
   serviceaccount/emailservice created
   serviceaccount/frontend created
   serviceaccount/loadgenerator created
   serviceaccount/paymentservice created
   serviceaccount/productcatalogservice created
   serviceaccount/recommendationservice created
   serviceaccount/shippingservice created
   service/adservice created
   service/cartservice created
   service/checkoutservice created
   service/currencyservice created
   service/emailservice created
   service/frontend created
   service/paymentservice created
   service/productcatalogservice created
   service/recommendationservice created
   service/redis-cart created
   service/shippingservice created
   deployment.apps/adservice created
   deployment.apps/cartservice created
   deployment.apps/checkoutservice created
   deployment.apps/currencyservice created
   deployment.apps/emailservice created
   deployment.apps/frontend created
   deployment.apps/loadgenerator created
   deployment.apps/paymentservice created
   deployment.apps/productcatalogservice created
   deployment.apps/recommendationservice created
   deployment.apps/redis-cart created
   deployment.apps/shippingservice created
   gateway.gateway.networking.k8s.io/istio-gateway created
   httproute.gateway.networking.k8s.io/frontend-route created
   serviceentry.networking.istio.io/allow-egress-google-metadata created
   serviceentry.networking.istio.io/allow-egress-googleapis created
   virtualservice.networking.istio.io/frontend created
   ```

# Verify that the deployment succeeded

1. Check that the pods and the gateway are in a healthy and ready state.

   ```sh
   kubectl get pods,gateways,services
   ```

   The output should be similar to:
   ```
   NAME                                         READY   STATUS    RESTARTS   AGE
   pod/adservice-6cbd9794f9-8c4gv               2/2     Running   0          47s
   pod/cartservice-667bbd5f6-84j8v              2/2     Running   0          47s
   pod/checkoutservice-547557f445-bw46n         2/2     Running   0          47s
   pod/currencyservice-6bd8885d9c-2cszv         2/2     Running   0          47s
   pod/emailservice-64997dcf97-8fpsd            2/2     Running   0          47s
   pod/frontend-c54778dcf-wbgmr                 2/2     Running   0          46s
   pod/istio-gateway-istio-8577b948c6-cxl8j     1/1     Running   0          45s
   pod/loadgenerator-ccfd4d598-jh6xj            2/2     Running   0          46s
   pod/paymentservice-79b77cd7c-6hth7           2/2     Running   0          46s
   pod/productcatalogservice-5f75795545-nk5wv   2/2     Running   0          46s
   pod/recommendationservice-56dd4c7df5-gnwwr   2/2     Running   0          46s
   pod/redis-cart-799c85c644-pxsvt              2/2     Running   0          46s
   pod/shippingservice-64f8df74f5-7wllf         2/2     Running   0          45s

   NAME                                              CLASS   ADDRESS          READY   AGE
   gateway.gateway.networking.k8s.io/istio-gateway   istio   35.247.123.146   True    45s

   NAME                            TYPE           CLUSTER-IP      EXTERNAL-IP      PORT(S)                        AGE
   service/adservice               ClusterIP      10.68.231.142   <none>           9555/TCP                       49s
   service/cartservice             ClusterIP      10.68.184.25    <none>           7070/TCP                       49s
   service/checkoutservice         ClusterIP      10.68.177.213   <none>           5050/TCP                       49s
   service/currencyservice         ClusterIP      10.68.249.87    <none>           7000/TCP                       49s
   service/emailservice            ClusterIP      10.68.205.123   <none>           5000/TCP                       49s
   service/frontend                ClusterIP      10.68.94.203    <none>           80/TCP                         48s
   service/istio-gateway-istio     LoadBalancer   10.68.147.158   35.247.123.146   15021:30376/TCP,80:30332/TCP   45s
   service/kubernetes              ClusterIP      10.68.0.1       <none>           443/TCP                        65m
   service/paymentservice          ClusterIP      10.68.114.19    <none>           50051/TCP                      48s
   service/productcatalogservice   ClusterIP      10.68.240.153   <none>           3550/TCP                       48s
   service/recommendationservice   ClusterIP      10.68.117.97    <none>           8080/TCP                       48s
   service/redis-cart              ClusterIP      10.68.189.126   <none>           6379/TCP                       48s
   service/shippingservice         ClusterIP      10.68.221.62    <none>           50051/TCP                      48s
   ```

1. Find the external IP address of your Istio gateway.

   ```sh
   INGRESS_HOST="$(kubectl get gateway istio-gateway \
       -o jsonpath='{.status.addresses[*].value}')"
   ```

1. Navigate to the frontend in a web browser.

   ```
   http://$INGRESS_HOST
   ```

# Additional service mesh demos using Online Boutique 

- [Canary deployment](https://github.com/GoogleCloudPlatform/istio-samples/tree/master/istio-canary-gke)
- [Security (mTLS, JWT, Authorization)](https://github.com/GoogleCloudPlatform/istio-samples/tree/master/security-intro)
- [Cloud Operations (Stackdriver)](https://github.com/GoogleCloudPlatform/istio-samples/tree/master/istio-stackdriver)
- [Stackdriver metrics (Open source Istio)](https://github.com/GoogleCloudPlatform/istio-samples/tree/master/stackdriver-metrics)

# Related resources

- [Deploying classic istio-ingressgateway in ASM](https://cloud.google.com/service-mesh/docs/gateways#deploy_gateways)
- [Uninstall Istio via istioctl](https://istio.io/latest/docs/setup/install/istioctl/#uninstall-istio)
- [Uninstall Cloud Service Mesh](https://cloud.google.com/service-mesh/docs/uninstall)
