# GitHub Actions Workflows

Trang này mô tả các CI/CD workflows cho Online Boutique trên AWS, chạy trên [GitHub Actions](https://github.com/online-boutique-application-demo/online-boutique-app/actions).

## Infrastructure

Các CI/CD pipelines chạy trên **GitHub-hosted runners (Ubuntu)**. Authentication với AWS sử dụng **OIDC** (không dùng long-lived access keys).

## Workflows

### CI – Build & Push to ECR: [`ci-main.yml`](ci-main.yml)

**Trigger:** Push vào `main`, `feature/**`, `fix/**` hoặc PR vào `main`.

Orchestrator workflow phát hiện service nào thay đổi (dùng `dorny/paths-filter`) và gọi [`ci-service.yml`](ci-service.yml) cho từng service song song:

1. Setup language runtime (Go, .NET, Node.js, Python, Java)
2. Run unit tests
3. Lint / format check
4. Build Docker image (multi-stage, Buildx)
5. Push to Amazon ECR (tags: `sha-<commit>`, `branch-<name>`, `latest`)
6. Update image tag trong `online-boutique-config` repo (chỉ trên main)

**11 services** được build: tất cả trừ `shoppingassistantservice` (phụ thuộc Google Cloud APIs).

### Terraform Plan (PR): [`terraform-plan.yml`](terraform-plan.yml)

**Trigger:** PR thay đổi `terraform-aws/`.

1. Detect environment nào thay đổi (dev, staging, global/ecr, global/github-oidc)
2. Chạy `terraform fmt -check`, `init`, `validate`, `plan`
3. Post plan output dưới dạng comment lên PR

### Terraform Apply (main): [`terraform-apply.yml`](terraform-apply.yml)

**Trigger:** Push vào `main` thay đổi `terraform-aws/`.

1. Detect environment nào thay đổi
2. Chạy `terraform plan` rồi `terraform apply -auto-approve`
3. Dev: auto-apply, Staging: requires manual approval (GitHub Environments)
4. Hỗ trợ global ECR và global GitHub OIDC modules

## Composite Actions

### [`update-manifests`](../actions/update-manifests/action.yml)

Composite action cập nhật image tag trong GitOps repo (`online-boutique-config`):
- Checkout config repo
- Dùng `yq` để update `newTag` trong Kustomize overlays
- Git commit + push

## AWS Authentication

Tất cả workflows dùng **GitHub OIDC** để assume IAM roles:

| Role | Mục đích |
|------|----------|
| `online-boutique-github-ci` | CI: ECR push, EKS describe |
| `online-boutique-github-terraform` | Terraform: full infrastructure management |

Không cần cấu hình AWS access keys trong GitHub Secrets.
