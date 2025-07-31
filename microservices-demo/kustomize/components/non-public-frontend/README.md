# Remove the public exposure of Online Boutique's frontend

By default, when you deploy Online Boutique, a `Service` (named `frontend-external`) of type `LoadBalancer` is deployed with a publicly accessible IP address.
But you may not want to expose this sample app publicly.

## Deploy Online Boutique without the default public endpoint

To automate the deployment of Online Boutique without the default public endpoint you can leverage the following variation with [Kustomize](../..).

From the `kustomize/` folder at the root level of this repository, execute this command:

```bash
kustomize edit add component components/non-public-frontend
```

This will update the `kustomize/kustomization.yaml` file which could be similar to:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/non-public-frontend
```

You can locally render these manifests by running `kubectl kustomize .` as well as deploying them by running `kubectl apply -k .`.
