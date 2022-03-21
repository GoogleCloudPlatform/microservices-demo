# AuthorizationPolicy + OnlineBoutique

This guide contains instructions for configuring `AuthorizationPolicy` resources for the OnlineBoutique apps.

## Steps
 
1. You need to have a GKE cluster created with Istio or Anthos Service Mesh (ASM) installed on it.

2. Apply all the manifests.

Update the manifests locally if you need to deploy the solution in a different namespace than `default`:
```
export NAMESPACE=default
sed -i "s/namespace: default/namespace: ${NAMESPACE}/g;s,ns/default,ns/${NAMESPACE},g" ./manifests/authorization-policies/kustomization.yaml
```

Get the base manifests:
```
cp ../../release/kubernetes-manifests.yaml .
```

Deploy the manifests:
```sh
kubectl apply -k .
```
_Note: this command above leverage `Kustomize` in order to deploy both base and overlays manifests. Overlays manifests contain the `ServiceAccount` and `AuthorizationPolicy` resources._

3. Verify the resources deployed.

If you run:
```
kubectl get serviceaccount,pod,authorizationpolicy -n $NAMESPACE
```
You should see:
```
FIXME
```

4. Verify you could still access the frontend's `EXTERNAL_IP` with no issues.

```
kubectl get service frontend-external -n $NAMESPACE | awk '{print $4}'
```

5. _(Optional)_ Update `frontend` manifest if you use an Ingress Gateway

Update the manifests locally if you need to deploy the solution in a different namespace than `default`:
```
sed -i "s/namespace: default/namespace: ${NAMESPACE}/g;s,ns/default,ns/${NAMESPACE},g" ./manifests/authorization-policies-ingress-gateway/kustomization.yaml
```

Update the manifests locally if you have a different name for your Ingress Gateway name rather than `asm-ingressgateway` in the `asm-ingress` namespace:
```
INGRESS_GATEWAY_NAME=asm-ingressgateway
INGRESS_GATEWAY_NAMESPACE=asm-ingress
sed -i "s,ns/asm-ingress/sa/asm-ingressgateway,ns/${INGRESS_GATEWAY_NAMESPACE}/sa/${INGRESS_GATEWAY_NAME},g" ./manifests/authorization-policies-ingress-gateway/kustomization.yaml
```

Deploy the manifests:
```
kubectl apply -k ./overlays-manifests/authorization-policies-ingress-gateway/
```

## Resources

- [`Authorization Policy`](https://cloud.google.com/service-mesh/docs/security/authorization-policy-overview)