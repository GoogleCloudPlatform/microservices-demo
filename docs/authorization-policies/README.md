# AuthorizationPolicy + OnlineBoutique

This guide contains instructions for configuring `AuthorizationPolicy` resources for the OnlineBoutique apps.

## Steps
 
1. You need to have a GKE cluster created with Istio or Anthos Service Mesh (ASM) installed on it.

You also need to have an Ingress Gateway deployed in your GKE cluster. `AuthorizationPolicy` needs to have mTLS `STRICT` enabled in both the Ingress Gateway's namespace and the OnlineBoutique's namespace. With that in place, when the end-user hits the Ingress Gateway's public IP address, the Ingress Gateway will transform the request in plain text in mTLS and will forward the request to the OnlineBoutique `frontend` app.

2. Apply all the manifests.

Get the base manifests:
```
cp ../../release/kubernetes-manifests.yaml .
cp ../../release/istio-manifests.yaml .
```

Update the manifests locally with the corresponding Ingress Gateway setup:
```
INGRESS_GATEWAY_NAME=asm-ingressgateway
INGRESS_GATEWAY_NAMESPACE=asm-ingress
sed -i "s/INGRESS_GATEWAY_NAME/${INGRESS_GATEWAY_NAME}/g;s/INGRESS_GATEWAY_NAMESPACE/${INGRESS_GATEWAY_NAMESPACE}/g" ./for-ingress-gateway/kustomization.yaml
kustomize edit add component for-ingress-gateway
```

Update the manifests locally with your OnlineBoutique namespace:
```
export ONLINEBOUTIQUE_NAMESPACE=default
sed -i "s/ONLINEBOUTIQUE_NAMESPACE/${ONLINEBOUTIQUE_NAMESPACE}/g" ./for-namespace/kustomization.yaml
sed -i "s/ONLINEBOUTIQUE_NAMESPACE/${ONLINEBOUTIQUE_NAMESPACE}/g" ./for-ingress-gateway/kustomization.yaml
kustomize edit add component for-namespace
kustomize edit set namespace ${ONLINEBOUTIQUE_NAMESPACE}
```

Deploy the manifests:
```sh
kubectl apply -k .
```

3. Verify the resources deployed.

If you run:
```
kubectl get serviceaccount,pod,authorizationpolicy
```
You should see:
```
FIXME
```

4. Verify you could still access OnlineBoutique solution.

```
kubectl get service ${INGRESS_GATEWAY_NAME} -n ${INGRESS_GATEWAY_NAMESPACE} | awk '{print $4}'
```

## Resources

- [`Authorization Policy`](https://cloud.google.com/service-mesh/docs/security/authorization-policy-overview)