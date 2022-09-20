# Memorystore (redis) + OnlineBoutique

This guide contains instructions for overriding the default in-cluster `redis` database for `cartservice` with Memorystore (redis).

Important notes:
- You can connect to a Memorystore (redis) instance from GKE clusters that are in the same region and use the same network as your instance.
- You cannot connect to a Memorystore (redis) instance from a GKE cluster without VPC-native/IP aliasing enabled.

![Architecture diagram with Memorystore](./img/memorystore.png)

## Memorystore Deployment

## Automated Deployment

Automated deployment for the Memorystore (Redis) variation is supported with [Terraform](https://www.terraform.io/) for infrastructure management and [Kustomize](https://kustomize.io/) for configuration management. Deployment instructions can be found at [`/kustomize/README.md`](https://github.com/GoogleCloudPlatform/microservices-demo/blob/main/kustomize/README.md).

## Manual Deployment

Note: This section is not a complete substitution for the entire Memorystore deployment process. Instead, this section takes you through the necessary infrastructure changes before **directing you back to the automated deployment process**.

1. Create a GKE cluster with VPC-native/IP aliasing enabled.
    ```sh
    PROJECT_ID="<your-project-id>"
    REGION="<your-GCP-region>"
    ZONE="<your-GCP-zone>"

    gcloud container clusters create onlineboutique \
        --project=${PROJECT_ID} \
        --zone=${ZONE} \
        --machine-type=e2-standard-2 \
        --enable-ip-alias
    ```

   Replace the following:

   * `<your-project-id>`: your GCP [project ID](https://cloud.google.com/resource-manager/docs/creating-managing-projects#identifying_projects).
   * `<your-GCP-region>`: the [Compute Engine region](https://cloud.google.com/compute/docs/regions-zones#available).
   * `<your-GCP-zone>`: the [Compute Engine zone](https://cloud.google.com/compute/docs/regions-zones#available).


1. Enable the Memorystore (Redis) service in your project.

    ```sh
    gcloud services enable redis.googleapis.com --project=${PROJECT_ID}
    ```

1. Create the Memorystore (Redis) instance. 

    ```sh
    gcloud redis instances create redis-cart --size=1 --region=${REGION} --zone=${ZONE} --redis-version=redis_6_x --project=${PROJECT_ID}
    ```

    After a few minutes, you will see the `STATUS` as `READY` when your Memorystore instance will be successfully provisioned:

    ```sh
    gcloud redis instances list --region ${REGION}
    ```

1. From the `microservices-demo/` directory, navigate to the `kustomize/` directory.
  
    ```sh
    cd kustomize
    ```

1. Update current Kustomize manifest to target this Memorystore (Redis) instance.
  
    ```sh
    REDIS_IP=$(gcloud redis instances describe redis-cart --region=${REGION} --format='get(host)')
    sed -i "s/REDIS_IP/${REDIS_IP}/g" components/memorystore/kustomization.yaml
    ```

At this point, you have properly created the infrastructure needed for the Memorystore deployment. To complete the deployment, perform the steps from the **[Run the deployment options](https://github.com/GoogleCloudPlatform/microservices-demo/blob/main/kustomize/README.md#run-the-deployment-options)** section of `/kustomize/README.md`.

## Resources

- [Connecting to a Redis instance from a Google Kubernetes Engine cluster](https://cloud.google.com/memorystore/docs/redis/connect-redis-instance-gke)
