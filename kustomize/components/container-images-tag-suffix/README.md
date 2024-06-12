# Add a suffix to the image tag of the Online Boutique container images

You may want to add a suffix to the Online Boutique container image tag to target a specific version.
The Kustomize Component inside this folder can help.

## Add a suffix to the container image tag via Kustomize

To automate the deployment of the Online Boutique apps with a suffix added to the container imag tag, you can leverage the following variation with [Kustomize](../..).

From the `kustomize/` folder at the root level of this repository, execute this command:

```bash
SUFFIX=-my-suffix
sed -i "s/CONTAINER_IMAGES_TAG_SUFFIX/$SUFFIX/g" components/container-images-tag-suffix/kustomization.yaml
kustomize edit add component components/container-images-tag-suffix
```

_Note: this Kustomize component will add a suffix to the container image tag of the `image:` field in all `Deployments`._

This will update the `kustomize/kustomization.yaml` file which could be similar to:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/container-images-tag-suffix
```

You can locally render these manifests by running `kubectl kustomize . | sed "s/$SUFFIX$SUFFIX/$SUFFIX/g"` as well as deploying them by running `kubectl kustomize . | sed "s/$SUFFIX$SUFFIX/$SUFFIX/g" | kubectl apply -f`.

_Note: for this variation, `kubectl apply -k .` alone won't work because there is a [known issue currently in Kustomize](https://github.com/kubernetes-sigs/kustomize/issues/4814) where the `tagSuffix` is duplicated. The `sed "s/$SUFFIX$SUFFIX/$SUFFIX/g"` commands above are a temporary workaround._

## Combine with other Kustomize Components

If you're combining this Kustomize Component with other variations, here are some considerations:

- `components/container-images-tag-suffix` should be placed before `components/container-images-registry`
- `components/container-images-tag-suffix` should be placed after `components/container-images-tag`

So for example here is the order respected:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/container-images-tag
- components/container-images-tag-suffix
- components/container-images-registry
```
