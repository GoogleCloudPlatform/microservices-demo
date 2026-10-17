# 🚀 Kế hoạch triển khai project DevOps – Online Boutique trên AWS

## Tổng Quan Dự Án

Triển khai ứng dụng **Google Online Boutique** (12 microservices) lên hạ tầng AWS với quy trình DevOps hoàn chỉnh end-to-end.

### Cấu trúc Repositories

```
online-boutique/
├── online-boutique-app/           # Source code + Infra (repo hiện tại)
│   ├── src/                       # 12 microservices
│   ├── terraform-aws/             # Terraform modules & environments
│   ├── devops/                    # 📝 Documentation theo từng stage
│   ├── .github/workflows/         # CI pipelines
│   └── ...
└── online-boutique-config/        # GitOps config (repo riêng)
    ├── apps/                      # ArgoCD Application definitions
    ├── base/                      # Base manifests
    ├── overlays/                  # Environment overlays (dev, staging)
    └── ...
```

### Kiến Trúc Microservices Hiện Tại

| Service | Ngôn ngữ | Port | Mô tả |
|---------|----------|------|--------|
| `frontend` | Go | 8080 | Web UI, gateway cho user |
| `cartservice` | C# (.NET) | 7070 | Quản lý giỏ hàng (Redis) |
| `productcatalogservice` | Go | 3550 | Danh mục sản phẩm |
| `currencyservice` | Node.js | 7000 | Chuyển đổi tiền tệ |
| `paymentservice` | Node.js | 50051 | Xử lý thanh toán |
| `shippingservice` | Go | 50051 | Tính phí vận chuyển |
| `emailservice` | Python | 8080 | Gửi email xác nhận |
| `checkoutservice` | Go | 5050 | Xử lý checkout |
| `recommendationservice` | Python | 8080 | Gợi ý sản phẩm |
| `adservice` | Java | 9555 | Quảng cáo |
| `loadgenerator` | Python | — | Tạo traffic giả lập |
| `shoppingassistantservice` | Python | 80 | Trợ lý mua sắm AI |

### Kiến Trúc Tổng Thể

```mermaid
graph TB
    subgraph "Developer"
        DEV[Developer Push Code]
    end

    subgraph "CI - GitHub Actions"
        LINT[Linting & Unit Tests]
        SCA[SCA - Dependency Scan]
        SAST[SAST - Code Analysis]
        BUILD[Docker Build & Push to ECR]
        SIGN[Image Signing - Cosign]
        SCAN[Container Image Scan - Trivy]
        UPDATE[Update K8s Manifests]
    end

    subgraph "CD - ArgoCD"
        ARGO[ArgoCD Sync]
        HELM[Helm Chart Deployment]
    end

    subgraph "AWS Infrastructure - Terraform"
        VPC[VPC & Networking]
        EKS["EKS Cluster (Spot, v1.36)"]
        ECR[ECR Repositories]
        REDIS[ElastiCache Redis]
        ALB[ALB Ingress]
    end

    subgraph "Service Mesh - Istio"
        GW[Istio Gateway]
        VS[Virtual Services]
        MTLS[mTLS]
        TRAFFIC[Traffic Management]
        KIALI[Kiali Dashboard]
    end

    subgraph "Monitoring & Observability"
        PROM[Prometheus]
        GRAF[Grafana]
        LOKI[Loki - Logs]
        TEMPO[Tempo - Traces]
        ALERT[Alertmanager]
    end

    subgraph "DAST"
        ZAP[OWASP ZAP Scan]
    end

    DEV --> LINT --> SCA --> SAST --> BUILD --> SIGN --> SCAN --> UPDATE
    UPDATE --> ARGO --> HELM
    HELM --> EKS
    EKS --> GW
    GW --> VS
    VS --> KIALI
    EKS --> PROM --> GRAF
    EKS --> LOKI
    EKS --> TEMPO
    ARGO --> ZAP
```

### Thư mục Documentation (`devops/`)

