# NetworkPolicy

This guide contains instructions for deploying Online Boutique with [`NetworkPolicy`](https://kubernetes.io/docs/concepts/services-networking/network-policies/) resources.

To use `NetworkPolicy` objects in Google Kubernetes Engine (GKE), you will need a GKE cluster with network policy enforcement enabled.
To learn more, see the official [GKE documentation on enabling network policy enforcement](https://cloud.google.com/kubernetes-engine/docs/how-to/network-policy#enabling_network_policy_enforcement).
You do not need to enable network policy enforcement in clusters that use [GKE Dataplane V2](https://cloud.google.com/kubernetes-engine/docs/concepts/dataplane-v2).

## Deploy Online Boutique with `NetworkPolicy` objects

The steps below will deploy Online Boutique with its `NetworkPolicy` resources on a Kubernetes cluster that supports `NetworkPolicy` resources.

1. Manually edit the `/kustomize/kustomization.yaml` to include the `network-policy` Kustomize Component inside this directory.
```
components:
  ...
  - components/network-policy
  ...
```

Alternatively, you can use `sed` to uncomment the existing `# - component/network-policy` line:
```
sed -i '' 's/# - components\/network-policy/- components\/network-policy/' kustomize/kustomization.yaml
```

2. Deploy Online Boutique with the `NetworkPolicy` objects.

The following command will deploy Online Boutique along with its `NetworkPolicy` resources:
```sh
kubectl apply -k ./kustomize/
```

3. Verify that the `NetworkPolicy` resources have been deployed.

If you run:
```bash
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

_Note: `Egress` is wide open in these `NetworkPolicy` resources. In our case, we do this is on purpose because there are multiple egress destinations to take into consideration like the Kubernetes DNS, Istio control plane (`istiod`), Cloud Trace API, Cloud Profiler API, Cloud Debugger API, etc._

4. Verify you could still access the frontend's `EXTERNAL_IP` with no issues.

```
kubectl get service frontend-external | awk '{print $4}'
```

## Related Resources

- [GKE Dataplane V2 announcement](https://cloud.google.com/blog/products/containers-kubernetes/bringing-ebpf-and-cilium-to-google-kubernetes-engine)
- [Kubernetes Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)
- [Kubernetes Network Policy Recipes](https://github.com/ahmetb/kubernetes-network-policy-recipes)
- [Network policy logging](https://cloud.google.com/kubernetes-engine/docs/how-to/network-policy-logging)
