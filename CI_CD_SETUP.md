# CI/CD Pipeline for Online Boutique

This document describes the CI/CD pipeline setup for the Online Boutique microservices demo application.

## Overview

The CI/CD pipeline is implemented using GitHub Actions and includes:

1. **Code Quality & Security Scanning**
   - CodeQL for Static Application Security Testing (SAST)
   - Dependabot for Software Composition Analysis (SCA)
   - GitHub Advanced Security for secret scanning
   - TruffleHog for additional secret scanning
   - Linting and code quality checks

2. **Infrastructure as Code (IaC) Scanning**
   - Trivy for scanning Kubernetes manifests
   - Trivy for scanning Terraform configurations
   - Trivy for scanning Dockerfiles

3. **Build & Test**
   - Matrix build for all 12 microservices in parallel
   - Build Docker images for each microservice
   - Run unit tests for each microservice

4. **Security Scanning**
   - Trivy for container image vulnerability scanning
   - Software Bill of Materials (SBOM) generation for each microservice
   - Consolidated SBOM for the entire application

5. **Publish**
   - Push Docker images to GitHub Container Registry (GHCR)
   - Create Kubernetes deployment manifests
   - Create GitHub releases for tagged versions

## Workflow Files

The pipeline is organized into subdirectories in the `.github/workflows` folder for better maintainability:

### Continuous Integration

1. **[ci-pipeline.yml](.github/workflows/ci/ci-pipeline.yml)**
   - Main CI pipeline that runs on every push to main and pull requests
   - Coordinates linting, CodeQL analysis, IaC scanning, and GitHub Advanced Security secret scanning
   - Uses matrix builds to build, test, and scan all 12 microservices in parallel
   - Generates SBOM for each microservice
   - Publishes images to GHCR when merged to main

### Security Scanning

2. **[security-scan.yml](.github/workflows/security/security-scan.yml)**
   - Dedicated security scanning workflow that runs weekly
   - Performs extended security analysis including GitHub Advanced Security secret scanning
   - Scans IaC (Kubernetes manifests, Terraform, Dockerfiles) for misconfigurations
   - Generates comprehensive SBOMs for all microservices
   - Consolidates SBOMs for easier management

### Release Management

3. **[build-publish.yml](.github/workflows/release/build-publish.yml)**
   - Triggered when a new tag is pushed or manually
   - Uses matrix builds to build and publish versioned Docker images for all 12 microservices
   - Scans images for vulnerabilities and misconfigurations
   - Generates and consolidates SBOMs for all microservices
   - Creates Kubernetes deployment manifests
   - Creates GitHub releases for tagged versions

### Infrastructure Validation

4. **Infrastructure Validation Workflows**
   - **[helm-chart-ci.yaml](.github/workflows/infrastructure/helm-chart-ci.yaml)**: Validates Helm charts
   - **[kubevious-manifests-ci.yaml](.github/workflows/infrastructure/kubevious-manifests-ci.yaml)**: Validates Kubernetes manifests
   - **[kustomize-build-ci.yaml](.github/workflows/infrastructure/kustomize-build-ci.yaml)**: Validates Kustomize configurations
   - **[terraform-validate-ci.yaml](.github/workflows/infrastructure/terraform-validate-ci.yaml)**: Validates Terraform configurations

## Security Features

### 1. CodeQL Analysis

