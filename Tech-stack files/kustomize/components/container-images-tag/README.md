# Update the container image tag of the Online Boutique apps

By default, the Online Boutique apps are targeting the latest release version (see the list of versions [here](https://github.com/GoogleCloudPlatform/microservices-demo/releases)). You may need to change this image tag to target a specific version, this Kustomize variation will help you setting this up.

## Change the default container image tag via Kustomize

To automate the deployment of the Online Boutique apps with a specific container imag tag, you can leverage the following variation with [Kustomize](../..).

From the `kustomize/` folder at the root level of this repository, execute this command:

```bash
TAG=v1.0.0
sed -i "s/CONTAINER_IMAGES_TAG/$TAG/g" components/container-images-tag/kustomization.yaml
kustomize edit add component components/container-images-tag
```

_Note: this Kustomize component will update the container image tag of the `image:` field in all `Deployments`._

This will update the `kustomize/kustomization.yaml` file which could be similar to:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/container-images-tag
```

You can locally render these manifests by running `kubectl kustomize .` as well as deploying them by running `kubectl apply -k .`.

**Important notes:** if combining with the other variations, here are some considerations:

- should be placed before `components/container-images-registry`

So for example here is the order respected:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/container-images-tag
- components/container-images-registry
```
