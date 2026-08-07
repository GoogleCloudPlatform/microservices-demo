# Customize the Base URL for Online Boutique

This component allows you to change the base URL for the Online Boutique application. By default, the application uses the root path ("/") as its base URL. This customization sets the base URL to "/online-boutique" and updates the health check paths accordingly.

## What it does

1. Sets the `BASE_URL` environment variable to "/online-boutique" for the frontend deployment.
2. Updates the liveness probe path to "/online-boutique/_healthz".
3. Updates the readiness probe path to "/online-boutique/_healthz".

## How to use

To apply this customization, you can use Kustomize to include this component in your deployment.

From the `kustomize/` folder at the root level of this repository, execute this command:

```bash
kustomize edit add component components/custom-base-url
```

This will update the `kustomize/kustomization.yaml` file, which could look similar to:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/custom-base-url
```

## Render and Deploy

You can locally render these manifests by running:

```bash
kubectl kustomize .
```

To deploy the customized application, run:

```bash
kubectl apply -k .
```

## Customizing the Base URL

If you want to use a different base URL, you can modify the `value` fields in the kustomization.yaml file. Make sure to update all three occurrences:

1. The `BASE_URL` environment variable
2. The liveness probe path
3. The readiness probe path

For example, to change the base URL to "/shop", you would modify the values as follows:

```yaml
value: /shop
value: /shop/_healthz
value: /shop/_healthz
```

Note: After changing the base URL, make sure to update any internal links or references within your application to use the new base URL.