```
devops/
├── plan.md                        # Bản kế hoạch này
├── git-convention.md              # Quy ước Git commit
├── architecture.md                # Kiến trúc tổng thể
├── stage-1-terraform.md           # Viết sau khi hoàn thành Stage 1
├── stage-2-ci-pipeline.md         # Viết sau khi hoàn thành Stage 2
├── stage-3-cd-argocd.md           # Viết sau khi hoàn thành Stage 3
├── stage-4-service-mesh.md        # Viết sau khi hoàn thành Stage 4
├── stage-5-monitoring.md          # Viết sau khi hoàn thành Stage 5
├── stage-6-devsecops.md           # Viết sau khi hoàn thành Stage 6
├── stage-7-integration.md         # Viết sau khi hoàn thành Stage 7
└── runbooks/                      # Operational runbooks
    ├── deploy.md
    ├── rollback.md
    ├── troubleshooting.md
    └── scaling.md
```

> Mỗi tài liệu stage sẽ bao gồm: mô tả kiến trúc, quyết định thiết kế, hướng dẫn sử dụng, cấu hình chi tiết, và bài học kinh nghiệm.

---

## 📋 Các Stage Triển Khai

---

## Stage 1: Thiết Lập Nền Tảng Terraform – Hạ Tầng AWS

> **Mục tiêu:** Định nghĩa toàn bộ hạ tầng AWS bằng Terraform với cấu trúc module hóa.
> **Thời gian ước tính:** 3-4 ngày

### 1.1 Cấu trúc thư mục Terraform

```
terraform-aws/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── terraform.tfvars.example
│   │   └── outputs.tf
│   └── staging/
│       ├── main.tf
│       ├── variables.tf
│       ├── terraform.tfvars.example
│       └── outputs.tf
├── modules/
│   ├── vpc/                      # VPC, Subnets, NAT, IGW, Flow Logs
│   ├── eks/                      # EKS Cluster, Node Groups (Spot), Addons
│   ├── ecr/                      # ECR Repositories cho 11 services
│   ├── elasticache/              # Redis cho CartService (Multi-AZ)
│   └── irsa/                     # IAM Roles for Service Accounts
└── global/
    ├── s3-backend/               # Bootstrap S3 state backend
    ├── ecr/                      # ECR repos (shared across envs)
    └── github-oidc/              # GitHub Actions OIDC + IAM roles
```

### 1.2 Chi tiết tài nguyên AWS

| Tài nguyên | Cấu hình | Ghi chú |
|------------|----------|---------|
| **VPC** | 3 AZs, Public/Private/DB Subnets, NAT Gateway | High availability |
| **EKS** | **v1.36**, Managed Node Groups (**Spot** – t3.medium x3) | IRSA, KMS encryption, VPC CNI prefix delegation, **Spot để tiết kiệm chi phí** |
| **ECR** | 11 repositories (1/service) | Lifecycle policy, scan on push, managed globally |
| **ElastiCache** | Redis 7.x, Multi-AZ, Encryption at rest | Thay thế in-cluster Redis |
| **S3** | Terraform state bucket | Versioning + KMS encryption + S3 native locking |
| **IAM** | EKS cluster role, node role, IRSA roles, GitHub OIDC | Least privilege |
| **ALB** | AWS Load Balancer Controller (via IRSA) | Ingress cho Istio Gateway |

> [!IMPORTANT]
> **EKS v1.36** được chọn vì nằm trong Standard Support đến 08/2027 (v1.32 trở xuống đã vào Extended Support, tính phí ~6x).
> **Spot Instances** giúp tiết kiệm ~60-70% chi phí so với On-Demand.

### 1.3 Cấu hình Environment

| Tham số | Dev | Staging |
|---------|-----|---------|
| Node Instance Types | `t3.medium` | `t3.medium` |
| Capacity Type | **SPOT** | **SPOT** |
| Node Desired/Min/Max | 3 / 2 / 5 | 3 / 2 / 5 |
| NAT Gateway | Single (tiết kiệm) | Single |
| Redis Node Type | `cache.t3.micro` | `cache.t3.micro` |
| Redis Clusters | 2 (Multi-AZ) | 2 (Multi-AZ) |
| VPC Flow Logs | Enabled | Enabled |

### 1.4 Deliverables
- [ ] Module VPC với 3 tầng subnet (public, private, database)
- [ ] Module EKS v1.36 với Spot managed node groups, VPC CNI prefix delegation và pinned add-ons
- [ ] Module ECR với lifecycle policies (global root module)
- [ ] Module ElastiCache Redis (Multi-AZ)
- [ ] Module IRSA (AWS LB Controller, Cluster Autoscaler)
- [ ] Remote state backend (S3 + native locking)
- [ ] GitHub Actions OIDC provider + IAM roles
- [ ] VPC Flow Logs
- [ ] Environment configs cho dev và staging
- [ ] Outputs: cluster endpoint, ECR URIs, Redis endpoint, VPC ID
- [ ] 📝 Documentation: `devops/stage-1-terraform.md`

