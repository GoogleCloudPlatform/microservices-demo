# Deploying Online Boutique variants with Kustomize

This page contains instructions on deploying variants of the [Online Boutique](https://github.com/GoogleCloudPlatform/microservices-demo) sample application using [Kustomize](https://kustomize.io/). Each variant is designed as a [**Kustomize Component**](https://github.com/kubernetes-sigs/kustomize/blob/master/examples/components.md), so multiple variants can be composed together in the deployment.

## What is Kustomize?

Kustomize is a Kubernetes configuration management tool that allows users to customize their manifest configurations without duplication. Its commands are built into `kubectl` as `apply -k`. More information on Kustomize can be found on the [official Kustomize website](https://kustomize.io/).

## Deployment variations supported by Kustomize

| **Variation Name**                                                                                                         | **Component**                                                                     | **Description**                                                                                                                                                                                                                                                                                |
|----------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Cymbal Shops Branding](https://github.com/GoogleCloudPlatform/microservices-demo/blob/main/docs/cymbal-shops.md)          | [cymbal-branding](/components/cymbal-branding/kustomization.yaml)                 | Changes all Online Boutique-related branding to Google Cloud's fictitious company — Cymbal Shops. The code adds/enables an environment variable `CYMBAL_BRANDING` in the `frontend` service.                                                                                                   |
| [Google Cloud Operations](https://github.com/GoogleCloudPlatform/microservices-demo/blob/main/docs/gcp-instrumentation.md) | [google-cloud-operations](/components/google-cloud-operations/kustomization.yaml) | Enables Monitoring (Stats), Tracing, Profiler, and Debugger for various services within Online Boutique. The code removes the existing environment variables (`DISABLE_STATS`, `DISABLE_TRACING`, `DISABLE_PROFILER`, `DISABLE_DEBUGGER`) from appropriate YAML config files.                  |
| [Memorystore](https://github.com/GoogleCloudPlatform/microservices-demo/blob/main/docs/memorystore.md)                     | [memorystore](/components/memorystore/kustomization.yaml)                         | The default Online Boutique deployment uses the default in-cluster `redis` database for storing the contents of its shopping cart. The Memorystore deployment variation overrides the default database with its own Memorystore (Redis) database. These changes directly affect `cartservice`. |

## Deployment Instructions

### Prerequisites

1. Have a Kubernetes cluster, such as a [GKE (Google Kubernetes Engine)](https://cloud.google.com/kubernetes-engine) cluster or a [minikube](https://minikube.sigs.k8s.io/docs/) cluster.
1. Set your `kubectl` context to the Kubernetes cluster.

Alternatively, if you would like to quickly provision a GKE cluster, you can use the [Online Boutique's Terraform setup at /terraform](https://github.com/GoogleCloudPlatform/microservices-demo/tree/main/terraform).

### [OPTIONAL] Deploying infrastructure for the Memorystore variation

1. While in the `microservices-demo` directory, enter the `terraform/` directory.

    ```
    cd terraform
    ```

1. Open the `terraform.tfvars` file. Replace `<project_id_here>` with the [GCP Project ID](https://cloud.google.com/resource-manager/docs/creating-managing-projects?hl=en#identifying_projects) for the `gcp_project_id` variable. Change the value of `memorystore = false` to `memorystore = true`.

1. Initialize Terraform.

    ```
    terraform init
    ```

1. See what resources will be created.

    ```
    terraform plan
    ```

1. Create the resources and deploy the updated infrastructure.

    ```
    terraform apply
    ```
    
    1. If there is a confirmation prompt, type `yes` and hit Enter/Return.
    
    Note: Following completion, there may be an error saying that the cluster already exists-- this is okay.

1. While in the `terraform/` directory, return back to the `microservices-demo/` directory.

    ```
    cd ..
    ```

### Run the deployment options

1. While in the `microservices-demo` directory, navigate to the `kustomize/` directory.

    ```
    cd kustomize
    ```

1. Edit the base level `kustomization.yaml` to enable the components for the desired variations.

    ```
    nano kustomization.yaml
    ```

    The file should contain a similar snippet of code with only the component variants that you intend to deploy left uncommented.
    
    ```
    components:
      - components/cymbal-branding
      - components/google-cloud-operations
      # - components/memorystore
     ```

    Note: The example above will enable both the Cymbal Shops Branding and Google Cloud Operations components in the deployment.

    Note: To close `nano`, press `Ctrl`/`control` + `x`. To save changes, press `y`, then press `Enter`/`return`.

1. Verify the changes that will be made to the existing deployment config.

    ```
    kubectl kustomize .
    ```

1. Apply the Kustomize deployment changes to the existing deployment.

    ```
    kubectl apply -k .
    ```

    Note: It may take 2-3 minutes before the changes are reflected on the deployment.

1. Wait for all Pods to show `STATUS` of `Running`.

    ```
    kubectl get pods
    ```

    The output should be similar to the following:

    ```
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

1. Access the web frontend in a browser using the frontend's `EXTERNAL_IP`.

    ```
    kubectl get service frontend-external | awk '{print $4}'
    ```

    Note: you may see `<pending>` while GCP provisions the load balancer. If this happens, wait a few minutes and re-run the command.
