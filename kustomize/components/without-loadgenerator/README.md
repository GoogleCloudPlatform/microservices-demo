# Exclude the loadgenerator

By default, when you deploy Online Boutique, its [loadgenerator](/src/loadgenerator/) will also be deployed.

You can use this Kustomize component to exclude the loadgenerator.

Note: This Kustomize component has not been tested with [other Kustomize Components](/kustomize/components/) that rely on the loadgenerator.

## Use this component

From the `kustomize/` folder at the root level of this repository, execute this command:

```bash
kustomize edit add component components/without-loadgenerator
```

This will update the `kustomize/kustomization.yaml` file which could be similar to:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/without-loadgenerator
```

You can then deploy Online Boutique and this component to your cluster using `kubectl apply -k .`. If you just want to render the YAML manifest (without deploying to your cluster), run `kubectl kustomize .`.

Learn more about Online Boutique's kustomize components at [/kustomize](/kustomize#readme).