[CodeQL](https://codeql.github.com/) is GitHub's semantic code analysis engine that automatically identifies vulnerabilities and errors in your code.

- Analyzes code in multiple languages (Go, JavaScript, Python, Java, C#)
- Runs on every push to main and pull requests
- Extended analysis runs weekly with security-extended and security-and-quality queries

### 2. Dependabot

[Dependabot](https://github.com/dependabot) is configured to:

- Monitor dependencies in all 12 microservices
- Create pull requests for vulnerable dependencies
- Check for updates weekly

Configuration: [dependabot.yml](.github/dependabot.yml)

### 3. Trivy Scanner

[Trivy](https://github.com/aquasecurity/trivy) is used for comprehensive security scanning:

- **Container Image Scanning**:
  - Scans each microservice image for vulnerabilities
  - Blocks publishing if critical or high vulnerabilities are found
  - Results are uploaded to GitHub Security tab

- **IaC and Configuration Scanning**:
  - Scans Kubernetes manifests for misconfigurations
  - Scans Terraform configurations for security issues
  - Scans Dockerfiles for best practices and security issues
  - Results are uploaded to GitHub Security tab

### 4. Secret Scanning

- **GitHub Advanced Security** for automated secret scanning
  - Detects secrets, tokens, and credentials in the codebase
  - Prevents accidental commits of secrets
  - Alerts repository administrators of any detected secrets

- **TruffleHog** for additional secret scanning coverage
  - Runs weekly and on demand
  - Provides deeper scanning for secrets that might be missed

### 5. Software Bill of Materials (SBOM)

- **Syft** is used to generate SBOMs for each microservice
  - Creates SPDX-compliant SBOMs for each container image
  - Runs during both CI pipeline and release process
  - SBOMs are stored as artifacts for each build
  - Consolidated SBOMs are created for releases

## Container Registry

All Docker images are published to GitHub Container Registry (GHCR):

- Images are tagged with:
  - Commit SHA for every build on main
  - Semantic version tags (v1.0.0, v1.0, v1) for releases
  - 'latest' tag for the most recent build on main

- All 12 microservices are published:
  - frontend (Go)
  - cartservice (C#)
  - productcatalogservice (Go)
  - currencyservice (Node.js)
  - paymentservice (Node.js)
  - shippingservice (Go)
  - emailservice (Python)
  - checkoutservice (Go)
  - recommendationservice (Python)
  - adservice (Java)
  - loadgenerator (Python/Locust)
  - shoppingassistantservice (Python)

## How to Use

### Triggering the CI Pipeline

The CI pipeline runs automatically on:
- Every push to the main branch
- Every pull request to the main branch

### Creating a Release

To create a new release:

1. Tag the repository with a semantic version:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. The `build-publish.yml` workflow will:
   - Build and scan all microservice images
   - Push images to GHCR with appropriate version tags
   - Create Kubernetes deployment manifests
   - Create a GitHub release with the manifests attached

### Manual Workflow Trigger

You can also manually trigger the build and publish workflow:

1. Go to the "Actions" tab in your GitHub repository
2. Select the "Build and Publish" workflow
3. Click "Run workflow"
4. Enter a version tag (e.g., "v1.0.0" or "latest")
5. Click "Run workflow"

## Required Secrets

The following secrets need to be configured in your GitHub repository:

- `GITHUB_TOKEN` (automatically provided by GitHub Actions)

## Customization

To customize the CI/CD pipeline:

1. Modify the workflow files in the `.github/workflows/` directory
2. Update the Dependabot configuration in `.github/dependabot.yml`
3. Adjust the security scanning thresholds in the workflow files
4. Configure GitHub Advanced Security settings in the repository settings
5. Modify the Trivy configuration for IaC scanning
6. Adjust the SBOM generation format and output

## FAQ

### Does GitHub Advanced Security provide SBOM generation?

No, GitHub Advanced Security does not directly provide SBOM generation. In this pipeline, we use Anchore's Syft tool to generate SBOMs for each microservice. GitHub Advanced Security provides complementary security features like secret scanning, code scanning with CodeQL, and dependency review.

### How are all 12 microservices handled in the pipeline?

All 12 microservices are built, tested, and scanned in parallel using GitHub Actions matrix strategy. This approach:

- Improves pipeline efficiency by running jobs in parallel
- Ensures consistent treatment of all microservices
- Makes it easy to add or remove services from the pipeline
- Provides individual artifacts and scan results for each service
