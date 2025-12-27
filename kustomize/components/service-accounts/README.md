# Create Kubernetes Service Accounts for Online Boutique

Creating a `ServiceAccount` per `Deployment` could be helpful if you need to define a fine granular identity for each `Deployment` in your Kubernetes clusters. This could help if for example you want to give specific Google Cloud IAM role binding by leveraging [Workload Identity with GKE](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity#enable). Another scenario could be if you want to define fine granular [`AuthorizationPolicies` with Istio/ASM](https://cloud.google.com/service-mesh/docs/by-example/authz).

## Deploy Online Boutique with `ServiceAccounts` via Kustomize

To automate the deployment of Online Boutique integrated with fine granular `ServiceAccounts` (one per `Deployment`), you can leverage the following variation with [Kustomize](../..).

From the `kustomize/` folder at the root level of this repository, execute this command:

```bash
kustomize edit add component components/service-accounts
```

_Note: this Kustomize component will also update the `serviceAccountName` field in all `Deployments`._

This will update the `kustomize/kustomization.yaml` file which could be similar to:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/service-accounts
```

You can locally render these manifests by running `kubectl kustomize .` as well as deploying them by running `kubectl apply -k .`.

Once deployed, you can verify that the `ServiceAccounts` are successfully deployed:

```bash
kubectl get serviceaccount
```

The output could be similar to:

```output
NAME                    SECRETS     AGE
default                 1           2m58s
adservice               1           2m58s
cartservice             1           2m58s
checkoutservice         1           2m58s
currencyservice         1           2m58s
emailservice            1           2m58s
frontend                1           2m58s
loadgenerator           1           2m58s
paymentservice          1           2m58s
productcatalogservice   1           2m58s
recommendationservice   1           2m58s
shippingservice         1           2m58s
```

_Note: We made the choice that the `redis-cart` `Deployment` doesn't have its own `ServiceAccount` because it doesn't need its own identity to talk to another `Deployment` or externally to the GKE cluster._
