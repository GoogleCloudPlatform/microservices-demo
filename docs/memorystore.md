# Memorystore (redis) + OnlineBoutique

This guide contains instructions for overriding the default in-cluster `redis` database for `cartservice` with Memorystore (redis).

Important notes:
- You can connect to a Memorystore (redis) instance from GKE clusters that are in the same region and use the same network as your instance.
- You cannot connect to a Memorystore (redis) instance from a GKE cluster without VPC-native/IP aliasing enabled.

![Architecture diagram with Memorystore](./img/memorystore.png)

## Memorystore Deployment
Online Boutique supports a multi-step automated deployment process for the Memorystore (Redis) variation. This process uses Terraform for infrastructure changes and Kustomize for manifest-configuration changes. Instructions for the entire automated deployment can be found [here](https://github.com/GoogleCloudPlatform/microservices-demo/blob/readme/kustomize/README.md).

Alternatively, to manually set up the required infrastructure yourself, follow the steps outlined in the **Manual Infrastructure Steps** section below.

### Manual Infrastructure Steps
Note: This section is not a complete substitution for the entire Memorystore deployment process. Instead, this section takes you through the necessary infrastructure changes before **directing you back to the automated deployment process**.

1. Create a GKE cluster with VPC-native/IP aliasing enabled.
    ```sh
    PROJECT_ID="<your-project-id>"
    ZONE="<your-GCP-zone>"
    REGION="<your-GCP-region>"

    gcloud container clusters create onlineboutique \
        --project=${PROJECT_ID} \
        --zone=${ZONE} \
        --machine-type=e2-standard-2 \
        --enable-ip-alias
    ```

1. Enable the Memorystore (redis) service on your project.

    ```sh
    gcloud services enable redis.googleapis.com --project=${PROJECT_ID}
    ```

1. Create the Memorystore (redis) instance. 

    ```sh
    gcloud redis instances create redis-cart --size=1 --region=${REGION} --zone=${ZONE} --redis-version=redis_6_x --project=${PROJECT_ID}
    ```

    After a few minutes, you will see the `STATUS` as `READY` when your Memorystore instance will be successfully provisioned:

    ```sh
    gcloud redis instances list --region ${REGION}
    ```

1. From the `microservices-demo/` directory, enter the `kustomize` directory.
  
    ```sh
    cd kustomize
    ```

1. Update current Kustomize manifest to target this Memorystore (redis) instance.
  
    ```sh
    REDIS_IP=$(gcloud redis instances describe redis-cart --region=${REGION} --format='get(host)')
    sed -i "s/REDIS_IP/${REDIS_IP}/g" components/memorystore/kustomization.yaml
    ```

1. While in the `kustomize/` directory, return back to the `microservices-demo/` directory.

    ```sh
    cd ..
    ```
    
At this point, you have properly created the infrastructure needed for the Memorystore deployment. Continue to the **[Deployment Instructions](https://github.com/GoogleCloudPlatform/microservices-demo/blob/readme/kustomize/README.md#deployment-instructions)** section for Online Boutique deployment variants to complete the deployment.

## Resources

- [Connecting to a Redis instance from a Google Kubernetes Engine cluster](https://cloud.google.com/memorystore/docs/redis/connect-redis-instance-gke)
