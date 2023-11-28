# Duet AI demo

This Kustomize component allows you to run the Duet AI version of Online Boutique (or Cymbal Shops).

## Deploy this Kustomize component

Replace `REPLACE_THIS_WITH_YOUR_PACKAGING_SERVICE_URL` inside this component's `kustomization.yaml` file.

From the `kustomize/` folder at the root level of this repository, run this command:

```bash
kustomize edit add component components/cymbal-branding
kustomize edit add component components/duet-ai-demo
kustomize edit add component components/without-loadgenerator
```

This will update the `kustomize/kustomization.yaml` file which could look similar to:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/cymbal-branding
- components/duet-ai-demo
- components/without-loadgenerator
```

To render the manifests (without deploying them), run:
```bash
kubectl kustomize .
```

To deploy the manifests, run:
```bash
kubectl apply -k .
```
