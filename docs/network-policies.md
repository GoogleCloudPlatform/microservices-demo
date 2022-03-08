# NetworkPolicy + OnlineBoutique

This guide contains instructions for configuring `NetworkPolicy` resources for the OnlineBoutique apps by leveraging the [GKE Dataplane V2](https://cloud.google.com/kubernetes-engine/docs/concepts/dataplane-v2) feature.

## Steps
 
1. You need to have a GKE cluster created with [GKE Dataplane V2 enabled](https://cloud.google.com/kubernetes-engine/docs/how-to/dataplane-v2).

As an example, here is the option you need to use when creating your cluster:
```sh
gcloud container clusters create \
    --enable-dataplane-v2
```

2. Apply all the manifests.

After you applied the Kubernetes manifests of the Online Boutique sample apps, you could apply the `NetworkPolicy` resources:
```sh
kubectl apply -f ./manifests/network-policies/
```

3. Verify the resources deployed.

If you run:
```
kubectl get networkpolicy
```

You should see:
```
NAME                    POD-SELECTOR                AGE
adservice               app=adservice               2m58s
cartservice             app=cartservice             2m58s
checkoutservice         app=checkoutservice         2m58s
currencyservice         app=currencyservice         2m58s
deny-all                <none>                      2m58s
emailservice            app=emailservice            2m58s
frontend                app=frontend                2m58s
loadgenerator           app=loadgenerator           2m58s
paymentservice          app=paymentservice          2m58s
productcatalogservice   app=productcatalogservice   2m58s
recommendationservice   app=recommendationservice   2m58s
shippingservice         app=shippingservice         2m58s
```

_Note: `Egress` is wide-open in these `NetworkPolicy` resources. In our case, we do that on purpose because there is multiple egress destinations to take into consideration like: the Kubernetes's DNS, Istio control plane (`istiod`), Cloud Trace API, Cloud Profiler API, Cloud Debugger API, etc._

4. Verify you could still access the frontend's `EXTERNAL_IP` with no issues.

```
kubectl get service frontend-external | awk '{print $4}'
```

5. Leverage the Network policy logging feature

[Network policy logging](https://cloud.google.com/kubernetes-engine/docs/how-to/network-policy-logging) lets you record when a connection is allowed or denied by a network policy.

To leverage this feature you need to deploy this `NetworkLogging` resource in your cluster:
```sh
cat << EOF | kubectl apply -f -
kind: NetworkLogging
apiVersion: networking.gke.io/v1alpha1
metadata:
  name: default
spec:
  cluster:
    allow:
      log: true
      delegate: false
    deny:
      log: true
      delegate: false
EOF
```

From there, you are able to see the `allow` and `deny` logs generated:
```sh
gcloud logging read --project "PROJECT_NAME" 'resource.type="k8s_node"
    resource.labels.location="CLUSTER_LOCATION"
    resource.labels.cluster_name="CLUSTER_NAME"
    logName="projects/PROJECT_NAME/logs/policy-action"'
```

_Note: you could even get more insights based on these logs if you go throught the ["Anthos > Security > Policy Summary > Kubernetes network policy" page](https://cloud.google.com/service-mesh/docs/observability/explore-dashboard#viewing_security_features) in the GCP console._

## Resources

- [GKE Dataplane V2 announcement](https://cloud.google.com/blog/products/containers-kubernetes/bringing-ebpf-and-cilium-to-google-kubernetes-engine)
- [Kubernetes Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Kubernetes Network Policy Recipes](https://github.com/ahmetb/kubernetes-network-policy-recipes)