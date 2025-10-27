# Adding a new microservice

This document outlines the steps required to add a new microservice to the Online Boutique application.

## 1. Create a new directory

Create a new directory for your microservice within the `src/` directory. The directory name should be the name of your microservice.

## 2. Add source code

Place your microservice's source code inside the newly created directory. The structure of this directory should follow the conventions of the existing microservices. For example, a Python-based service would include at minimum the following files:

- `README.md`: The service's description and documentation.
- `main.py`: The application's entry point.
- `requirements.in`: A list of Python dependencies.
- `Dockerfile`: To containerize the application.

Take a look at existing microservices for inspiration.

## 3. Create a Dockerfile

Create a `Dockerfile` in your microservice's directory. This file will define the steps to build a container image for your service.

Refer to this example and tweak based on your new service's needs: https://github.com/GoogleCloudPlatform/microservices-demo/blob/main/src/frontend/Dockerfile

## 4. Create Kubernetes manifests

Create a new directory under `kustomize/components/` in the root of the repository for your microservice. Inside this directory, add the necessary Kubernetes YAML files for your new microservice. This typically includes:

- A **Deployment** to manage your service's pods.
- A **Service** to expose your microservice to other services within the cluster.

Ensure you follow the existing naming conventions and that the container image specified in the Deployment matches the one built by your `cloudbuild.yaml` and `skaffold.yaml` files.

Refer to this example and tweak based on your new service's needs: https://github.com/GoogleCloudPlatform/microservices-demo/tree/main/kustomize/components/shopping-assistant

## 5. Update the root `kustomization.yaml` file

Add your newly created component to the root kustomization file so it gets picked up by the deployment cycle.

The file is available here: https://github.com/GoogleCloudPlatform/microservices-demo/blob/main/kustomize/kustomization.yaml

## 6. Update the root `skaffold.yaml`

Add your newly created service to the root skaffold file so the images build correctly.

The file is available here: https://github.com/GoogleCloudPlatform/microservices-demo/blob/main/skaffold.yaml

## 7. Update the Helm chart

Add your newly created service to the Helm chart templates and default values.

The chart is available here: https://github.com/GoogleCloudPlatform/microservices-demo/tree/main/helm-chart

## 8. Update the documentation

Finally, update the project's documentation to reflect the addition of your new microservice. This may include:

- Adding a section to the main `README.md` if the service introduces significant new functionality.
- Updating the architecture diagrams in the `docs/img` directory.
- Adding a new document in the `docs` directory if the service requires detailed explanation.
