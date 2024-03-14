#!/bin/sh

set -e
set -x

# Replace me
PROJECT_ID=<project_id>
PROJECT_NUMBER=<project_number>
PGPASSWORD=<password>

# Set sensible defaults
REGION=us-central1
USE_GKE_GCLOUD_AUTH_PLUGIN=True
ALLOYDB_NETWORK=default
ALLOYDB_SERVICE_NAME=onlineboutique-network-range
ALLOYDB_CLUSTER_NAME=onlineboutique-cluster
ALLOYDB_INSTANCE_NAME=onlineboutique-instance
ALLOYDB_DATABASE_NAME=carts
ALLOYDB_TABLE_NAME=cart_items
ALLOYDB_USER_GSA_NAME=alloydb-user-sa
ALLOYDB_USER_GSA_ID=${ALLOYDB_USER_GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
CARTSERVICE_KSA_NAME=cartservice
ALLOYDB_SECRET_NAME=alloydb-secret

# Enable services
gcloud services enable alloydb.googleapis.com
gcloud services enable servicenetworking.googleapis.com
gcloud services enable secretmanager.googleapis.com

# Set our DB credentials behind the secret
echo $PGPASSWORD | gcloud secrets create ${ALLOYDB_SECRET_NAME} --data-file=-

# Set up needed service connection
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

# Fetch the primary and read IPs
ALLOYDB_PRIMARY_IP=`gcloud alloydb instances list --region=${REGION} --cluster=${ALLOYDB_CLUSTER_NAME} --filter="INSTANCE_TYPE:PRIMARY" --format=flattened | sed -nE "s/ipAddress:\s*(.*)/\1/p"`
ALLOYDB_READ_IP=`gcloud alloydb instances list --region=${REGION} --cluster=${ALLOYDB_CLUSTER_NAME} --filter="INSTANCE_TYPE:READ_POOL" --format=flattened | sed -nE "s/ipAddress:\s*(.*)/\1/p"`

# Substitute environment values
sed -i "s/PROJECT_ID_VAL/${PROJECT_ID}/g" kustomize/components/alloydb/kustomization.yaml
sed -i "s/ALLOYDB_PRIMARY_IP_VAL/${ALLOYDB_PRIMARY_IP}/g" kustomize/components/alloydb/kustomization.yaml
sed -i "s/ALLOYDB_USER_GSA_ID/${ALLOYDB_USER_GSA_ID}/g" kustomize/components/alloydb/kustomization.yaml
sed -i "s/ALLOYDB_DATABASE_NAME_VAL/${ALLOYDB_DATABASE_NAME}/g" kustomize/components/alloydb/kustomization.yaml
sed -i "s/ALLOYDB_TABLE_NAME_VAL/${ALLOYDB_TABLE_NAME}/g" kustomize/components/alloydb/kustomization.yaml
sed -i "s/ALLOYDB_SECRET_NAME_VAL/${ALLOYDB_SECRET_NAME}/g" kustomize/components/alloydb/kustomization.yaml

# Create service account for the cart service
gcloud iam service-accounts create ${ALLOYDB_USER_GSA_NAME} \
    --display-name=${ALLOYDB_USER_GSA_NAME}

gcloud projects add-iam-policy-binding ${PROJECT_ID} --member=serviceAccount:${ALLOYDB_USER_GSA_ID} --role=roles/alloydb.client
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member=serviceAccount:${ALLOYDB_USER_GSA_ID} --role=roles/secretmanager.secretAccessor
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member=service-${PROJECT_NUMBER}@gcp-sa-alloydb.iam.gserviceaccount.com --role=roles/aiplatform.user


gcloud iam service-accounts add-iam-policy-binding ${ALLOYDB_USER_GSA_ID} \
    --member "serviceAccount:${PROJECT_ID}.svc.id.goog[default/${CARTSERVICE_KSA_NAME}]" \
    --role roles/iam.workloadIdentityUser
