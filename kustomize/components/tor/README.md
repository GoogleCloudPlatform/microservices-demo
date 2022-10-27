# Change the Online Boutique to run with Tor 

## Deploy Online Boutique with Tor 

To automate the deployment of Online Boutique with the Cymbal Shops branding you can leverage the following variation with [Kustomize](../..).

From the `kustomize/` folder at the root level of this repository, execute this command:
```bash
kustomize edit add component components/tor
```

This will update the `kustomize/kustomization.yaml` file which could be similar to:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/tor
```

You can locally render these manifests by running `kubectl kustomize .` as well as deploying them by running `kubectl apply -k .`.
