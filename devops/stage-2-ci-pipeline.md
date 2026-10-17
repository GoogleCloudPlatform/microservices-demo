# =============================================================================
# Stage 2 – CI Pipeline: GitHub Actions
# Comprehensive documentation on the CI pipeline architecture and workflows
# =============================================================================

# Cấu Trúc & Hướng Dẫn CI Pipeline – GitHub Actions

## 1. Tổng Quan

Stage 2 xây dựng **CI Pipeline hoàn chỉnh** tự động hóa quá trình từ khi developer push code đến khi Docker image được đẩy lên Amazon ECR và manifest trong GitOps repo được cập nhật để ArgoCD sync xuống cluster.

### Luồng tổng thể

```
Developer Push Code
       │
       ▼
ci-main.yml (Orchestrator)
  │  Detect changed services (dorny/paths-filter)
  │
  ├──► build-adservice      ─┐
  ├──► build-cartservice     │ Chạy song song
  ├──► build-frontend        │ (matrix per service)
  ├──► build-checkoutservice ─┤
  └──► ...                   │
                              ▼
                     ci-service.yml (Reusable)
                       │
                       ├─ 1. Checkout code
                       ├─ 2. Setup language runtime + cache
                       ├─ 3. Install dependencies
                       ├─ 4. Unit tests
                       ├─ 5. Lint / format check
                       ├─ 6. Compute image tags (sha-xxxx, branch-xxx, latest)
                       ├─ 7. Auth to AWS via OIDC (no long-lived keys!)
                       ├─ 8. Docker build & push to ECR
                       └─ 9. Update image tag in online-boutique-config
                              (only on push to main)
```

## 2. Cấu Trúc Thư Mục

```
.github/
├── workflows/
│   ├── ci-main.yml            # Orchestrator: detect changes → trigger per-service builds
│   ├── ci-service.yml         # Reusable workflow cho mỗi service
│   ├── terraform-plan.yml     # Terraform plan khi PR thay đổi terraform-aws/
│   └── terraform-apply.yml    # Terraform apply khi merge vào main
└── actions/
    └── update-manifests/      # Composite action: update image tag trong config repo
        └── action.yml
```

## 3. Chi Tiết Từng Workflow

### 3.1 `ci-main.yml` – Orchestrator

**Trigger:**
- `push` vào `main`, `feature/**`, `fix/**`
- `pull_request` vào `main`
- Bỏ qua thay đổi trong `*.md`, `devops/`, `docs/`

**Hoạt động:**

| Job | Mô tả |
|-----|-------|
| `detect-changes` | Dùng `dorny/paths-filter@v3` để kiểm tra `src/<service>/**` có thay đổi không |
| `build-<service>` | Nếu service thay đổi → gọi `ci-service.yml` với input phù hợp |

**Điểm quan trọng:**
- Mỗi service được build **song song và độc lập** → nếu một service fail, service khác vẫn tiếp tục.
- Mỗi service được cấu hình đúng `language`, `dockerfile_path`, `context_path` (do `cartservice` có cấu trúc thư mục khác: `src/cartservice/src/Dockerfile`).

### 3.2 `ci-service.yml` – Reusable Per-Service Workflow

**Inputs:**

| Input | Mô tả |
|-------|-------|
| `service` | Tên service (e.g. `frontend`) |
| `language` | `go`, `dotnet`, `node`, `python`, `java` |
| `dockerfile_path` | Đường dẫn tới Dockerfile |
| `context_path` | Docker build context |
| `push_to_ecr` | Boolean – mặc định `true` |
| `update_manifests` | Boolean – mặc định `true` |

**Steps:**

| Bước | Công cụ | Mô tả |
|------|---------|-------|
| Setup language | `setup-go`, `setup-dotnet`, `setup-node`, `setup-python`, `setup-java` | Cài runtime đúng version, bật cache tự động |
| Unit Tests | `go test`, `dotnet test`, `npm test`, `pytest`, `gradle test` | Chạy tests theo ngôn ngữ |
| Lint | `golangci-lint`, `flake8`, `eslint` | Code quality check |
| Compute tags | Shell script | Tạo 3 tags: `sha-<short>`, `branch-<name>`, `latest` (chỉ trên main) |
| AWS Auth | `aws-actions/configure-aws-credentials@v4` (OIDC) | Không dùng access key – dùng GitHub OIDC |
| ECR Login | `aws-actions/amazon-ecr-login@v2` | Lấy token login Docker |
| Docker Build | `docker/build-push-action@v6` | Multi-stage build, cache vào ECR |
| Update manifests | `update-manifests` composite action | Cập nhật tag trong `online-boutique-config` |

### 3.3 `terraform-plan.yml` – Terraform PR Review

**Trigger:** Pull Request thay đổi `terraform-aws/**`

**Hoạt động:**
- Detect environment nào thay đổi (dev, staging, global/ecr, global/github-oidc)
- Chạy `terraform fmt -check`, `init`, `validate`, `plan`
- Post plan output dưới dạng comment lên PR (có collapse)
- Nếu plan đã tồn tại comment → update (không tạo mới)

### 3.4 `terraform-apply.yml` – Terraform Auto Apply

**Trigger:** Push vào `main` thay đổi `terraform-aws/**`

| Environment | Hành vi |
|-------------|---------|
| `dev` | Auto-apply (không cần approval) |
| `staging` | Requires manual approval (GitHub Environments protection rule) |
| `global/ecr` | Auto-apply |
| `global/github-oidc` | Auto-apply |

## 4. Tagging Strategy

| Tag | Ví dụ | Mục đích |
|-----|-------|----------|
| `sha-<7 chars>` | `sha-a3b4c5d` | Immutable – unique per commit, dùng trong ArgoCD |
| `branch-<name>` | `branch-main` | Mutable – tracking latest trên mỗi branch |
| `latest` | `latest` | Chỉ tag khi push vào `main` |

