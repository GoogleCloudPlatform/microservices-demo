# Add a suffix the container image tag of the Online Boutique apps

You may need to add a suffix to the Online Boutique container image tag to target a specific version, this Kustomize variation will help you setting this up.

## Add a suffix to the container image tag via Kustomize

To automate the deployment of the Online Boutique apps with a suffix added to the container imag tag, you can leverage the following variation with [Kustomize](../..).

From the `kustomize/` folder at the root level of this repository, execute this command:
```
SUFFIX=-test
sed -i "s/CONTAINER_IMAGES_TAG_SUFFIX/$SUFFIX/g" components/container-images-tag-suffix/kustomization.yaml
kustomize edit add components/container-images-tag-suffix
```
_Note: this Kustomize component will add a suffix to the container image tag of the `image:` field in all `Deployments`._

This will update the `kustomize/kustomization.yaml` file which could be similar to:
```
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/container-images-tag-suffix
```

You can locally render these manifests by running `kubectl kustomize . | sed "s/$SUFFIX$SUFFIX/$SUFFIX/g"` as well as deploying them by running `kubectl kustomize . | sed "s/$SUFFIX$SUFFIX/$SUFFIX/g" | kubectl apply -f`.

_Note: for this variation, `kubectl apply -k .` won't work because there is a [known issue currently in Kustomize](https://github.com/kubernetes-sigs/kustomize/issues/4814) where the `tagSuffix` is duplicated. The command lines above are a temporary workaround._

**Important notes:** if combining with the other variations, here are some considerations:
- should be placed before `components/container-images-registry`
- should be placed after `components/container-images-tag`

So for example here is the order respected:
```
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/container-images-tag
- components/container-images-tag-suffix
- components/container-images-registry
```