---

## Stage 2: CI Pipeline – GitHub Actions

> **Mục tiêu:** Xây dựng pipeline CI tự động hóa build, test và push images.
> **Thời gian ước tính:** 3-4 ngày

### 2.1 Cấu trúc thư mục CI

```
.github/
├── workflows/
│   ├── ci-main.yml               # Orchestrator workflow
│   ├── ci-service.yml            # Reusable workflow cho mỗi service
│   ├── terraform-plan.yml        # Terraform plan trên PR
│   ├── terraform-apply.yml       # Terraform apply khi merge
│   └── security-scan.yml         # Scheduled security scans
├── actions/
│   ├── docker-build-push/        # Composite action: build + push ECR
│   └── update-manifests/         # Composite action: update image tags
└── CODEOWNERS
```

### 2.2 CI Pipeline Flow

```mermaid
graph LR
    A[Push/PR] --> B{Detect Changed Services}
    B --> C[Service-specific CI]
    
    subgraph "Per Service CI"
        C --> D[Checkout Code]
        D --> E[Unit Tests]
        E --> F[Lint & Format Check]
        F --> G[Build Docker Image]
        G --> H[Push to ECR]
        H --> I["Update Image Tag in online-boutique-config"]
    end
```

### 2.3 Chi tiết Workflow

#### `ci-main.yml` – Orchestrator
- **Trigger:** Push to `main`, Pull Requests
- **Job 1 – Detect Changes:** Sử dụng `dorny/paths-filter` để phát hiện service nào thay đổi
- **Job 2 – Matrix Build:** Chạy `ci-service.yml` dạng matrix cho các service thay đổi

#### `ci-service.yml` – Reusable Per-Service Workflow
| Step | Tool | Mô tả |
|------|------|--------|
| Checkout | `actions/checkout@v4` | Clone code |
| Setup Language | `actions/setup-go`, `setup-node`, etc. | Cài đặt runtime |
| Cache Dependencies | `actions/cache` | Cache go modules, npm, pip |
| Unit Tests | `go test`, `dotnet test`, `npm test`, `pytest` | Run tests |
| Lint | `golangci-lint`, `eslint`, `pylint`, `checkstyle` | Code quality |
| Docker Build | `docker/build-push-action@v5` | Multi-platform build |
| Login ECR | `aws-actions/amazon-ecr-login` | Authenticate ECR |
| Push Image | Tag: `sha-<commit>`, `latest` | Push to ECR |
| Update Manifests | `yq` / custom script | Cập nhật image tag trong **online-boutique-config** repo |

#### `terraform-plan.yml`
- **Trigger:** PR thay đổi `terraform-aws/`
- Chạy `terraform fmt -check`, `terraform validate`, `terraform plan`
- Comment plan output vào PR

#### `terraform-apply.yml`
- **Trigger:** Merge vào `main` có thay đổi `terraform-aws/`
- Chạy `terraform apply -auto-approve`
- Chỉ chạy trên branch `main`

### 2.4 Deliverables
- [ ] Reusable workflow CI cho từng service với path filtering
- [ ] Docker build multi-stage tối ưu
- [ ] ECR push với proper tagging strategy (`sha-xxx`, `branch-name`, `latest`)
- [ ] Terraform plan/apply workflow
- [ ] GitHub Environments với approval gates cho staging
- [ ] Secrets management (AWS credentials, ECR, etc.)
- [ ] 📝 Documentation: `devops/stage-2-ci-pipeline.md`

---

## Stage 3: CD Pipeline – ArgoCD + GitOps

> **Mục tiêu:** Triển khai GitOps-based CD với ArgoCD, tách biệt hoàn toàn config khỏi source code.
> **Thời gian ước tính:** 2-3 ngày
> **Working directory:** `d:\online-boutique\online-boutique-config`

### 3.1 Cấu trúc GitOps Repository (`online-boutique-config`)

