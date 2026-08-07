#!/bin/sh
#
# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -e
set -x

# Set sensible defaults
REGION=us-central1
ALLOYDB_CLUSTER_NAME=onlineboutique-cluster
ALLOYDB_CARTS_DATABASE_NAME=carts
ALLOYDB_CARTS_TABLE_NAME=cart_items
ALLOYDB_PRODUCTS_DATABASE_NAME=products
ALLOYDB_PRODUCTS_TABLE_NAME=catalog_items

# Fetch the primary and read IPs
ALLOYDB_PRIMARY_IP=`gcloud alloydb instances list --region=${REGION} --cluster=${ALLOYDB_CLUSTER_NAME} --filter="INSTANCE_TYPE:PRIMARY" --format=flattened | sed -nE "s/ipAddress:\s*(.*)/\1/p"`

# Create carts database and table
psql -h ${ALLOYDB_PRIMARY_IP} -U postgres -c "CREATE DATABASE ${ALLOYDB_CARTS_DATABASE_NAME}"
psql -h ${ALLOYDB_PRIMARY_IP} -U postgres -d ${ALLOYDB_CARTS_DATABASE_NAME} -c "CREATE TABLE ${ALLOYDB_CARTS_TABLE_NAME} (userId text, productId text, quantity int, PRIMARY KEY(userId, productId))"
psql -h ${ALLOYDB_PRIMARY_IP} -U postgres -d ${ALLOYDB_CARTS_DATABASE_NAME} -c "CREATE INDEX cartItemsByUserId ON ${ALLOYDB_CARTS_TABLE_NAME}(userId)"

# Create products database, table, and extensions
psql -h ${ALLOYDB_PRIMARY_IP} -U postgres -c "CREATE DATABASE ${ALLOYDB_PRODUCTS_DATABASE_NAME}"
psql -h ${ALLOYDB_PRIMARY_IP} -U postgres -d ${ALLOYDB_PRODUCTS_DATABASE_NAME} -c "CREATE EXTENSION IF NOT EXISTS vector"
psql -h ${ALLOYDB_PRIMARY_IP} -U postgres -d ${ALLOYDB_PRODUCTS_DATABASE_NAME} -c "CREATE EXTENSION IF NOT EXISTS google_ml_integration CASCADE;"
psql -h ${ALLOYDB_PRIMARY_IP} -U postgres -d ${ALLOYDB_PRODUCTS_DATABASE_NAME} -c "GRANT EXECUTE ON FUNCTION embedding TO postgres;"
psql -h ${ALLOYDB_PRIMARY_IP} -U postgres -d ${ALLOYDB_PRODUCTS_DATABASE_NAME} -c "CREATE TABLE ${ALLOYDB_PRODUCTS_TABLE_NAME} (id TEXT PRIMARY KEY, name TEXT, description TEXT, picture TEXT, price_usd_currency_code TEXT, price_usd_units INTEGER, price_usd_nanos BIGINT, categories TEXT, product_embedding VECTOR(768), embed_model TEXT)"

# Generate and insert products table entries
python3 ./generate_sql_from_products.py > products.sql
psql -h ${ALLOYDB_PRIMARY_IP} -U postgres -d ${ALLOYDB_PRODUCTS_DATABASE_NAME} -f products.sql
rm products.sql

# Generate vector embeddings
psql -h ${ALLOYDB_PRIMARY_IP} -U postgres -d ${ALLOYDB_PRODUCTS_DATABASE_NAME} -c "UPDATE ${ALLOYDB_PRODUCTS_TABLE_NAME} SET product_embedding = embedding('textembedding-gecko@003', description), embed_model='textembedding-gecko@003';"
