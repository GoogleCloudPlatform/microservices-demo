# Integrate Online Boutique with Memorystore (Redis)

By default the `cartservice` app is serializing the data in an in-cluster Redis database. Using a database outside your GKE cluster could bring more resiliency and more security with a managed service like Google Cloud Memorystore (Redis).

![Architecture diagram with Memorystore](/docs/img/memorystore.png)

## Provision a Memorystore (Redis) instance

Important notes:

- You can connect to a Memorystore (Redis) instance from GKE clusters that are in the same region and use the same network as your instance.
- You cannot connect to a Memorystore (Redis) instance from a GKE cluster without VPC-native/IP aliasing enabled.

To provision a Memorystore (Redis) instance you can follow the following instructions:

```bash
ZONE="<your-GCP-zone>"
REGION="<your-GCP-region>"

gcloud services enable redis.googleapis.com

gcloud redis instances create redis-cart \
    --size=1 \
    --region=${REGION} \
    --zone=${ZONE} \
    --redis-version=redis_6_x
```

_Note: You can also find in this repository the Terraform script to provision the Memorystore (Redis) instance alongside the GKE cluster, more information [here](/terraform)._

## Deploy Online Boutique connected to a Memorystore (Redis) instance

To automate the deployment of Online Boutique integrated with Memorystore (Redis) you can leverage the following variation with [Kustomize](../..).

From the `kustomize/` folder at the root level of this repository, execute this command:

```bash
kustomize edit add component components/memorystore
```

_Note: this Kustomize component will also remove the `redis-cart` `Deployment` and `Service` not used anymore._

This will update the `kustomize/kustomization.yaml` file which could be similar to:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/memorystore
```

Update current Kustomize manifest to target this Memorystore (Redis) instance.

```bash
REDIS_IP=$(gcloud redis instances describe redis-cart --region=${REGION} --format='get(host)')
REDIS_PORT=$(gcloud redis instances describe redis-cart --region=${REGION} --format='get(port)')
sed -i "s/REDIS_CONNECTION_STRING/${REDIS_IP}:${REDIS_PORT}/g" components/memorystore/kustomization.yaml
```

You can locally render these manifests by running `kubectl kustomize .` as well as deploying them by running `kubectl apply -k .`.

## Resources

- [Connecting to a Redis instance from a Google Kubernetes Engine cluster](https://cloud.google.com/memorystore/docs/redis/connect-redis-instance-gke)
- [Seamlessly encrypt traffic from any apps in your Mesh to Memorystore (Redis)](https://medium.com/google-cloud/64b71969318d)