```
online-boutique-config/
├── argocd/                        # ArgoCD installation & config
│   ├── install/
│   │   └── values.yaml            # ArgoCD Helm values
│   └── apps/
│       ├── dev/
│       │   ├── online-boutique.yaml    # ArgoCD App: 11 microservices (dev)
│       │   ├── aws-lb-controller.yaml  # ArgoCD App: AWS LB Controller Helm
│       │   └── cluster-autoscaler.yaml # ArgoCD App: Cluster Autoscaler Helm
│       └── staging/
│           └── online-boutique.yaml    # ArgoCD App: 11 microservices (staging)
├── base/                          # Base Kustomize manifests
│   └── online-boutique/
│       ├── kustomization.yaml
│       ├── namespace.yaml
│       └── *.yaml                 # 11 services (từ kubernetes-manifests/ gốc, đã dọn dẹp)
├── overlays/                      # Environment-specific overlays
│   ├── dev/
│   │   ├── kustomization.yaml     # images newTag (CI update qua yq)
│   │   └── patches/
│   │       └── cartservice-redis.yaml  # Patch REDIS_ADDR → ElastiCache
│   └── staging/
│       ├── kustomization.yaml
│       └── patches/
│           └── cartservice-redis.yaml
└── README.md
```

### 3.2 ArgoCD Setup

| Component | Chi tiết |
|-----------|---------|
| **Installation** | Helm chart, namespace `argocd` |
| **Pattern** | Application per environment (không cần App of Apps cho MVP) |
| **Sync Policy** | **Auto-sync cho dev**, **Manual sync cho staging** |
| **Notifications** | Slack/Discord integration |
| **RBAC** | SSO via GitHub OAuth, role-based access |

> [!IMPORTANT]
> **ArgoCD Image Updater đã bị loại bỏ.** Stage 2 đã triển khai cơ chế CI push-based: composite action `update-manifests` dùng `yq` commit tag `sha-xxx` vào `overlays/dev/kustomization.yaml`. Nếu bật cả Image Updater sẽ gây xung đột Git commit (race condition). CI push-based đơn giản hơn, không tốn tài nguyên pod trên EKS, và đảm bảo immutable tag traceability.

### 3.3 Dọn dẹp Manifests

Khi tạo `base/online-boutique/` từ `kubernetes-manifests/` gốc, cần điều chỉnh:

| Hạng mục | Hành động | Lý do |
|----------|-----------|-------|
| `redis-cart` Deployment + Service | **Xóa** khỏi `cartservice.yaml` | Dùng AWS ElastiCache, không dùng in-cluster Redis |
| `shoppingassistantservice` | **Không tạo** manifest | Phụ thuộc Google Cloud APIs (Gemini, AlloyDB) |
| `cartservice` env `REDIS_ADDR` | **Patch** ở overlay: `redis-cart:6379` → ElastiCache endpoint | Lấy từ `terraform output redis_connection_string` |
| Image names | **Map** qua Kustomize `images` section | `image: frontend` → ECR URI |

### 3.4 Infrastructure Components (ArgoCD-managed)

Stage 1 đã tạo IRSA roles nhưng chưa cài Helm chart. Stage 3 cài qua ArgoCD Applications:

| Component | Helm Chart | Namespace | IRSA Role |
|-----------|-----------|-----------|-----------|
| **AWS LB Controller** | `aws/aws-load-balancer-controller` | `kube-system` | `aws_lb_controller_role_arn` |
| **Cluster Autoscaler** | `autoscaler/cluster-autoscaler` | `kube-system` | `cluster_autoscaler_role_arn` |

> Cài ở Stage 3 để chuẩn bị sẵn cho AWS ALB Ingress ở Stage 4.

### 3.5 Deployment Strategy

```mermaid
graph TD
    A[CI Updates Image Tag] --> B["online-boutique-config Updated"]
    B --> C[ArgoCD Detects Drift]
    C --> D{Environment?}
    D -->|Dev| E[Auto Sync]
    D -->|Staging| F[Manual Approval + Sync]
    E --> G[Health Check]
    F --> G
```

### 3.6 Deliverables
- [ ] ArgoCD installation via Helm trên EKS
- [ ] ArgoCD Applications cho dev và staging (online-boutique)
- [ ] Kustomize base manifests (11 services, không redis-cart, không shoppingassistantservice)
- [ ] Kustomize overlays cho dev/staging (với ElastiCache Redis patch)
- [ ] AWS LB Controller + Cluster Autoscaler cài qua ArgoCD Helm Applications
- [ ] Sync policies (auto cho dev, manual cho staging)
- [ ] Rollback strategy documentation
- [ ] 📝 Documentation: `devops/stage-3-cd-argocd.md`

---

## Stage 4: Service Mesh – Istio + Kiali

