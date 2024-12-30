# Shopping Assistant with RAG & AlloyDB

This demo adds a new service to Online Boutique called `shoppingassistantservice` which, alongside an Alloy-DB backed products catalog, adds a RAG-featured AI assistant to the frontned experience, helping users suggest products matching their home decor.

## Setup instructions

**Note:** This demo requires a Google Cloud project where you to have the `owner` role, else you may be unable to enable APIs or modify VPC rules that are needed for this demo.

1. Set some environment variables.
    ```sh
    export PROJECT_ID=<project_id>
    export PROJECT_NUMBER=<project_number>
    export PGPASSWORD=<pgpassword>
    ```

    **Note**: The project ID and project number of your Google Cloud project can be found in the Console. The PostgreSQL password can be set to anything you want, but make sure to note it down.

1. Change your default Google Cloud project.
    ```sh
    gcloud auth login
    gcloud config set project $PROJECT_ID
    ```

1. Enable the Google Kubernetes Engine (GKE) and Artifact Registry (AR) APIs.
    ```sh
    gcloud services enable container.googleapis.com
    gcloud services enable artifactregistry.googleapis.com
    ```

1. Create a GKE Autopilot cluster. This may take a few minutes.
    ```sh
    gcloud container clusters create-auto cymbal-shops \
        --region=us-central1
    ```

1. Change your Kubernetes context to your newly created GKE cluster.
    ```sh
    gcloud container clusters get-credentials cymbal-shops \
        --region us-central1
    ```

1. Create an Artifact Registry container image repository.
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

1. Run script #1. If it asks about policy bindings, select the option `None`. This may take a few minutes.
    ```sh
    ./kustomize/components/shopping-assistant/scripts/1_deploy_alloydb_infra.sh
    ```

    **Note**: If you are on macOS and use a non-GNU version of `sed`, you may have to tweak the script to use `gsed` instead.

1. Create a Linux VM in Compute Engine (GCE).
    ```sh
    gcloud compute instances create gce-linux \
        --zone=us-central1-a \
        --machine-type=e2-micro \
        --image-family=debian-12 \
        --image-project=debian-cloud 
    ```

1. SSH into the VM. From here until we exit, all steps happen in the VM.
    ```sh
    gcloud compute ssh gce-linux \
        --zone "us-central1-a"
    ```

1. Install the Postgres client and set your default Google Cloud project.
    ```sh
    sudo apt-get install -y postgresql-client
    gcloud auth login
    gcloud config set project <PROJECT_ID>
    ```

1. Copy script #2, the python script, and the products.json to the VM. Make sure the scripts are executable.
    ```sh
    nano 2_create_populate_alloydb_tables.sh # paste content
    nano generate_sql_from_products.py # paste content
    nano products.json # paste content
    chmod +x 2_create_populate_alloydb_tables.sh
    chmod +x generate_sql_from_products.py
    ```

    **Note:** You can find the files at the following places:
    - `kustomize/components/shopping-assistant/scripts/2_create_populate_alloydb_tables.sh`
    - `kustomize/components/shopping-assistant/scripts/generate_sql_from_products.py`
    - `src/productcatalogservice/products.json`

1. Run script #2 in the VM. If it asks for a postgres password, it should be the same that you set in script #1 earlier. This may take a few minutes.
    ```sh
    ./2_create_populate_alloydb_tables.sh
    ```

1. Exit SSH.
    ```sh
    exit
    ```

1. Create an API key in the [Credentials page](https://pantheon.corp.google.com/apis/credentials) with permissions for "Generative Language API", and make note of the secret key.

1. Replace the Google API key placeholder in the shoppingassistant service.
    ```sh
    export GOOGLE_API_KEY=<google_api_key>
    sed -i "s/GOOGLE_API_KEY_VAL/${GOOGLE_API_KEY}/g" kustomize/components/shopping-assistant/shoppingassistantservice.yaml
    ```

1. Edit the root Kustomize file to enable the `alloydb` and `shopping-assistant` components.
    ```sh
    nano kubernetes-manifests/kustomization.yaml # make the modifications below
    ```
    
    ```yaml
    # ...head of the file
    components: # remove this comment
    # - ../kustomize/components/cymbal-branding
    # - ../kustomize/components/google-cloud-operations
    # - ../kustomize/components/memorystore
    # - ../kustomize/components/network-policies
     - ../kustomize/components/alloydb # remove this comment
     - ../kustomize/components/shopping-assistant # remove this comment
    # - ../kustomize/components/spanner
    # - ../kustomize/components/container-images-tag
    # - ../kustomize/components/container-images-tag-suffix
    # - ../kustomize/components/container-images-registry
    ```

1. Deploy to the GKE cluster.
    ```sh
    skaffold run --default-repo=us-central1-docker.pkg.dev/$PROJECT_ID/images
    ```

1. Wait for all the pods to be up and running. You can then find the external IP and navigate to it.
    ```sh
    kubectl get pods
    kubectl get services
    ```
