# Update the container registry of the Online Boutique apps

By default, the Online Boutique apps are coming from the public container registry `gcr.io/google-samples/microservices-demo`. One best practice is to have these container images in your own private container registry, this Kustomize variation will help you setting this up.

## Change the default container registry via Kustomize

To automate the deployment of Online Boutique integrated with your own container registry, you can leverage the following variation with [Kustomize](../..).

From the `kustomize/` folder at the root level of this repository, execute this command:
```
REGISTRY=my-registry
sed -i "s/CONTAINER_IMAGES_REGISTRY/$REGISTRY/g" components/container-images-registry/kustomization.yaml
kustomize edit add components/container-images-registry
```
_Note: this Kustomize component will update the container registry in the `image:` field in all `Deployments`._

This will update the `kustomize/kustomization.yaml` file which could be similar to:
```
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/container-images-registry
```

You can locally render these manifests by running `kubectl kustomize .` as well as deploying them by running `kubectl apply -k .`.
