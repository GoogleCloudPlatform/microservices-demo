# Integrate Online Boutique with Spanner

By default the `cartservice` stores its data in an in-cluster Redis database.
Using a fully managed database service outside your GKE cluster (such as [Google Cloud Spanner](https://cloud.google.com/spanner)) could bring more resiliency and more security.

## Provision a Spanner database

To provision a Spanner instance you can follow the following instructions:

```bash
gcloud services enable spanner.googleapis.com

SPANNER_REGION_CONFIG="<your-spanner-region-config-name>" # e.g. "regional-us-east5"
SPANNER_INSTANCE_NAME=onlineboutique

gcloud spanner instances create ${SPANNER_INSTANCE_NAME} \
    --description="online boutique shopping cart" \
    --config ${SPANNER_REGION_CONFIG} \
    --instance-type free-instance
```

_Note: With latest version of `gcloud` we are creating a free Spanner instance._

To provision a Spanner database you can follow the following instructions:

```bash
SPANNER_DATABASE_NAME=carts

gcloud spanner databases create ${SPANNER_DATABASE_NAME} \
    --instance ${SPANNER_INSTANCE_NAME} \
    --database-dialect GOOGLE_STANDARD_SQL \
    --ddl "CREATE TABLE CartItems (userId STRING(1024), productId STRING(1024), quantity INT64) PRIMARY KEY (userId, productId); CREATE INDEX CartItemsByUserId ON CartItems(userId);"
```

## Grant the `cartservice`'s service account access to the Spanner database

**Important note:** Your GKE cluster should have [Workload Identity enabled](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity#enable).

As a good practice, let's create a dedicated least privilege Google Service Account to allow the `cartservice` to communicate with the Spanner database:

```bash
PROJECT_ID=<your-project-id>
SPANNER_DB_USER_GSA_NAME=spanner-db-user-sa
SPANNER_DB_USER_GSA_ID=${SPANNER_DB_USER_GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
ONLINEBOUTIQUE_NAMESPACE=default
CARTSERVICE_KSA_NAME=cartservice

gcloud iam service-accounts create ${SPANNER_DB_USER_GSA_NAME} \
    --display-name=${SPANNER_DB_USER_GSA_NAME}

gcloud spanner databases add-iam-policy-binding ${SPANNER_DATABASE_NAME} \
    --member "serviceAccount:${SPANNER_DB_USER_GSA_ID}" \
    --role roles/spanner.databaseUser

gcloud iam service-accounts add-iam-policy-binding ${SPANNER_DB_USER_GSA_ID} \
    --member "serviceAccount:${PROJECT_ID}.svc.id.goog[${ONLINEBOUTIQUE_NAMESPACE}/${CARTSERVICE_KSA_NAME}]" \
    --role roles/iam.workloadIdentityUser
```

## Deploy Online Boutique connected to a Spanner database

To automate the deployment of Online Boutique integrated with Spanner you can leverage the following variation with [Kustomize](../..).

From the `kustomize/` folder at the root level of this repository, execute these commands:

```bash
kustomize edit add component components/service-accounts
kustomize edit add component components/spanner
```

_Note: this Kustomize component will also remove the `redis-cart` `Deployment` and `Service` not used anymore._

This will update the `kustomize/kustomization.yaml` file which could be similar to:

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
- base
components:
- components/service-accounts
- components/spanner
```

Update current Kustomize manifest to target this Spanner database.

```bash
sed -i "s/SPANNER_PROJECT/${PROJECT_ID}/g" components/spanner/kustomization.yaml
sed -i "s/SPANNER_INSTANCE/${SPANNER_INSTANCE_NAME}/g" components/spanner/kustomization.yaml
sed -i "s/SPANNER_DATABASE/${SPANNER_DATABASE_NAME}/g" components/spanner/kustomization.yaml
sed -i "s/SPANNER_DB_USER_GSA_ID/${SPANNER_DB_USER_GSA_ID}/g" components/spanner/kustomization.yaml
```

You can locally render these manifests by running `kubectl kustomize .` as well as deploying them by running `kubectl apply -k .`.

## Note on Spanner connection environment variables

The following environment variables will be used by the `cartservice`, if present:

- `SPANNER_INSTANCE`: defaults to `onlineboutique`, unless specified.
- `SPANNER_DATABASE`: defaults to `carts`, unless specified.
- `SPANNER_CONNECTION_STRING`: defaults to `projects/${SPANNER_PROJECT}/instances/${SPANNER_INSTANCE}/databases/${SPANNER_DATABASE}`. If this variable is defined explicitly, all other environment variables will be ignored.

## Resources

- [Use Google Cloud Spanner with the Online Boutique sample apps](https://medium.com/google-cloud/f7248e077339)
