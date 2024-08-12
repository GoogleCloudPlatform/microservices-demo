# Use Online Boutique with Kustomize

This page contains instructions on deploying variations of the [Online Boutique](https://github.com/GoogleCloudPlatform/microservices-demo) sample application using [Kustomize](https://kustomize.io/). Each variations is designed as a [**Kustomize component**](https://github.com/kubernetes-sigs/kustomize/blob/master/examples/components.md), so multiple variations can be composed together in the deployment.

## What is Kustomize?

Kustomize is a Kubernetes configuration management tool that allows users to customize their manifest configurations without duplication. Its commands are built into `kubectl` as `apply -k`. More information on Kustomize can be found on the [official Kustomize website](https://kustomize.io/).

## Prerequisites

Optionally, [install the `kustomize` binary](https://kubectl.docs.kubernetes.io/installation/) to avoid manually editing a `kustomization.yaml` file. Online Boutique's instructions will often use `kustomize edit` (like `kustomize edit add component components/some-component`), but you can skip these commands and instead add components manually to the [`/kustomize/kustomization.yaml` file](/kustomize/kustomization.yaml).

You need to have a Kubernetes cluster where you will deploy the Online Boutique's Kubernetes manifests. To set up a GKE (Google Kubernetes Engine) cluster, you can follow the instruction in the [root `/README.md`](/).

## Deploy Online Boutique with Kustomize

1. From the root folder of this repository, navigate to the `kustomize/` directory.

    ```bash
    cd kustomize/
    ```

1. See what the default Kustomize configuration defined by `kustomize/kustomization.yaml` will generate (without actually deploying them yet).

    ```bash
    kubectl kustomize .
    ```

1. Apply the default Kustomize configuration (`kustomize/kustomization.yaml`).

    ```bash
    kubectl apply -k .
    ```

1. Wait for all Pods to show `STATUS` of `Running`.

    ```bash
    kubectl get pods
    ```

    The output should be similar to the following:

    ```terminal
    NAME                                     READY   STATUS    RESTARTS   AGE
    adservice-76bdd69666-ckc5j               1/1     Running   0          2m58s
    cartservice-66d497c6b7-dp5jr             1/1     Running   0          2m59s
    checkoutservice-666c784bd6-4jd22         1/1     Running   0          3m1s
    currencyservice-5d5d496984-4jmd7         1/1     Running   0          2m59s
    emailservice-667457d9d6-75jcq            1/1     Running   0          3m2s
    frontend-6b8d69b9fb-wjqdg                1/1     Running   0          3m1s
    loadgenerator-665b5cd444-gwqdq           1/1     Running   0          3m
    paymentservice-68596d6dd6-bf6bv          1/1     Running   0          3m
    productcatalogservice-557d474574-888kr   1/1     Running   0          3m
    recommendationservice-69c56b74d4-7z8r5   1/1     Running   0          3m1s
    shippingservice-6ccc89f8fd-v686r         1/1     Running   0          2m58s
    ```

    _Note: It may take 2-3 minutes before the changes are reflected on the deployment._

1. Access the web frontend in a browser using the frontend's `EXTERNAL_IP`.

    ```bash
    kubectl get service frontend-external | awk '{print $4}'
    ```

    Note: you may see `<pending>` while GCP provisions the load balancer. If this happens, wait a few minutes and re-run the command.

## Deploy Online Boutique variations with Kustomize

Here is the list of the variations available as Kustomize components that you could leverage:

- [**Change to the Cymbal Shops Branding**](components/cymbal-branding)
  - Changes all Online Boutique-related branding to Google Cloud's fictitious company — Cymbal Shops. The code adds/enables an environment variable `CYMBAL_BRANDING` in the `frontend` service.
- [**Integrate with Google Cloud Operations**](components/google-cloud-operations)
  - Enables Monitoring (Stats), Tracing, and Profiler for various services within Online Boutique. The code adds the appropriare environment variables (`ENABLE_STATS`, `ENABLE_TRACING`, `DISABLE_PROFILER`) for each YAML config file.
- [**Integrate with Memorystore (Redis)**](components/memorystore)
  - The default Online Boutique deployment uses the in-cluster `redis` database for storing the contents of its shopping cart. The Memorystore deployment variation overrides the default database with its own Memorystore (Redis) database. These changes directly affect `cartservice`.
- [**Integrate with Spanner**](components/spanner)
  - The default Online Boutique deployment uses the in-cluster `redis` database for storing the contents of its shopping cart. The Spanner deployment variation overrides the default database with its own Spanner database. These changes directly affect `cartservice`.
- [**Integrate with AlloyDB**](components/alloydb)
  - The default Online Boutique deployment uses the in-cluster `redis` database for storing the contents of its shopping cart. The AlloyDB deployment variation overrides the default database with its own AlloyDB database.
These changes directly affect `cartservice`.
- [**Secure with Network Policies**](components/network-policies)
  - Deploy fine granular `NetworkPolicies` for Online Boutique.
- [**Update the registry name of the container images**](components/container-images-registry)
- [**Update the image tag of the container images**](components/container-images-tag)
- [**Add an image tag suffix to the container images**](components/container-images-tag-suffix)
- [**Do not expose the `frontend` publicly**](components/non-public-frontend)
- [**Set the `frontend` to manage only one single shared session**](components/single-shared-session)
- [**Configure `Istio` service mesh resources**](components/service-mesh-istio)

### Select variations

To customize Online Boutique with its variations, you need to update the default `kustomize/kustomization.yaml` file. You could do that manually, use `sed`, or use the `kustomize edit` command like illustrated below.

#### Use `kustomize edit` to select variations

Here is an example with the [**Cymbal Shops Branding**](components/cymbal-branding) variation, from the `kustomize/` folder, run the command below:

```bash
kustomize edit add component components/cymbal-branding
```

You could now combine it with other variations, like for example with the [**Google Cloud Operations**](components/google-cloud-operations) variation:

```bash
kustomize edit add component components/google-cloud-operations
```

### Deploy selected variations

Like explained earlier, you can locally render these manifests by running `kubectl kustomize .` as well as deploying them by running `kubectl apply -k .`.

So for example, the associated `kustomization.yaml` could look like:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/cymbal-branding
- components/google-cloud-operations
```

### Use remote Kustomize targets

Kustomize allows you to reference public remote resources so the `kustomization.yaml` could look like:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- github.com/GoogleCloudPlatform/microservices-demo/kustomize/base
components:
- github.com/GoogleCloudPlatform/microservices-demo/kustomize/components/cymbal-branding
- github.com/GoogleCloudPlatform/microservices-demo/kustomize/components/google-cloud-operations
```

Learn more about [Kustomize remote targets](https://github.com/kubernetes-sigs/kustomize/blob/master/examples/remoteBuild.md).
