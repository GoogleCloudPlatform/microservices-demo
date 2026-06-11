# Essentia Attire: E-Commerce Microservices Architecture on AWS EKS

## Project Overview

Essentia Attire is a dynamic, fully functional, and visually bespoke e-commerce platform built upon a polyglot microservices architecture. This project showcases the engineering of a modern, scalable, and automated cloud infrastructure using best practices in AWS, Kubernetes, and GitOps.

Originally based on the [Google Microservices Demo](https://github.com/GoogleCloudPlatform/microservices-demo), this platform has been significantly customized and engineered for native deployment on AWS, featuring:

* **11 polyglot microservices:** Written in Go, C#, Python, and Node.js, demonstrating polyglot interoperability.
* **AWS EKS & ECR:** Orchestrated on a high-availability Kubernetes cluster on AWS EKS, with private container images managed in AWS ECR.
* **Scalable S3 Assets:** Decoupled static imagery (branding logos, product pictures) for optimized delivery.
* **GitOps (ArgoCD):** Automated and consistent application delivery directly from Git.
* **CI/CD (GitHub Actions):** Seamless integration, image building, and deployment rollout triggered on code commit.

---

## Architecture

**[INSERT YOUR CUSTOM DRAW.IO DIAGRAM IMAGE HERE - USE THE ROUGH DIAGRAM DESCRIPTION BELOW AS YOUR BASE]**

The architecture consists of standard components:

1.  **Frontend (Custom Image):** Serves the bespoke website design and brand identity.
2.  **Product Catalog (Custom Image):** Manages product details and links to S3-hosted bespoke assets.
3.  **Other standard services:** Cart, Checkout, Currency, Payment, Shipping, Ad service, etc., demonstrating a complete polyglot e-commerce flow.

### AWS Infrastructure (Managed via AWS CLI/eksctl)

* **AWS EKS Cluster:** Master nodes + managed worker nodes (`t3.small` initially).
* **AWS ECR:** Private repositories for custom Frontend and Product Catalog images.
* **AWS S3:** Public bucket (`your-bucket-name`) hosting all product images and the brand logo.
* **AWS ELB (Classic LoadBalancer):** Physical entry point for public internet traffic, routing to the frontend service.

---

## CI/CD Pipeline & Automation

This project features a sophisticated CI/CD bridge using a nested monorepo structure:

### Continuous Integration (GitHub Actions)

**(/docs/img/github_actions_green_pipeline.png)[SCREENSHOT OF GREEN PIPELINE IN GITHUB ACTIONS]**

On push to `main` (specifically targeting `src/frontend/**` or `src/productcatalogservice/**` changes):
1.  **Code verification & Unit Tests (Go/C#):** Pipeline validates changes.
2.  **Authentication:** securely logs into AWS via stored GitHub Secrets.
3.  **Dynamic Build & Push:** Pipeline automatically builds new Docker images, tagging them with the unique Git commit SHA, and pushes to AWS ECR.
4.  **GitOps Manifest Update:** Pipeline dynamically updates the corresponding deployment YAML manifest in `kubernetes-manifests/` with the new image tag and *commits the update back to the Git repository* [skip ci].

### Continuous Deployment (GitOps with ArgoCD)

**(docs\img\argocd_dashboard.png)|(docs\img\argocd_dashboard1.png)|(docs\img\argocd_dashboard2.png)[ARGOCD DASHBOARD]**

* **Polling:** ArgoCD is configured to poll the specified Git repository for changes to Kubernetes manifests.
* **Synchronization:** Upon detecting the manifest commit from the CI pipeline, ArgoCD automatically and gracefully rolls out the updated pods to the EKS cluster, pulling the correct new image from ECR.

---

## Challenges Overcome & SRE Debugging

A major focus of this project was engineering through real-world infrastructure and application bottlenecks:

* **Critical EKS IP Exhaustion (ENI Limits):** Initially encountered `FailedScheduling` errors due to strict ENI IP address limitations on `t3.small` nodes in the ap-south-1 region. **Resolution:** Debugged ENI constraints, recalculated pod requirements, and programmatically scaled the worker node group (desired count, minimums, maximums) to overcome the limitation without service interruption.
* **Intermittent Shopping Cart Panic (Go):** Triaged intermittent "error loading" cart page. Identified silent failures (0 pod restarts) by setting up live log streaming for `frontend` and `cartservice`. Root cause was identified as a Go panic (`money.Must`) caused by strict JSON typing mismatches in custom product pricing (`currencyCode`, `units`, `nanos`) in the product catalog. **Resolution:** Restructured the JSON schema payload for custom products to match strict application code requirements.
* **Monorepo CI Optimization:** Resolved critical pathing issues in GitHub Actions where shared pipelines could not find Go dependency files (`go.mod`). **Resolution:** Explicitly defined a recursive `cache-dependency-path: 'src/**/go.sum'` for efficient module caching across the nested monorepo structure.
* **Git 403 Forbidden & Pipeline Self-Update:** Overcame a standard Git `403 Forbidden` error where the pipeline failed to commit manifest updates back to the repo. **Resolution:** Engineered the workflow with explicit `permissions: contents: write` and securely configured the GitHub Actions bot user.

---

## Customizations & Bespoke Branding

* **S3 Asset Integration:** Offloaded original Google assets. Integrated public object access and robust bucket policies for secure, scalable asset delivery (interlocking EA brand logo and all custom product imagery). **customize with specific examples if relevant**
* **Bespoke Frontend:** Customized the original Google design to inject the EA brand identity via header HTML modifications, ensuring seamless integration with the S3-hosted logo. **customize with specific examples**
* **Dynamic Product Catalog:** Overhauled the product catalog schema with custom product details (e.g., specific apparel descriptions, updated prices) and full integration with bespoke S3 URLs for each item. **customize with specific examples**

---
## Screenshots

| Home Page                                                                                                         | Checkout Screen                                                                                                    |
| ----------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| [![Screenshot of store homepage](/docs/img/essentia_webpage.png)](/docs/img/essentia_productpage.png) | [![Screenshot of checkout screen](/docs/img/essentia_cart_page.png)](/docs/img/essentia_cart_page1.png) |


## How to Deploy & Use

### Prerequisites

1.  AWS CLI & Configure credentials with suitable permissions (EKS, ECR, S3, IAM PowerUser recommended).
2.  Docker, Kubernetes Tools (`kubectl`, `eksctl` recommended).
3.  Access to a Git repository for this project.

### Step 1: Create AWS Infrastructure

* Create an EKS cluster (e.g., using `eksctl create cluster`).
* Create ECR repositories for your custom frontend and product catalog.
* Create an S3 bucket with public read access (carefully apply the required bucket policy found in the permissions section).

### Step 2: Build & Push Initial Images (Manual or via Pipeline)

* You can manually build and push initial images to ECR, or trigger the automatic pipeline by pushing changes to the `src/` folders. **[INSERT A LINK TO YOUR CI/CD LOGS OR A BASIC DOCKER BUILD EXAMPLE IF MANUAL BUILD IS AN OPTION]**

### Step 3: Deploy ArgoCD

* Install ArgoCD in your EKS cluster and set up an application pointing to your Git repository's `kubernetes-manifests/` folder. **<a href="https://argo-cd.readthedocs.io/en/stable/">[LINK TO ARGOCD DOCS]</a>**

### Step 4: Scale Nodes for full deployment

* To fully run all microservices, you will need to scale your initial nodes:
    ```bash
    eksctl scale nodegroup --cluster online-clothing --name clothing-workers --nodes 3 --nodes-min 2 --nodes-max 4
    ```

### Step 5: Access the Website

* Once fully synced and running, get the external IP of the frontend load balancer:
    ```bash
    kubectl get service frontend-external
    ```
* Access the provided LoadBalancer URL in your browser to see Essentia Attire live!

### To trigger automated updates

Simply make a code change (e.g., to HTML, CSS, or `products.json`), commit, and push to `main`. Watch the GitHub Actions pipeline and ArgoCD dashboard for fully automated integration and delivery.

---

[SKIP CI] - This project uses the `[skip ci]` commit message convention for automated commits to avoid recursive pipeline triggering.
