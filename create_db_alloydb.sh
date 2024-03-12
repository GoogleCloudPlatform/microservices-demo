#!/bin/sh

set -e
set -x

# Set sensible defaults
REGION=us-central1
ALLOYDB_CLUSTER_NAME=onlineboutique-cluster
ALLOYDB_DATABASE_NAME=carts
ALLOYDB_TABLE_NAME=cart_items

# Fetch the primary and read IPs
ALLOYDB_PRIMARY_IP=`gcloud alloydb instances list --region=${REGION} --cluster=${ALLOYDB_CLUSTER_NAME} --filter="INSTANCE_TYPE:PRIMARY" --format=flattened | sed -nE "s/ipAddress:\s*(.*)/\1/p"`
ALLOYDB_READ_IP=`gcloud alloydb instances list --region=${REGION} --cluster=${ALLOYDB_CLUSTER_NAME} --filter="INSTANCE_TYPE:READ_POOL" --format=flattened | sed -nE "s/ipAddress:\s*(.*)/\1/p"`

# Create database and products table
psql -h ${ALLOYDB_PRIMARY_IP} -U postgres -c "CREATE DATABASE ${ALLOYDB_DATABASE_NAME}"
psql -h ${ALLOYDB_PRIMARY_IP} -U postgres -d ${ALLOYDB_DATABASE_NAME} -c "CREATE TABLE ${ALLOYDB_TABLE_NAME} (userId text, productId text, quantity int, PRIMARY KEY(userId, productId))"
psql -h ${ALLOYDB_PRIMARY_IP} -U postgres -d ${ALLOYDB_DATABASE_NAME} -c "CREATE INDEX cartItemsByUserId ON ${ALLOYDB_TABLE_NAME}(userId)"
