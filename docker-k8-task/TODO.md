# Task list

1. Create GitHub Actions pipeline to check container images and push them to repository
    * build container images with correct tags
        * find services for build
        * 
    * scan with sec tools (Trivy, Checkov, Docker Scout)
    * scan manifests with sec tools in pipeline
    * push images to repository
2. Contenerise each app for minimal image
3. Create GitHub Actions pipeline for infrastructure with GitOps approach
4. Create infrastructure on Cloud:
    * K8 cluster
    * IAM
5. Enable K8 cluster to pull images from repository
6. Install K8 addons: HPA controller, Metrics server
7. Create manifests for application with Kustomize
8. Build Helm charts based on manifests
9. Add Redis to infrastructure and application
