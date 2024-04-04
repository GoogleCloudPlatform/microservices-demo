# Releasing Online Boutique

This document walks through the process of creating a new release of Online Boutique.

## Creating a new release

1. Decide on the next release version number using [semantic versioning](https://semver.org/), based on the [commits since the previous release](https://github.com/GoogleCloudPlatform/microservices-demo/commits/main).

2. Open a new terminal.

3. Make sure you have `gsed` installed. If not, `brew install gnu-sed`.

4. Set the following environment variables:

   - `TAG` - This is the new version (e.g., `v0.3.5`).
   - `REPO_PREFIX` - This is the Docker repository.
   - `PROJECT_ID` - This is the Google Cloud project in which Google Cloud Build will be used to remotely build microservice Docker images.

   **Example:**

   ```
   export TAG=v0.3.5
   export REPO_PREFIX=gcr.io/google-samples/microservices-demo
   export PROJECT_ID=google-samples
   ```

5. Run `./docs/releasing/make-release.sh`.

   - Make sure you run `./docs/releasing/make-release.sh` from this project's root directory — **not** from inside the `docs/releasing/` directory.
   - This script:
     1. uses `make-docker-images.sh` to build and push a Docker image for each microservice to the previously specified repository.
     1. uses `make-release-artifacts.sh` to regenerates (and update the image $TAGS) YAML file at `./release/kubernetes-manifests.yaml` and `./kustomize/base/`.
     1. runs `git tag` and pushes a new branch (e.g., `release/v0.3.5`) with the changes to `./release/kubernetes-manifests.yaml`.

6. Make sure the new Docker images were created and pushed.

   - Go through [our Container Registry repository](https://pantheon.corp.google.com/gcr/images/google-samples/global/microservices-demo?project=google-samples).
   - Make sure a Docker image was created for each microservice (with the new version tag).

7. [Draft a new release on GitHub](https://github.com/GoogleCloudPlatform/microservices-demo/releases).

   - Summarize the [commits since the previous release](https://github.com/GoogleCloudPlatform/microservices-demo/commits/main).
   - See previous releases for inspiration on release notes.

8. Create a new pull-request.

   - When you ran `make-release.sh`, it created a new branch (e.g., `release/v0.3.5`).
   - Include the new release draft in the pull-request description for reviewers to see.

9. Once your pull-request is approved, merge it.

10. Connect to our [online-boutique-release GKE cluster](https://pantheon.corp.google.com/kubernetes/clusters/details/us-central1-c/online-boutique-release/details?project=online-boutique-ci).

   ```
   gcloud container clusters get-credentials online-boutique-release \
     --zone us-central1-c --project online-boutique-ci
   ```

11. Deploy `release/kubernetes-manifests.yaml` to our [online-boutique-release GKE cluster](https://pantheon.corp.google.com/kubernetes/clusters/details/us-central1-c/online-boutique-release/details?project=online-boutique-ci).

   ```
   kubectl apply -f ./release/kubernetes-manifests.yaml
   ```

12. Make sure [cymbal-shops.retail.cymbal.dev](https://cymbal-shops.retail.cymbal.dev) works.

13. [Publish your draft release on GitHub](https://github.com/GoogleCloudPlatform/microservices-demo/releases).
