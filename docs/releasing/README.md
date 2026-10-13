# Releasing Online Boutique

This document walks through the process of creating a new release of Online Boutique.

## Prerequisites for tagging a release

1. Choose the logical [next release tag](https://github.com/GoogleCloudPlatform/microservices-demo/releases), using [semantic versioning](https://semver.org/): `vX.Y.Z`.

   If this release includes significant feature changes, update the minor version (`Y`). Otherwise, for bug-fix releases or standard quarterly release, update the patch version `Z`).

2. Ensure that the following commands are in your `PATH`:
   - `gsed` (found in the `gnu-sed` Brew package for macOS, or by symlinking `sed` for Linux)
   - `gcloud`
   - `helm`

3. Make sure that your `gcloud` is authenticated:

   ```sh
   gcloud auth login
   gcloud auth configure-docker us-central1-docker.pkg.dev
   ```

## Create the release branch and PR

The preferred way to start a new release is to run the **Manual Release Builder** workflow in GitHub Actions.

### Trigger the release workflow

1. Go to the **Actions** tab of the repository on GitHub.
2. Select the **Manual Release Builder** workflow from the left sidebar.
3. Click the **Run workflow** dropdown button.
4. Fill in the parameters:
   - **The release version (e.g., v0.3.5)**: Set the version string `vX.Y.Z`.
   - **The repository prefix for container images**: Defaults to `us-central1-docker.pkg.dev/online-boutique-ci/microservices-demo`.
   - **The Google Cloud Project ID for the release CI**: Defaults to `online-boutique-ci`.
5. Click **Run workflow**.

This workflow will:
1. Build and push the container images for all services.
2. Regenerate YAML manifests and Kustomize bases.
3. Package and push the Helm chart.
4. Create and push a new branch `release/vX.Y.Z` and a git tag `vX.Y.Z`.
5. Automatically open a Pull Request targeting `main` with the release checklist.

### Alternative: Manual release script

If you need to run the release process manually from your local machine, ensure you have the prerequisites installed and authenticated. Then run the `make-release.sh` script:

```sh
# assuming you are inside the root path of the microservices-demo repository
export TAG=vX.Y.Z # This is the new version (e.g. `v0.3.5`)
export REPO_PREFIX=us-central1-docker.pkg.dev/online-boutique-ci/microservices-demo # This is the Docker repository for tagged images
export PROJECT_ID=online-boutique-ci # This is the Google Cloud project for the release CI
./docs/releasing/make-release.sh
```

Once the script completes, you can go to the GitHub branches list to manually create a pull request targeting `main`.

This process is going to trigger multiple CI checks as well as stage the release onto a temporary cluster. Once the PR has been approved and all checks are successfully passing, you can then merge the branch. Make sure to include the release draft (see next section) in the pull-request description for reviewers to see.

Once reviewed and you're ready to merge, make sure to not delete the release branch or the tags during that process.

## Add notes to the release

Once the PR has been fully merged, you are ready to create a new release for the newly created [tag](https://github.com/GoogleCloudPlatform/microservices-demo/tags).
- Click the breadcrumbs on the row of the latest tag that was created in the [tags](https://github.com/GoogleCloudPlatform/microservices-demo/tags) page
- Select the `Create release` option

The release notes should contain a brief description of the changes since the previous release (like bug fixed and new features). For inspiration, you can look at the list of [releases](https://github.com/GoogleCloudPlatform/microservices-demo/releases).

> ***Note:*** No assets need to be uploaded. They are picked up automatically from the tagged revision

## Deploy on the production environment

Once the release notes are published, you should then replace the version of the production environment to the newly published version.

1. Connect to the [online-boutique-release GKE cluster](https://pantheon.corp.google.com/kubernetes/clusters/details/us-central1-c/online-boutique-release/details?project=online-boutique-ci):

   ```sh
   gcloud container clusters get-credentials online-boutique-release \
     --zone us-central1-c --project online-boutique-ci
   ```

2. Deploy `release/kubernetes-manifests.yaml` to it:

   ```sh
   kubectl apply -f ./release/kubernetes-manifests.yaml
   ```

3. Remove unnecessary objects:

   ```sh
   kubectl delete service frontend-external
   kubectl delete deployment loadgenerator
   ```

3. Make sure [cymbal-shops.retail.cymbal.dev](https://cymbal-shops.retail.cymbal.dev) works.

## Update major tags

1. Update the relevant major tag (for example, `v1`):

  ```sh
  export MAJOR_TAG=v0 # Edit this as needed (to v1/v2/v3/etc)
  git checkout release/${TAG}
  git pull
  git push --delete origin ${MAJOR_TAG} # Delete the remote tag (if it exists)
  git tag --delete ${MAJOR_TAG} # Delete the local tag (if it exists)
  git tag -a ${MAJOR_TAG} -m "Updating ${MAJOR_TAG} to its most recent release: ${TAG}"
  git push origin ${MAJOR_TAG} # Push the new tag to origin
  ```

## Announce the new release internally

Once the new release is out, you can now announce it via [g/online-boutique-announce](https://groups.google.com/a/google.com/g/online-boutique-announce).
