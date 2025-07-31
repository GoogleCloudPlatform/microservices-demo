# Manage a single shared session for the Online Boutique apps

By default, when you deploy this sample app, the Online Boutique's `frontend` generates a `shop_session-id` cookie per browser session.
But you may want to share one unique `shop_session-id` cookie across all browser sessions.
This is useful for multi-cluster environments.

## Deploy Online Boutique to generate a single shared session

To automate the deployment of Online Boutique to manage a single shared session you can leverage the following variation with [Kustomize](../..).

From the `kustomize/` folder at the root level of this repository, execute this command:

```bash
kustomize edit add component components/single-shared-session
```

This will update the `kustomize/kustomization.yaml` file which could be similar to:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/single-shared-session
```

You can locally render these manifests by running `kubectl kustomize .` as well as deploying them by running `kubectl apply -k .`.
