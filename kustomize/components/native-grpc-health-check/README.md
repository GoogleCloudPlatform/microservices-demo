# Integrate Online Boutique with native gRPC probes

The current container images of the Online Boutique apps contains the [grpc-health-probe](https://github.com/grpc-ecosystem/grpc-health-probe) binary in order to have their `liveness` and `readiness` probes working on Kubernetes. But, since [Kubernetes 1.24, gRPC container probes feature is in beta](https://kubernetes.io/blog/2022/05/13/grpc-probes-now-in-beta/), and this binary could be removed from the container images and the associated `Deployment` manifests can directly use the new gRPC probes (`liveness` and `readiness`).

## Deploy Online Boutique integrated with native gRPC probes

To automate the deployment of Online Boutique integrated with native gRPC probes you can leverage the following variation with [Kustomize](../..).

From the `kustomize/` folder at the root level of this repository, execute this command:

```bash
ONLINE_BOUTIQUE_VERSION=$(curl -s https://api.github.com/repos/GoogleCloudPlatform/microservices-demo/releases | jq -r '[.[]] | .[0].tag_name')
sed -i "s/ONLINE_BOUTIQUE_VERSION/$ONLINE_BOUTIQUE_VERSION/g" components/native-grpc-health-check/kustomization.yaml
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
- components/native-grpc-health-check
```

You can locally render these manifests by running `kubectl kustomize .` as well as deploying them by running `kubectl apply -k .`.

## Resources

- [gRPC health probes with Kubernetes 1.24+ with Online Boutique](https://medium.com/google-cloud/b5bd26253a4c)
- [Kubernetes 1.24: gRPC container probes in beta](https://kubernetes.io/blog/2022/05/13/grpc-probes-now-in-beta/)
- [Define a gRPC liveness probe](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/#define-a-grpc-liveness-probe)
