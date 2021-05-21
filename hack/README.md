## Tagging a release

Make sure that the following two commands are in your `PATH`:
- `realpath` (It can be found in the `coreutils` package if not already present.)
- `skaffold`
- `gcloud`

When you're ready, run the `make-release.sh` script found inside the `release` folder.

```sh
# assuming you are inside the root path of the microservices-demo repository
export NEW_VERSION=vX.Y.Z
export REPO_PREFIX=gcr.io/google-samples/microservices-demo
./release/make-release.sh
```

This script does the following:
1. Replaces the existing `kubernetes-manifests` with the contents of `dev-kubernetes-manifests`.
2. Updates the image tag for all the Deployments in the new `kubernetes-manifests`, with the new release tag.
3. Uses `git tag` to create a new local release.
4. Creates a new release branch.
5. Uses `skaffold` to build and push new stable release images to `gcr.io/google-samples/microservices-demo`.
6. Pushes the Git tags and the release branch.

### Troubleshooting script failures

In the event of any of the steps above failing you might have to revert the repository to its original state. Follow the steps below as required:
```sh
# delete the newly created release branch & tag before re-running the script
git checkout master
git branch -D release/$NEW_VERSION
git tag -d $NEW_VERSION

# delete temporary files created
rm kubernetes-manifests/*-e
```

## Creating a PR

Now that the release branch has been created, you can find it in the [list of branches](https://github.com/GoogleCloudPlatform/microservices-demo/branches) and create a pull request targeting `master` (the default branch).

This process is going to trigger multiple CI checks as well as stage the release onto a temporary cluster. Once the PR has been approved and all checks are successfully passing, you can now merge the branch.

## Add notes to release

Once the PR has been fully merged, you are ready to create a new release for the newly created [tag](https://github.com/GoogleCloudPlatform/microservices-demo/tags).
- Click the breadcrumbs on the row of the latest tag that was created in the [tags](https://github.com/GoogleCloudPlatform/microservices-demo/tags) page
- Select the `Create release` option

The release notes should contain a brief description of the changes since the previous release (like bug fixed and new features). For inspiration, you can look at the list of [releases](https://github.com/GoogleCloudPlatform/microservices-demo/releases).

> ***Note:*** No assets need to be uploaded. They are picked up automatically from the tagged revision

## Deploy on the production environment

Once the release notes are published, you should then replace the version of the production environment to the newly published version.

1. Make sure you are connected to the production cluster: 
   
```
gcloud container clusters get-credentials online-boutique-master --zone us-west1-a --project onlineboutique-ci
```

2. Apply the new manifest versions on top of the current environment:
```
kubectl apply -f ./kubernetes-manifests
```
