# Shopping Assistant with RAG & AlloyDB

This demo adds a new service to Online Boutique called `shoppingassistantservice`, which, alongside an Alloy-DB backed products catalog, adds a RAG-featured AI assistant to the frontned experience, which helps users suggest new products for their room decor.

## Set-up instructions

> Note: Make sure you have the `owner` role to the Google Cloud project you want to deploy this to, else you will be unable to enable certain APIs or modify certain VPC rules that are needed for this demo.

1. Enable the Google Kubernetes Engine (GKE) and Artifact Registry (AR) APIs.
    ```sh
    gcloud services enable container.googleapis.com
    gcloud services enable artifactregistry.googleapis.com
    ```

1. Create a GKE Autopilot cluster.
    ```sh
    gcloud container clusters create-auto cymbal-shops \
        --region=us-central1
    ```

1. Create an AR Docker image repository.
    ```sh
    gcloud artifacts repositories create images \
        --repository-format=docker \
        --location=us-central1
    ```

1. Clone the `microservices-demo` repository locally.
    ```sh
    git clone https://github.com/GoogleCloudPlatform/microservices-demo \
        && cd microservices-demo/
    ```

1. Context into the right project and GKE cluster.
    ```sh
    gcloud auth login
    gcloud config set project <PROJECT_ID>
    gcloud container clusters get-credentials cymbal-shops \
        --region us-central1
    ```

1. Replace the placeholder variables into infra script #1 and run it. If it asks about policy bindings, select the option for "None".
    ```sh
    vim kustomize/components/shopping-assistant/scripts/1_deploy_alloydb_infra.sh
    ./scripts/1_deploy_alloydb_infra.sh
    ```

1. Create micro Linux VM on GCP
    ```sh
    gcloud compute instances create gce-linux \
        --zone=us-central1-a \
        --machine-type=e2-micro \
        --image-family=debian-12-bookworm-v20240312 \
        --image-project=debian-cloud 
    ```

1. SSH into the VM. From here until we exit, all steps happen in the VM.
    ```sh
    gcloud compute ssh gce-linux \
        --zone "us-central1-a"
    ```

1. Install the Postgres client and context into the right project.
    ```sh
    sudo apt-get install -y postgresql-client
    gcloud auth login
    gcloud config set project <PROJECT_ID>
    ```

1. Copy script #2, the python script, and the updated products.json to the VM. Make sure the scripts are executable.
    ```sh
    vim 2_create_populate_alloydb_tables.sh
    vim generate_sql_from_products.py
    vim products.json
    chmod +x 2_create_populate_alloydb_tables.sh
    chmod +x generate_sql_from_products.py
    ```

    > Note: You can find the files at the following places:
    > - kustomize/components/shopping-assistant/scripts/2_create_populate_alloydb_tables.sh
    > - kustomize/components/shopping-assistant/scripts/generate_sql_from_products.py
    > - src/productcatalogservice/products.json

1. Run script #2 in the VM. If it asks for a postgres password, it should be the same that you set in script #1 earlier.
    ```sh
    ./2_create_populate_alloydb_tables.sh
    ```

1. Exit SSH
    ```sh
    exit
    ```

1. Create an API key in the [Credentials page](https://pantheon.corp.google.com/apis/credentials) with permissions for "Generative Language API", and make note of the secret key.

1. Paste this secret key in the shopping assistant service envs, replacing `GOOGLE_API_KEY_VAL`.
    ```sh
    vim kustomize/components/shopping-assistant/shoppingassistantservice.yaml
    ```

1. Change the commented-out components in `kubernetes-manifests/kustomization.yaml` to look like this:
    ```yaml
    components: # remove comment
    # - ../kustomize/components/cymbal-branding
    # - ../kustomize/components/google-cloud-operations
    # - ../kustomize/components/memorystore
    # - ../kustomize/components/network-policies
     - ../kustomize/components/alloydb # remove comment
     - ../kustomize/components/shopping-assistant # remove comment
    # - ../kustomize/components/spanner
    # - ../kustomize/components/container-images-tag
    # - ../kustomize/components/container-images-tag-suffix
    # - ../kustomize/components/container-images-registry
    ```

1. Deploy to the GKE cluster.
    ```
    skaffold run --default-repo=us-central1-docker.pkg.dev/<PROJECT_ID>/images
    ```

1. Wait for all the pods to be up and running. You can then find the external IP and navigate to it.
    ```sh
    kubectl get pods
    kubectl get services
    ```
