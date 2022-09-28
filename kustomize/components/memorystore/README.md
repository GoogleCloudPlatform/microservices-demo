# Integrate Online Boutique with Memorystore (Redis)

By default the `cartservice` app is serializing the data in an in-cluster Redis database. Using a database outside your GKE cluster could bring more resiliency and more security with a managed service like Google Cloud Memorystore (Redis).

![Architecture diagram with Memorystore](/docs/img/memorystore.png)

To use Memorystore (Redis), the `cartservice`'s environment variable `REDIS_ADDR` needs to be updated to point to the Memorystore (Redis) instance.

To provision a Memorystore (Redis) instance you can follow the instructions [here](https://cloud.google.com/memorystore/docs/redis/creating-managing-instances).

You can also find in this repository the Terraform script to provision the Memorystore (Redis) instance alongside the GKE cluster, more information [here](/terraform).

Important notes:
- You can connect to a Memorystore (Redis) instance from GKE clusters that are in the same region and use the same network as your instance.
- You cannot connect to a Memorystore (Redis) instance from a GKE cluster without VPC-native/IP aliasing enabled.

## Deploy Online Boutique connected to a Memorystore (Redis) instance

To automate the deployment of Online Boutique integrated with Memorystore (Redis) you can leverage the following variation with [Kustomize](../..).

From the `kustomize/` folder at the root level of this repository, execute this command:
```
kustomize edit add components/memorystore
```
_Note: this Kustomize component will also remove the `redis-cart` `Deployment` and `Service` not used anymore._

This will update the `kustomize/kustomization.yaml` file which could be similar to:
```
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/memorystore
```

Update current Kustomize manifest to target this Memorystore (Redis) instance.
```sh
MEMORYSTORE_REGION=replace-with-the-region-of-your-memorystore-instance
REDIS_IP=$(gcloud redis instances describe redis-cart --region=${MEMORYSTORE_REGION} --format='get(host)')
REDIS_PORT=$(gcloud redis instances describe redis-cart --region=${MEMORYSTORE_REGION} --format='get(port)')
sed -i "s/{{REDIS_ADDR}}/${REDIS_IP}:${REDIS_PORT}/g" components/memorystore/kustomization.yaml
```

You can locally render these manifests by running `kubectl kustomize .` as well as deploying them by running `kubectl apply -k .`.

## Resources

- [Connecting to a Redis instance from a Google Kubernetes Engine cluster](https://cloud.google.com/memorystore/docs/redis/connect-redis-instance-gke)
- [Seamlessly encrypt traffic from any apps in your Mesh to Memorystore (Redis)](https://medium.com/google-cloud/64b71969318d)
