# Integrate Online Boutique with native gRPC Healthcheck probes

FIXME

Kubernetes 1.24+

## Deploy Online Boutique connected to a Memorystore (Redis) instance

To automate the deployment of Online Boutique integrated with Memorystore (Redis) you can leverage the following variation with [Kustomize](../..).

From the `kustomize/` folder at the root level of this repository, execute this command:
```
kustomize edit add components/container-images-tag-suffix
```
_Note: this Kustomize component will also remove the `redis-cart` `Deployment` and `Service` not used anymore._

This will update the `kustomize/kustomization.yaml` file which could be similar to:
```
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/container-images-tag-suffix
```

Update current Kustomize manifest to target the new container images tag (same tag as default tag but with the suffix `-native-grpc`).
```sh
sed -i "s/$(CONTAINER_IMAGES_TAG_SUFFIX)/-native-grpc/g" components/container-images-tag-suffix/kustomization.yaml
```

You can locally render these manifests by running `kubectl kustomize .` as well as deploying them by running `kubectl apply -k .`.

## Resources

- FIXME