> **Mục tiêu:** Cài đặt và cấu hình Istio cho traffic management, security (mTLS), observability và **Kiali** dashboard.
> **Thời gian ước tính:** 2-3 ngày

### 4.1 Istio + Kiali Installation

| Component | Chi tiết |
|-----------|---------|
| **Istio Installation** | `istioctl` hoặc Istio Operator, profile: `default` |
| **Namespace** | `istio-system` |
| **Ingress Gateway** | Tích hợp AWS ALB |
| **Sidecar Injection** | Label namespace: `istio-injection=enabled` |
| **Kiali** | Helm chart, namespace `istio-system`, tích hợp Prometheus + Grafana |

### 4.2 Cấu hình Chi tiết

```
istio/
├── installation/
│   ├── istio-operator.yaml        # IstioOperator CR
│   └── namespace.yaml
├── gateway/
│   ├── gateway.yaml               # Istio Gateway + AWS ALB annotations
│   └── virtual-services.yaml      # VirtualService cho frontend
├── security/
│   ├── peer-authentication.yaml   # STRICT mTLS
│   ├── authorization-policies.yaml # Service-to-service access control
│   └── request-authentication.yaml
├── traffic/
│   ├── destination-rules.yaml     # Load balancing, circuit breaker
│   ├── retry-policies.yaml        # Retry configuration
│   └── timeout-policies.yaml      # Timeout configuration
├── kiali/
│   └── values.yaml                # Kiali Helm values
└── observability/
    ├── telemetry.yaml             # Metrics, traces export config
    └── envoy-filter.yaml          # Custom Envoy filters (nếu cần)
```

### 4.3 Tính năng triển khai

| Tính năng | Cấu hình |
|-----------|----------|
| **mTLS** | `PeerAuthentication` mode: `STRICT` cho toàn mesh |
| **Traffic Management** | Canary deployment via `VirtualService` weight-based routing |
| **Circuit Breaker** | `DestinationRule` với outlier detection |
| **Rate Limiting** | `EnvoyFilter` hoặc Istio `RequestAuthentication` |
| **Access Control** | `AuthorizationPolicy` - whitelist service-to-service communication |
| **Observability** | Tự động export metrics/traces qua Envoy sidecar |
| **Kiali Dashboard** | Visualization service mesh topology, traffic flow, health status |

### 4.4 Kiali Dashboard Features

| Feature | Mô tả |
|---------|--------|
| **Graph** | Service mesh topology visualization, traffic animation |
| **Workloads** | Xem trạng thái pods, deployments, Istio configs |
| **Services** | Service details, inbound/outbound traffic |
| **Istio Config** | Validate VirtualServices, DestinationRules, Policies |
| **Health** | Health check dashboard cho toàn bộ mesh |

### 4.5 Deliverables
- [ ] Istio installation manifest (IstioOperator)
- [ ] Gateway + VirtualService cho frontend
- [ ] mTLS strict mode cho toàn namespace
- [ ] Authorization policies (least privilege service-to-service)
- [ ] DestinationRules với circuit breaking
- [ ] Traffic management configs (canary routing weights)
- [ ] **Kiali dashboard** cài đặt và cấu hình
- [ ] Kiali tích hợp với Prometheus, Grafana, Tempo
- [ ] 📝 Documentation: `devops/stage-4-service-mesh.md`

---

## Stage 5: Monitoring & Observability

> **Mục tiêu:** Thiết lập hệ thống monitoring toàn diện với 3 trụ cột: Metrics, Logs, Traces.
> **Thời gian ước tính:** 3-4 ngày

### 5.1 Stack Công nghệ

```mermaid
graph TB
    subgraph "Metrics"
        PROM[Prometheus] --> GRAF_M[Grafana Dashboards]
        PROM --> ALERT[Alertmanager]
    end

    subgraph "Logs"
        PROMTAIL[Promtail/Alloy] --> LOKI[Loki]
        LOKI --> GRAF_L[Grafana - Explore]
    end

    subgraph "Traces"
        OTEL[OpenTelemetry Collector] --> TEMPO[Tempo]
        TEMPO --> GRAF_T[Grafana - Traces]
    end

    subgraph "Service Mesh"
        PROM --> KIALI_M[Kiali]
    end

    subgraph "Alerting"
        ALERT --> SLACK[Slack/PagerDuty]
    end
```

### 5.2 Cấu trúc thư mục

