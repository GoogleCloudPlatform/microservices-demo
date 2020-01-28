# GitHub Actions Workflows

## Setup
- workloads run using [GitHub self-hosted runners](https://help.github.com/en/actions/automating-your-workflow-with-github-actions/about-self-hosted-runners)
- project admins maintain a private Google Compute Engine VM for running tests
  - VM should be at least n1-standard-4 with 50GB persistent disk
  - instructions for setting up the VM can be found in repo settings under "Actions"
  - ⚠️  WARNING: VM should be set up with no GCP service account
    - external contributors could contribute malicious PRs to run code on our test VM. Ensure no service accounts or other secrets exist on the VM
    - An empty GCP project should be used for extra security
  - to set up dependencies, run the following commands:
    ```
    # install kubectl
    sudo apt-get install kubectl

    # install kind
    curl -Lo ./kind "https://github.com/kubernetes-sigs/kind/releases/download/v0.7.0/kind-$(uname)-amd64" && \
    chmod +x ./kind && \
    sudo mv ./kind /usr/local/bin

    # install skaffold
    curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64 && \
    chmod +x skaffold && \
    sudo mv skaffold /usr/local/bin

    # install docker
    sudo apt install apt-transport-https ca-certificates curl gnupg2 software-properties-common && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add - && \
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable" && \
    sudo apt update && \
    sudo apt install docker-ce && \
    sudo usermod -aG docker ${USER}

    # logout and back on
    exit
    ```
  - ensure GitHub Actions runs as background service:
    ```
    sudo ∼/actions-runner/svc.sh install
    sudo ∼/actions-runner/svc.sh start
    ```


---
## Workflows

### Smoketests.yaml

#### Triggers
- commits pushed to master
- PRs to master
- PRs to release/ branches

#### Actions
- ensures kind cluster is running
- builds all containers in src/
- deploys local containers to kind
  - ensures all pods reach ready state
  - ensures HTTP request to frontend returns HTTP status 200
- deploys manifests from /releases
  - ensures all pods reach ready state
  - ensures HTTP request to frontend returns HTTP status 200
