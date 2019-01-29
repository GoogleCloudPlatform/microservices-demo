## `hack/` 

This directory provides scripts for building and pushing Docker images, and tagging new demo
releases. 

### env variables 

- `TAG` - git release tag / Docker tag. 
- `REPO_PREFIX` - Docker repo prefix to push images. Format: `$user/$project`.  Resulting images will be of the
  format `$user/$project/$svcname:$tag` (where `svcname` = `adservice`, `cartservice`,
  etc.)

### scripts 

1. `./make-docker-images.sh`: builds and pushes images to the specified Docker repository.
2. `./make-release-artifacts.sh`: generates a combined YAML file with image $TAG at: 
   `./release/kubernetes-manifests/demo.yaml`. 
3. `./make-release.sh`: runs scripts 1 and 2, then runs `git tag` / pushes updated manifests to master.
