# Integrate Online Boutique with native gRPC probes

The current container images of the Online Boutique apps contains the [grpc-health-probe](https://github.com/grpc-ecosystem/grpc-health-probe) binary in order to have their `liveness` and `readiness` probes working on Kubernetes. But, since [Kubernetes 1.24, gRPC container probes feature is in beta](https://kubernetes.io/blog/2022/05/13/grpc-probes-now-in-beta/), and this binary could be removed from the container images and the associated `Deployment` manifests can directly use the new gRPC probes (`liveness` and `readiness`).

## Deploy Online Boutique integrated with native gRPC probes

To automate the deployment of Online Boutique integrated with native gRPC probes you can leverage the following variation with [Kustomize](../..).

From the `kustomize/` folder at the root level of this repository, execute this command:
```bash
SUFFIX=-native-grpc-probes
sed -i "s/CONTAINER_IMAGES_TAG_SUFFIX/$SUFFIX/g" components/container-images-tag-suffix/kustomization.yaml
kustomize edit add component components/container-images-tag-suffix
kustomize edit add component components/native-grpc-health-check
```
_Note: we are applying the `-native-grpc-probes` tag suffix to all the container images, it's a prebuilt image without the [grpc-health-probe](https://github.com/grpc-ecosystem/grpc-health-probe) binary since the version 0.4.0 of Online Boutique._

This will update the `kustomize/kustomization.yaml` file which could be similar to:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/container-images-tag-suffix
- components/native-grpc-health-check
```

You can (optionally) locally render these manifests by running `kubectl kustomize . | sed "s/$SUFFIX$SUFFIX/$SUFFIX/g"`.
You can deploy them by running `kubectl kustomize . | sed "s/$SUFFIX$SUFFIX/$SUFFIX/g" | kubectl apply -f`.

_Note: for this variation, `kubectl apply -k .` alone won't work because there is a [known issue currently in Kustomize](https://github.com/kubernetes-sigs/kustomize/issues/4814) where the `tagSuffix` is duplicated. The `sed "s/$SUFFIX$SUFFIX/$SUFFIX/g"` commands above are a temporary workaround._

## Resources

- [Kubernetes 1.24: gRPC container probes in beta](https://kubernetes.io/blog/2022/05/13/grpc-probes-now-in-beta/)
- [Define a gRPC liveness probe](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/#define-a-grpc-liveness-probe)
