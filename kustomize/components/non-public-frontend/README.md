# Do not expose publicly the Online Boutique frontend Service

By default, when you deploy this sample app, the Online Boutique's `frontend-external` is deployed as a public (`LoadBalancer`) `Service.
But you may want to not expose this sample app publicly.

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