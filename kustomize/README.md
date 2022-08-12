# Use Kustomize to deploy Online Boutique with variants
This page walks you through the deployment options for the [Online Boutique](https://github.com/GoogleCloudPlatform/microservices-demo) sample application on a [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine) cluster using Kustomize. Deployment variants are designed as **components**, meaning that multiple variant components can be enabled at once.

## What is Kustomize?
Kustomize is a Kubernetes native configuration management tool that allows users to customize their manifest configurations without having to copy entire files multiple times. Its commands are built into `kubectl` as `apply -k`. This repo uses Kustomize to enable the deployment variants found [here](https://github.com/GoogleCloudPlatform/microservices-demo#other-deployment-options). More information can be found on the official [Kustomize website](https://kustomize.io/).

## Supported Deployment Variations
| **Variation Name**                                                                                                         | **Description**                                                                                                                                                                                                                                                                                |
|----------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| [Cymbal Branding](https://github.com/GoogleCloudPlatform/microservices-demo/blob/main/docs/cymbal-shops.md)                | Changes all Online Boutique-related branding to Google Cloud's fictitious company--Cymbal Shops. The code adds/enables an environment variable `CYMBAL_BRANDING` to the `frontend` deployment.                                                                                                 |
| [Google Cloud Operations](https://github.com/GoogleCloudPlatform/microservices-demo/blob/main/docs/gcp-instrumentation.md) | Enables Monitoring (Stats), Tracing, Profiler, and Debugger for various services within Online Boutique. The code removes the existing environment variables (`DISABLE_STATS`, `DISABLE_TRACING`, `DISABLE_PROFILER`, `DISABLE_DEBUGGER`) from appropriate YAML config files.                  |
| [Memorystore](https://github.com/GoogleCloudPlatform/microservices-demo/blob/main/docs/memorystore.md)                     | The vanilla Online Boutique deployment uses the default in-cluster `redis` database for storing the contents of its shopping cart. The Memorystore deployment variation overrides the default database with its own Memorystore (redis) database. These changes directly affect `cartservice`. |

## Deployment Instructions (General)
1. While in the `microservices-demo` directory, enter the `kustomize/` directory.
    ```
    cd kustomize
    ```

1. Edit the base level `kustomization.yaml` so that it is uses the intended components.
    ```
    vim kustomization.yaml
    ```

    The file should contain a similar snippet of code with only the component variants that you intend to deploy.
    ```
    components:
      - components/cymbal-branding
      - components/google-cloud-operations
      # - components/memorystore
     ```

    Note: The example above will enable both the Cymbal Branding and Google Cloud Operations components in the new deployment.

1. Check to see what changes will be made to the existing deployment config.
    ```
    kustomize build .
    ```

1. Apply the Kustomize deployment changes to the existing deployment.
    ```
    kubectl apply -k .
    ```

    Note: It may take 2-3 minutes before the changes are reflected on the deployment.
