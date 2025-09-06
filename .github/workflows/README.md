# GitHub Actions Workflows

This page describes the CI/CD workflows for the Online Boutique app, which run in [GitHub Actions](https://github.com/GoogleCloudPlatform/microservices-demo/actions).

## Workflow Organization

The workflows are organized into the following directories:

### `/ci` - Continuous Integration

- **[ci-pipeline.yml](ci/ci-pipeline.yml)**: Main CI pipeline that runs on every push to main and pull requests
  - Coordinates linting, CodeQL analysis, IaC scanning, and GitHub Advanced Security secret scanning
  - Uses matrix builds to build, test, and scan all 12 microservices in parallel
  - Generates SBOM for each microservice
  - Publishes images to GHCR when merged to main

### `/security` - Security Scanning

- **[security-scan.yml](security/security-scan.yml)**: Dedicated security scanning workflow that runs weekly
  - Performs extended security analysis including GitHub Advanced Security secret scanning
  - Scans IaC (Kubernetes manifests, Terraform, Dockerfiles) for misconfigurations
  - Generates comprehensive SBOMs for all microservices
  - Consolidates SBOMs for easier management

### `/release` - Release Management

- **[build-publish.yml](release/build-publish.yml)**: Triggered when a new tag is pushed or manually
  - Uses matrix builds to build and publish versioned Docker images for all 12 microservices
  - Scans images for vulnerabilities and misconfigurations
  - Generates and consolidates SBOMs for all microservices
  - Creates Kubernetes deployment manifests
  - Creates GitHub releases for tagged versions

### `/infrastructure` - Infrastructure Validation

- **[helm-chart-ci.yaml](infrastructure/helm-chart-ci.yaml)**: Validates Helm charts
- **[kubevious-manifests-ci.yaml](infrastructure/kubevious-manifests-ci.yaml)**: Validates Kubernetes manifests
- **[kustomize-build-ci.yaml](infrastructure/kustomize-build-ci.yaml)**: Validates Kustomize configurations
- **[terraform-validate-ci.yaml](infrastructure/terraform-validate-ci.yaml)**: Validates Terraform configurations

### `/archive` - Archived Workflows

Contains older workflow files that are kept for reference but are no longer actively used:

- **[ci-main.yaml](archive/ci-main.yaml)**: Older main branch CI workflow
- **[ci-pr.yaml](archive/ci-pr.yaml)**: Older PR-based CI workflow
- **[cleanup.yaml](archive/cleanup.yaml)**: Cleanup workflow for PR environments

## Helper Scripts

- **[install-dependencies.sh](install-dependencies.sh)**: Script to install dependencies needed for CI/CD workflows

## Infrastructure

The CI/CD pipelines for Online Boutique run in GitHub Actions. For every open Pull Request in the repo, the CI pipeline runs code tests, security scans, and builds container images.

## Notes for Contributors

- All new workflow files should be placed in the appropriate directory based on their purpose
- When creating new workflows, follow the naming convention of using `.yml` extension for consistency
- Reference the CI_CD_SETUP.md file in the repository root for detailed information about the CI/CD pipeline

## Appendix - Creating a new Actions runner

Should one of the two self-hosted Github Actions runners (GCE instances) fail, or you want to add more runner capacity, this is how to provision a new runner. Note that you need IAM access to the admin Online Boutique GCP project in order to do this.

1. Create a GCE instance.
    - VM should be at least n1-standard-4 with 50GB persistent disk
    - VM should use custom service account with permissions to: access a GKE cluster, create GCS storage buckets, and push to GCR.
2. SSH into new VM through the Google Cloud Console.
3. Install project-specific dependencies, including go, docker, skaffold, and kubectl:

```
wget -O - https://raw.githubusercontent.com/GoogleCloudPlatform/microservices-demo/main/.github/workflows/install-dependencies.sh | bash
```

The instance will restart when the script completes in order to finish the Docker install.

4. SSH back into the VM.

5. Follow the instructions to add a new runner on the [Actions Settings page](https://github.com/GoogleCloudPlatform/microservices-demo/settings/actions) to authenticate the new runner
6. Start GitHub Actions as a background service:
```
sudo ~/actions-runner/svc.sh install ; sudo ~/actions-runner/svc.sh start
```