```
monitoring/
├── kube-prometheus-stack/
│   ├── values.yaml                # Prometheus + Grafana + Alertmanager
│   └── custom-rules/
│       ├── online-boutique-alerts.yaml
│       └── sla-recording-rules.yaml
├── loki-stack/
│   ├── values.yaml                # Loki + Promtail
│   └── loki-config.yaml
├── tempo/
│   └── values.yaml
├── grafana-dashboards/
│   ├── microservices-overview.json
│   ├── istio-mesh.json
│   ├── node-exporter.json
│   ├── pod-resources.json
│   └── business-metrics.json
└── opentelemetry/
    └── otel-collector.yaml
```

### 5.3 Chi tiết từng component

| Component | Tool | Mục đích |
|-----------|------|----------|
| **Metrics** | Prometheus (kube-prometheus-stack) | Thu thập metrics từ pods, nodes, Istio |
| **Visualization** | Grafana | Dashboards cho infrastructure, app, Istio mesh |
| **Logging** | Loki + Promtail/Grafana Alloy | Centralized logging, LogQL queries |
| **Tracing** | Tempo + OpenTelemetry Collector | Distributed tracing across microservices |
| **Alerting** | Alertmanager | Alert routing (Slack, PagerDuty, Email) |
| **Mesh Viz** | Kiali (từ Stage 4) | Service mesh topology + health |

### 5.4 Alert Rules

| Alert | Condition | Severity |
|-------|-----------|----------|
| `HighErrorRate` | Error rate > 5% trong 5 phút | Critical |
| `HighLatency` | P99 latency > 2s trong 5 phút | Warning |
| `PodCrashLooping` | Pod restart > 3 lần trong 15 phút | Critical |
| `HighMemoryUsage` | Memory > 85% limit | Warning |
| `HighCPUUsage` | CPU > 80% limit | Warning |
| `ServiceDown` | Service không available > 1 phút | Critical |
| `CertificateExpiringSoon` | TLS cert hết hạn < 7 ngày | Warning |
| `IstioSidecarInjectionFailed` | Sidecar injection failure | Critical |
| `SpotInstanceInterruption` | Spot instance sắp bị thu hồi | Warning |

### 5.5 Deliverables
- [ ] kube-prometheus-stack Helm values (Prometheus + Grafana + Alertmanager)
- [ ] Loki + Promtail/Alloy cài đặt và cấu hình
- [ ] Tempo cho distributed tracing
- [ ] OpenTelemetry Collector config
- [ ] Grafana dashboards custom cho Online Boutique
- [ ] Istio mesh dashboard
- [ ] Alert rules + notification channels (bao gồm Spot interruption)
- [ ] ServiceMonitor/PodMonitor CRDs cho từng service
- [ ] 📝 Documentation: `devops/stage-5-monitoring.md`

---

## Stage 6: DevSecOps – Security Scanning Pipeline

> **Mục tiêu:** Tích hợp bảo mật vào toàn bộ CI/CD pipeline (Shift-Left Security).
> **Thời gian ước tính:** 3-4 ngày

### 6.1 Security Scanning Overview

```mermaid
graph LR
    subgraph "Pre-Commit"
        A[gitleaks - Secret Scan]
    end

    subgraph "CI Pipeline - SCA"
        B[Trivy FS Scan]
        C[Dependabot]
    end

    subgraph "CI Pipeline - SAST"
        D[SonarQube]
    end

    subgraph "CI Pipeline - Container"
        F[Trivy Image Scan]
        G[Cosign Image Signing]
        H[Dockerfile Lint - hadolint]
    end

    subgraph "Post-Deploy - DAST"
        I[OWASP ZAP]
    end

    subgraph "Runtime"
        K[Kyverno - Policy Engine]
    end

    A --> B --> D --> F --> G
    C --> D
    G --> I
    F --> H
```

### 6.2 Chi tiết từng loại scan

#### 🔍 SCA – Software Composition Analysis
> Quét lỗ hổng trong dependencies/thư viện bên thứ 3

| Tool | Áp dụng cho | Tích hợp |
|------|------------|----------|
| **Trivy** (filesystem mode) | Tất cả services | GitHub Actions step |
| **Dependabot** | Go modules, npm, pip, NuGet, Gradle | GitHub native, auto-create PRs |

