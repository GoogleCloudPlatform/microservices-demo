# Secure Online Boutique with Network Policies

You can use [Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/) enforcement to control the communication between your cluster's Pods and Services.

To use `NetworkPolicies` in Google Kubernetes Engine (GKE), you will need a GKE cluster with network policy enforcement enabled, the recommended approach is to use [GKE Dataplane V2](https://cloud.google.com/kubernetes-engine/docs/how-to/dataplane-v2).

To use `NetworkPolicies` on a local cluster such as [minikube](https://minikube.sigs.k8s.io/docs/start/), you will need to use an alternative CNI that supports `NetworkPolicies` like [Calico](https://projectcalico.docs.tigera.io/getting-started/kubernetes/minikube). To run a minikube cluster with Calico, run `minikube start --cni=calico`. By design, the minikube default CNI [Kindnet](https://github.com/aojea/kindnet) does not support it.  

## Deploy Online Boutique with `NetworkPolicies` via Kustomize

To automate the deployment of Online Boutique integrated with fine granular `NetworkPolicies` (one per `Deployment`), you can leverage the following variation with [Kustomize](../..).

From the `kustomize/` folder at the root level of this repository, execute this command:

```bash
kustomize edit add component components/network-policies
```

This will update the `kustomize/kustomization.yaml` file which could be similar to:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/network-policies
```

You can locally render these manifests by running `kubectl kustomize .` as well as deploying them by running `kubectl apply -k .`.

Once deployed, you can verify that the `NetworkPolicies` are successfully deployed:

```bash
kubectl get networkpolicy
```

The output could be similar to:

```output
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
redis-cart              app=redis-cart              2m58s
shippingservice         app=shippingservice         2m58s
```

_Note: `Egress` is wide open in these `NetworkPolicies` . In our case, we do this is on purpose because there are multiple egress destinations to take into consideration like the Kubernetes DNS, Istio control plane (`istiod`), Cloud Trace API, Cloud Profiler API, etc._

## Related Resources

- [GKE Dataplane V2 announcement](https://cloud.google.com/blog/products/containers-kubernetes/bringing-ebpf-and-cilium-to-google-kubernetes-engine)
- [Kubernetes Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Kubernetes Network Policy Recipes](https://github.com/ahmetb/kubernetes-network-policy-recipes)
- [Network policy logging](https://cloud.google.com/kubernetes-engine/docs/how-to/network-policy-logging)
