# Integrate Online Boutique with Redis Enterprise in Google Cloud Marketplace

By default the `cartservice` app is serializing the data in an in-cluster Redis database. Using a database outside your GKE cluster could bring more resiliency and more security with a managed service like Redis Enterprise in Google Cloud Marketplace.

![Architecture diagram with Redis Enterprise](/docs/img/redis-enterprise/redis-enterprise.png)
  
To provision a fully managed Redis Enterprise database instance you can follow the instructions [here](./redis-enterprise.md).  

You can also find in this repository the Terraform script to provision the fully managed Redis Enterprise database instance alongside the GKE cluster, more information [here](/terraform). To use Terraform, you are required to collect the [Redis Cloud Access Key](https://docs.redis.com/latest/rc/api/get-started/enable-the-api/) and [Redis Cloud Secret Key](https://docs.redis.com/latest/rc/api/get-started/manage-api-keys/#secret) and save them in your environment variables namely `REDISCLOUD_ACCESS_KEY` and `REDISCLOUD_SECRET_KEY`.

Important notes:
- You cannot connect to a fully managed Redis Enterprise database (redis) instance via private endpoint from a GKE cluster without peering your VPC to Redis's managed VPC.
    
## Deploy Online Boutique connected to a fully managed Redis Enterprise database instance

To automate the deployment of Online Boutique integrated with a fully managed Redis Enterprise database instance you can leverage the following variation with [Kustomize](../..).

From the `kustomize/` folder at the root level of this repository, execute this command:
```
kustomize edit add component components/redis-enterprise
```
_Note: this Kustomize component will also remove the `redis-cart` `Deployment` and `Service` not used anymore._

This will update the `kustomize/kustomization.yaml` file which could be similar to:
```
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/redis-enterprise
```

Update current Kustomize manifest to target this fully managed Redis Enterprise database instance
Construct the connection string for the fully managed Redis Enterprise database instance:
```
REDIS_IP="<database's private endpoint>,user=default,password=<default user's password>"

For example,
REDIS_IP="redis-15219.internal.c21247.us-central1-mz.gcp.cloud.rlrcp.com:15219,user=default,password=VJKeYjdXQgaPnqpU5Ypktx1qhzNYeEOI"
```
```
sed -i .bak "s/REDIS_CONNECTION_STRING/${REDIS_IP}/g" components/redis-enterprise/kustomization.yaml
```
   
You can locally render these manifests by running `kubectl kustomize .` as well as deploying them by running `kubectl apply -k .`.
