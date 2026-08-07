# Integrate Online Boutique with AlloyDB

By default the `cartservice` stores its data in an in-cluster Redis database. 
Using a fully managed database service outside your GKE cluster (such as [AlloyDB](https://cloud.google.com/alloydb)) could bring more resiliency and more security.

Note that because of AlloyDB's current connectivity, you'll need to run all this from a VM with
VPC access to the network you want to use for everything (out of the box this should just use the
default network). The Cloud Shell doesn't work because of transitive VPC peering not working.

## Provision an AlloyDB database and the supporting infrastructure

Environmental variables needed for setup. These should be set in a .bashrc or similar as some of the variables are used in the application itself. Default values are supplied in this readme, but any of them can be changed. Anything in <> needs to be replaced.

```bash
# PROJECT_ID should be set to the project ID that was created to hold the demo
PROJECT_ID=<project_id>

#Pick a region near you that also has AlloyDB available. See available regions: https://cloud.google.com/alloydb/docs/locations
REGION=<region>
USE_GKE_GCLOUD_AUTH_PLUGIN=True
ALLOYDB_NETWORK=default
ALLOYDB_SERVICE_NAME=onlineboutique-network-range
ALLOYDB_CLUSTER_NAME=onlineboutique-cluster
ALLOYDB_INSTANCE_NAME=onlineboutique-instance

# **Note:** Primary and Read IP will need to be set after you create the instance. The command to set this in the shell is included below, but it would also be a good idea to run the command, and manually set the IP address in the .bashrc
ALLOYDB_PRIMARY_IP=<ip set below after instance created>
ALLOYDB_READ_IP=<ip set below after instance created>

ALLOYDB_DATABASE_NAME=carts
ALLOYDB_TABLE_NAME=cart_items
ALLOYDB_USER_GSA_NAME=alloydb-user-sa
ALLOYDB_USER_GSA_ID=${ALLOYDB_USER_GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
CARTSERVICE_KSA_NAME=cartservice
ALLOYDB_SECRET_NAME=alloydb-secret

# PGPASSWORD needs to be set in order to run the psql from the CLI easily. The value for this
# needs to be set behind the Secret mentioned above
PGPASSWORD=<password>
```

To provision an AlloyDB instance you can follow the following instructions:
```bash
gcloud services enable alloydb.googleapis.com
gcloud services enable servicenetworking.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Set our DB credentials behind the secret. Replace <password> with whatever you want
# to use as the credentials for the database. Don't use $ in the password.
echo <password> | gcloud secrets create ${ALLOYDB_SECRET_NAME} --data-file=-

# Setting up needed service connection
gcloud compute addresses create ${ALLOYDB_SERVICE_NAME} \
    --global \
    --purpose=VPC_PEERING \
    --prefix-length=16 \
    --description="Online Boutique Private Services" \
    --network=${ALLOYDB_NETWORK}

gcloud services vpc-peerings connect \
    --service=servicenetworking.googleapis.com \
    --ranges=${ALLOYDB_SERVICE_NAME} \
    --network=${ALLOYDB_NETWORK}

gcloud alloydb clusters create ${ALLOYDB_CLUSTER_NAME} \
    --region=${REGION} \
    --password=${PGPASSWORD} \
    --disable-automated-backup \
    --network=${ALLOYDB_NETWORK}

gcloud alloydb instances create ${ALLOYDB_INSTANCE_NAME} \
    --cluster=${ALLOYDB_CLUSTER_NAME} \
    --region=${REGION} \
    --cpu-count=4 \
    --instance-type=PRIMARY
    
gcloud alloydb instances create ${ALLOYDB_INSTANCE_NAME}-replica \
    --cluster=${ALLOYDB_CLUSTER_NAME} \
    --region=${REGION} \
    --cpu-count=4 \
    --instance-type=READ_POOL \
    --read-pool-node-count=2

# Need to grab and store the IP addresses for our primary and read replicas
# Don't forget to set these two values in the environment for later use.
ALLOYDB_PRIMARY_IP=gcloud alloydb instances list --region=${REGION} --cluster=${ALLOYDB_CLUSTER_NAME} --filter="INSTANCE_TYPE:PRIMARY" --format=flattened | sed -nE "s/ipAddress:\s*(.*)/\1/p"
ALLOYDB_READ_IP=gcloud alloydb instances list --region=${REGION} --cluster=${ALLOYDB_CLUSTER_NAME} --filter="INSTANCE_TYPE:READ_POOL" --format=flattened | sed -nE "s/ipAddress:\s*(.*)/\1/p"

psql -h ${ALLOYDB_PRIMARY_IP} -U postgres -c "CREATE DATABASE ${ALLOYDB_DATABASE_NAME}"
psql -h ${ALLOYDB_PRIMARY_IP} -U postgres -d ${ALLOYDB_DATABASE_NAME} -c "CREATE TABLE ${ALLOYDB_TABLE_NAME} (userId text, productId text, quantity int, PRIMARY KEY(userId, productId))"
psql -h ${ALLOYDB_PRIMARY_IP} -U postgres -d ${ALLOYDB_DATABASE_NAME} -c "CREATE INDEX cartItemsByUserId ON ${ALLOYDB_TABLE_NAME}(userId)"
```

_Note: It can take more than 20 minutes for the AlloyDB instances to be created._

## Grant the `cartservice`'s service account access to the AlloyDB database

**Important note:** Your GKE cluster should have [Workload Identity enabled](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity#enable).

As a good practice, let's create a dedicated least privilege Google Service Account to allow the `cartservice` to communicate with the AlloyDB database and grab the database password from the Secret manager.:
```bash
gcloud iam service-accounts create ${ALLOYDB_USER_GSA_NAME} \
    --display-name=${ALLOYDB_USER_GSA_NAME}

gcloud projects add-iam-policy-binding ${PROJECT_ID} --member=serviceAccount:${ALLOYDB_USER_GSA_ID} --role=roles/alloydb.client
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member=serviceAccount:${ALLOYDB_USER_GSA_ID} --role=roles/secretmanager.secretAccessor

gcloud iam service-accounts add-iam-policy-binding ${ALLOYDB_USER_GSA_ID} \
    --member "serviceAccount:${PROJECT_ID}.svc.id.goog[default/${CARTSERVICE_KSA_NAME}]" \
    --role roles/iam.workloadIdentityUser
```

## Deploy Online Boutique connected to an AlloyDB database

To automate the deployment of Online Boutique integrated with AlloyDB you can leverage the following variation with [Kustomize](../..).

From the `kustomize/` folder at the root level of this repository, execute these commands:
```bash
kustomize edit add component components/alloydb
```
_**Note:** this Kustomize component will also remove the `redis-cart` `Deployment` and `Service` not used anymore._

This will update the `kustomize/kustomization.yaml` file which could be similar to:
```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/alloydb
```

Update current Kustomize manifest to target this AlloyDB database.
```bash
sed -i "s/PROJECT_ID_VAL/${PROJECT_ID}/g" components/alloydb/kustomization.yaml
sed -i "s/ALLOYDB_PRIMARY_IP_VAL/${ALLOYDB_PRIMARY_IP}/g" components/alloydb/kustomization.yaml
sed -i "s/ALLOYDB_USER_GSA_ID/${ALLOYDB_USER_GSA_ID}/g" components/alloydb/kustomization.yaml
sed -i "s/ALLOYDB_DATABASE_NAME_VAL/${ALLOYDB_DATABASE_NAME}/g" components/alloydb/kustomization.yaml
sed -i "s/ALLOYDB_TABLE_NAME_VAL/${ALLOYDB_TABLE_NAME}/g" components/alloydb/kustomization.yaml
sed -i "s/ALLOYDB_SECRET_NAME_VAL/${ALLOYDB_SECRET_NAME}/g" components/alloydb/kustomization.yaml
```

You can locally render these manifests by running `kubectl kustomize .` as well as deploying them by running `kubectl apply -k .`.

## Extra cleanup steps
```bash
gcloud compute addresses delete ${ALLOYDB_SERVICE_NAME} --global

# Force takes care of cleaning up the instances inside the cluster automatically
gcloud alloydb clusters delete ${ALLOYDB_CLUSTER_NAME} --force --region ${REGION}

gcloud iam service-accounts delete ${ALLOYDB_USER_GSA_ID}

gcloud secrets delete ${ALLOYDB_SECRET_NAME}
```