**Workflow:**
```yaml
# Trong ci-service.yml
- name: SCA - Trivy Filesystem Scan
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    scan-ref: './src/${{ matrix.service }}'
    format: 'sarif'
    output: 'trivy-sca-results.sarif'
    severity: 'CRITICAL,HIGH'

- name: Upload SCA Results
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: 'trivy-sca-results.sarif'
```

#### 🔬 SAST – Static Application Security Testing
> Phân tích mã nguồn tìm lỗ hổng bảo mật

| Tool | Ngôn ngữ hỗ trợ | Tích hợp |
|------|-----------------|----------|
| **SonarQube** | Go, Python, Java, C#, JS/TS | GitHub Actions, SonarQube Scanner |

> [!NOTE]
> SonarQube thay thế Semgrep + CodeQL, cung cấp cả SAST, code quality, code coverage trong một nền tảng duy nhất.
> Sử dụng SonarCloud (free cho public repos) hoặc self-host trên EKS.

**Workflow:**
```yaml
- name: SAST - SonarQube Scan
  uses: SonarSource/sonarqube-scan-action@v5
  env:
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
    SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}
```

#### 🐳 Container Security
> Quét Docker images trước khi deploy

| Tool | Mục đích | Tích hợp |
|------|----------|----------|
| **Trivy** (image mode) | Quét CVEs trong container images | GitHub Actions |
| **Hadolint** | Lint Dockerfile best practices | GitHub Actions |
| **Cosign** | Sign & verify container images | GitHub Actions + Kyverno policy |
| **ECR Scan** | AWS native image scanning | Tự động khi push |

#### 🌐 DAST – Dynamic Application Security Testing
> Quét ứng dụng đang chạy tìm lỗ hổng runtime

| Tool | Mục đích | Tích hợp |
|------|----------|----------|
| **OWASP ZAP** | Full scan, API scan, baseline scan | GitHub Actions (sau deploy staging) |

**Workflow:**
```yaml
# Chạy sau khi deploy staging thành công
- name: DAST - OWASP ZAP Baseline Scan
  uses: zaproxy/action-baseline@v0.12.0
  with:
    target: 'https://staging.online-boutique.example.com'
    rules_file_name: 'zap-rules.tsv'
    fail_action: 'warn'

- name: DAST - OWASP ZAP Full Scan
  uses: zaproxy/action-full-scan@v0.10.0
  with:
    target: 'https://staging.online-boutique.example.com'
```

#### 🛡️ Runtime Security & Policy Enforcement

| Tool | Mục đích |
|------|----------|
| **Kyverno** | Kubernetes policy engine (chặn privileged pods, enforce labels, require signed images, etc.) |

### 6.3 Security Gates

```mermaid
graph TD
    A[Code Push] --> B{Secret Scan}
    B -->|Pass| C{SCA Scan}
    B -->|Fail - Secrets Found| X[❌ Block Pipeline]
    C -->|No CRITICAL| D{SAST Scan}
    C -->|CRITICAL CVE| X
    D -->|No HIGH/CRITICAL| E[Build Image]
    D -->|HIGH/CRITICAL Finding| X
    E --> F{Image Scan}
    F -->|No CRITICAL| G[Sign Image]
    F -->|CRITICAL CVE| X
    G --> H[Deploy to Dev]
    H --> I[Promote to Staging]
    I --> J{DAST Scan}
    J -->|Pass| K[✅ Staging Verified]
    J -->|HIGH Risk| L[⚠️ Review Required]
```

### 6.4 Deliverables
- [ ] Trivy filesystem scan (SCA) tích hợp trong CI
- [ ] Dependabot config cho tất cả services
- [ ] SonarQube SAST scan tích hợp vào CI pipeline
- [ ] Trivy image scan sau Docker build
- [ ] Hadolint Dockerfile linting
- [ ] Cosign image signing
- [ ] OWASP ZAP baseline + full scan workflow (chạy trên staging)
- [ ] Kyverno policies (enforce security contexts, image signing, etc.)
- [ ] Security scan results upload to GitHub Security tab (SARIF)
- [ ] `zap-rules.tsv` tuning file
- [ ] 📝 Documentation: `devops/stage-6-devsecops.md`

---

## Stage 7: Tích Hợp, Kiểm Thử & Tài Liệu

> **Mục tiêu:** Tích hợp toàn bộ components, end-to-end testing, và hoàn thiện documentation.
> **Thời gian ước tính:** 2-3 ngày