**ECR URI pattern:**
```
798836978890.dkr.ecr.ap-southeast-1.amazonaws.com/online-boutique/<service>:<tag>
```

## 5. AWS Authentication – OIDC (No Long-lived Keys)

Thay vì dùng `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`, pipeline dùng **GitHub OIDC** để assume IAM Role trực tiếp.

```
GitHub Actions Runner
    │
    │ Request OIDC token
    ▼
token.actions.githubusercontent.com
    │
    │ sts:AssumeRoleWithWebIdentity
    ▼
AWS IAM Role: online-boutique-github-ci
    (arn:aws:iam::798836978890:role/online-boutique-github-ci)
```

**IAM Role được cấu hình trong `terraform-aws/global/github-oidc/main.tf`:**
- Chỉ cho phép repo `online-boutique-application-demo/online-boutique-app` assume role
- Terraform role chỉ cho phép từ branch `main`
- Permissions: ECR push, EKS describe

**Không cần cấu hình secrets AWS trong GitHub!** Chỉ cần 1 secret:
- `CONFIG_REPO_TOKEN`: GitHub PAT hoặc GitHub App token có quyền write vào `online-boutique-config` repo (dùng để cập nhật image tag sau khi push ECR)

## 6. GitHub Environments & Secrets

### Environments cần tạo trên GitHub

| Environment | Protection Rules |
|-------------|-----------------|
| `dev` | Không cần approval |
| `staging` | Required reviewers (manual approval) |

### Secrets cần cấu hình

| Secret | Scope | Mục đích |
|--------|-------|---------|
| `CONFIG_REPO_TOKEN` | Repository | GitHub PAT/App token có quyền write vào `online-boutique-config` |

> **Không cần** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `ECR_TOKEN` – tất cả xử lý qua OIDC.

## 7. Services và Languages

| Service | Language | Test command | Dockerfile location |
|---------|----------|-------------|---------------------|
| `adservice` | Java (Gradle) | `gradle test` | `src/adservice/Dockerfile` |
| `cartservice` | C# (.NET 8) | `dotnet test` | `src/cartservice/src/Dockerfile` |
| `checkoutservice` | Go | `go test ./...` | `src/checkoutservice/Dockerfile` |
| `currencyservice` | Node.js | `npm test` | `src/currencyservice/Dockerfile` |
| `emailservice` | Python | `pytest` | `src/emailservice/Dockerfile` |
| `frontend` | Go | `go test ./...` | `src/frontend/Dockerfile` |
| `loadgenerator` | Python | `pytest` | `src/loadgenerator/Dockerfile` |
| `paymentservice` | Node.js | `npm test` | `src/paymentservice/Dockerfile` |
| `productcatalogservice` | Go | `go test ./...` | `src/productcatalogservice/Dockerfile` |
| `recommendationservice` | Python | `pytest` | `src/recommendationservice/Dockerfile` |
| `shippingservice` | Go | `go test ./...` | `src/shippingservice/Dockerfile` |

> **Lưu ý:** `shoppingassistantservice` **không được đưa vào CI pipeline** vì service này phụ thuộc hoàn toàn vào Google Cloud (Gemini AI qua `langchain-google-genai`, AlloyDB qua `google-cloud-alloydb-connector`, Secret Manager, Cloud Storage). Các Google Cloud APIs này không khả dụng trên AWS, nên service này sẽ không được build và deploy. Nếu sau này cần port sang AWS (thay Gemini bằng Amazon Bedrock, AlloyDB bằng RDS, v.v.), cần thêm ECR repo và build job tương ứng.

## 8. Docker Image Cache

Build cache được lưu trực tiếp vào ECR:
```
<registry>/<service>:buildcache
```

Cơ chế `cache-from` + `cache-to` của Buildx dùng cache layers từ lần build trước → giảm thời gian build đáng kể cho các layers không thay đổi (e.g. dependencies, base image).

## 9. Cập Nhật GitOps Manifests (Update Manifests Action)

Sau khi push image thành công lên ECR (chỉ trên branch `main`):

1. Checkout repo `online-boutique-config`
2. Dùng `yq` để update `newTag` trong `overlays/dev/kustomization.yaml`
3. Git commit + push với message `chore(cd): update <service> to sha-xxxxx`
4. ArgoCD detect drift → auto-sync vào cluster (Stage 3)

## 10. Bài Học Kinh Nghiệm

1. **Reusable workflows** (`workflow_call`): Giảm code duplication cực kỳ hiệu quả. Mỗi service chỉ cần thêm 10 dòng trong ci-main.yml, không cần copy workflow riêng.
2. **`dorny/paths-filter`**: Phát hiện thay đổi chính xác theo từng service path, tránh build lại toàn bộ 11 services khi chỉ 1 service thay đổi.
3. **OIDC thay access keys**: An toàn hơn nhiều, không bao giờ có long-lived credentials trong GitHub Secrets.
4. **Build cache vào ECR**: Dùng ECR làm registry cache cho Buildx (`cache-from`/`cache-to`) giúp tái dụng layers, giảm build time từ 5-10 phút xuống còn 1-2 phút cho subsequent builds.
5. **Immutable tag `sha-<commit>`**: Tag theo commit SHA đảm bảo traceability và reproducibility, ArgoCD có thể rollback về bất kỳ commit nào.
6. **PRs không push ECR**: CI trên PR chỉ chạy build để verify không có lỗi, không push lên ECR (tránh tốn storage và chi phí). Chỉ push khi merge vào `main`.
7. **Staging requires approval**: GitHub Environments với protection rules cho phép có approval gate trước khi apply Terraform vào staging.
