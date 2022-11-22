# Integrate Online Boutique with Redis Enterprise in Google Cloud Marketplace

By default, the `cartservice` serializes its data in an in-cluster Redis database. Using a database outside your Google Kubernetes Engine (GKE) cluster, such as a managed service like [Redis Enterprise](https://redis.io/docs/about/redis-enterprise/) in Google Cloud Marketplace, could bring more resiliency and more security.

![Architecture diagram with Redis Enterprise](/docs/img/redis-enterprise/redis-enterprise.png)
  
To provision a fully managed Redis Enterprise database instance you can follow the instructions [here](https://github.com/Redislabs-Solution-Architects/redis-enterprise-cloud-gcp/blob/main/marketplace/gcp/redis-enterprise.md).  

The ['/terraform'](/terraform) folder of this repository contains Terraform scripts for provisioning a fully managed Redis Enterprise database instance alongside a GKE cluster. To use Terraform, you are required to collect the [Redis Cloud Access Key](https://docs.redis.com/latest/rc/api/get-started/enable-the-api/) and [Redis Cloud Secret Key](https://docs.redis.com/latest/rc/api/get-started/manage-api-keys/#secret) and save them in your environment variables namely `REDISCLOUD_ACCESS_KEY` and `REDISCLOUD_SECRET_KEY`.

Important notes:
- You cannot connect to a fully managed Redis Enterprise database (redis) instance via private endpoint from a GKE cluster without peering your VPC to Redis's managed VPC.
    
## Deploy Online Boutique connected to a fully managed Redis Enterprise database instance

To automate the deployment of Online Boutique integrated with a fully managed Redis Enterprise database instance you can leverage the following variation with [Kustomize](/kustomize).

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
sed -i "s/REDIS_CONNECTION_STRING/${REDIS_IP}/g" components/redis-enterprise/kustomization.yaml
```
   
You can locally render these manifests by running `kubectl kustomize .` as well as deploying them by running `kubectl apply -k .`.