### 7.1 End-to-End Testing
- [ ] Triển khai toàn bộ pipeline: commit → CI → CD → deploy lên dev
- [ ] Promote từ dev → staging qua ArgoCD
- [ ] Verify Istio mTLS hoạt động giữa các services
- [ ] Verify Kiali hiển thị service mesh topology chính xác
- [ ] Verify monitoring dashboards hiển thị đúng metrics
- [ ] Verify alerts gửi đúng notification channels
- [ ] Verify security scans chạy và report kết quả
- [ ] Test rollback scenario qua ArgoCD
- [ ] Load test với loadgenerator, kiểm tra Spot instance behavior
- [ ] Test Spot instance interruption handling

### 7.2 Documentation Tổng Kết
- [ ] Tổng hợp và review tài liệu từ Stage 1-6
- [ ] Architecture diagram tổng thể (đã bao gồm ở trên)
- [ ] README.md cho từng thư mục (infra, monitoring, security)
- [ ] Runbooks cho common operations:
  - `devops/runbooks/deploy.md` – Quy trình deploy
  - `devops/runbooks/rollback.md` – Quy trình rollback
  - `devops/runbooks/troubleshooting.md` – Xử lý sự cố
  - `devops/runbooks/scaling.md` – Hướng dẫn scaling
- [ ] 📝 Documentation: `devops/stage-7-integration.md`

### 7.3 Deliverables
- [ ] Toàn bộ pipeline hoạt động end-to-end (dev + staging)
- [ ] Documentation hoàn chỉnh trong `devops/`
- [ ] Runbooks
- [ ] Kiểm chứng Spot instance behavior

---

## 📊 Tổng Hợp Timeline

| Stage | Nội dung | Thời gian | Dependencies |
|-------|----------|-----------|-------------|
| **1** | Terraform – Hạ tầng AWS (EKS Spot v1.36) | 3-4 ngày | Không |
| **2** | CI – GitHub Actions | 3-4 ngày | Stage 1 (cần ECR URIs) |
| **3** | CD – ArgoCD + GitOps (online-boutique-config) | 2-3 ngày | Stage 1 (cần EKS) |
| **4** | Service Mesh – Istio + Kiali | 2-3 ngày | Stage 1 (cần EKS) |
| **5** | Monitoring & Observability | 3-4 ngày | Stage 1, 4 |
| **6** | DevSecOps – Security Scans | 3-4 ngày | Stage 2 (tích hợp vào CI) |
| **7** | Tích hợp & Tài liệu | 2-3 ngày | Tất cả stages |

> **Tổng thời gian ước tính: 18-25 ngày làm việc**

### Dependency Graph

```mermaid
graph LR
    S1["Stage 1: Terraform\n(EKS Spot v1.36)"] --> S2[Stage 2: CI/GitHub Actions]
    S1 --> S3["Stage 3: ArgoCD\n(online-boutique-config)"]
    S1 --> S4["Stage 4: Istio + Kiali"]
    S4 --> S5[Stage 5: Monitoring]
    S2 --> S6[Stage 6: DevSecOps]
    S1 --> S5
    S2 --> S3
    S3 --> S7[Stage 7: Integration]
    S4 --> S7
    S5 --> S7
    S6 --> S7
```

> [!NOTE]
> **Stages 2, 3, 4** có thể triển khai **song song** sau khi Stage 1 hoàn thành.
> **Stage 6** có thể bắt đầu song song với Stage 3 vì phần lớn tích hợp vào CI (Stage 2).
> **Sau mỗi stage**, viết tài liệu vào `devops/stage-X-*.md` trước khi chuyển sang stage tiếp theo.

---

## 🔧 Yêu Cầu Trước Khi Bắt Đầu

### AWS Account
- [ ] AWS Account với quyền admin hoặc sufficient IAM permissions
- [ ] AWS CLI configured
- [ ] Budget alert đã thiết lập (ước tính chi phí dev+staging Spot: ~$120-180/tháng)

### GitHub
- [ ] GitHub repository cho source code: `online-boutique-app`
- [ ] GitHub repository cho GitOps config: **`online-boutique-config`** ✅ (đã tạo)
- [ ] GitHub Actions enabled
- [ ] GitHub Secrets configured (AWS credentials)

### Tools Cục Bộ
- [ ] Terraform >= 1.5
- [ ] kubectl
- [ ] Helm >= 3.x
- [ ] AWS CLI v2
- [ ] Docker
- [ ] istioctl
