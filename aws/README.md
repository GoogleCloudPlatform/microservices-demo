# AWS Deployment — Online Boutique (ECS + EC2)

This directory contains the ECS task definitions for deploying the Online
Boutique microservices to Amazon ECS with **EC2 launch type**.

## Workflows

| Workflow | File | Trigger |
| --- | --- | --- |
| Sync development into derived branches | `.github/workflows/sync-branches.yaml` | PR merged into `development` |
| Deploy to AWS ECS (Production) | `.github/workflows/deploy-aws-prod.yaml` | PR from `development` merged into `main` |

## Architecture

- **Container registry:** Amazon ECR — one repository per service under a
  shared prefix (e.g. `<account>.dkr.ecr.<region>.amazonaws.com/boutique/<service>`).
- **Cluster:** Amazon ECS with EC2 launch type (e.g. an Auto Scaling Group of
  `t3.medium` instances registered as a container instance capacity provider).
- **Networking:** `networkMode: bridge` — each task maps container ports to
  host ports on the EC2 instance. An **Application Load Balancer** fronts the
  `frontend` service (port 8080) and routes traffic to the EC2 instances.
- **Service discovery:** backend services reference each other by name
  (e.g. `productcatalogservice:3550`). For these hostnames to resolve inside
  ECS, configure **AWS Cloud Map (ECS Service Discovery)** with DNS records
  matching each service name, or use a shared ALB with path-based routing.
- **Redis:** deployed as an ECS task using the public `redis:alpine` image.
  For production, consider replacing this with Amazon ElastiCache.

## Task Definitions

Located in `aws/ecs-task-definitions/`. Each file is a JSON task definition
template with `IMAGE_PLACEHOLDER` as the container image. The deploy workflow
uses `aws-actions/amazon-ecs-render-task-definition` to replace the placeholder
with the actual ECR image URI at deploy time.

| File | Service | Port | CPU | Memory |
| --- | --- | --- | --- | --- |
| `redis-cart.json` | redis-cart | 6379 | 256 | 512 |
| `emailservice.json` | emailservice | 8080 | 256 | 512 |
| `productcatalogservice.json` | productcatalogservice | 3550 | 256 | 512 |
| `currencyservice.json` | currencyservice | 7000 | 256 | 512 |
| `paymentservice.json` | paymentservice | 50051 | 256 | 512 |
| `shippingservice.json` | shippingservice | 50051 | 256 | 512 |
| `recommendationservice.json` | recommendationservice | 8080 | 256 | 512 |
| `cartservice.json` | cartservice | 7070 | 512 | 1024 |
| `adservice.json` | adservice | 9555 | 256 | 512 |
| `checkoutservice.json` | checkoutservice | 5050 | 256 | 512 |
| `frontend.json` | frontend | 8080 | 512 | 1024 |
| `loadgenerator.json` | loadgenerator | — | 256 | 512 |
| `shoppingassistantservice.json` | shoppingassistantservice | 8080 | 256 | 512 |

> **Note:** The `executionRoleArn` in each task definition contains the
> placeholder `AWS_ACCOUNT_ID`. Replace it with your actual AWS account ID,
> or let the deploy workflow override it. The default role
> `ecsTaskExecutionRole` needs `ecr:GetDownloadUrlForLayer`,
> `ecr:BatchGetImage`, `ecr:GetAuthorizationToken`, and
> `ecr:BatchCheckLayerAvailability` permissions.

## Required GitHub Configuration

### Secrets (Repository → Settings → Secrets and variables → Actions → Secrets)

| Secret | Description | Required for |
| --- | --- | --- |
| `AWS_ROLE_ARN` | IAM role ARN to assume via OIDC | OIDC auth (recommended) |
| `AWS_ACCESS_KEY_ID` | Access key ID | Alternative to OIDC |
| `AWS_SECRET_ACCESS_KEY` | Secret access key | Alternative to OIDC |

> **Choose one auth method.** OIDC is recommended. To use it:
> 1. Create an OIDC identity provider in IAM for `https://token.actions.githubusercontent.com`.
> 2. Create an IAM role with a trust policy allowing `sts:AssumeRoleWithWebIdentity`
>    for your GitHub repo/branch.
> 3. Attach a policy with ECR, ECS, and CloudWatch permissions.
> 4. Set `AWS_ROLE_ARN` to the role ARN.
>
> If you prefer access keys, set `AWS_ACCESS_KEY_ID` and
> `AWS_SECRET_ACCESS_KEY`, and edit `deploy-aws-prod.yaml` to use
> `aws-access-key-id` / `aws-secret-access-key` instead of `role-to-assume`.

### Variables (Repository → Settings → Secrets and variables → Actions → Variables)

| Variable | Example | Description |
| --- | --- | --- |
| `AWS_REGION` | `us-east-1` | AWS region for ECR/ECS |
| `AWS_ACCOUNT_ID` | `123456789012` | 12-digit AWS account ID |
| `ECR_REPO_PREFIX` | `boutique` | ECR repository prefix (repos created as `boutique/<service>`) |
| `ECS_CLUSTER_NAME` | `boutique-cluster` | Name of the pre-existing ECS cluster |
| `FRONTEND_URL` | `http://boutique-alb-123.us-east-1.elb.amazonaws.com` | ALB URL for smoke test |

> Until these secrets and variables are configured, the deploy workflow will
> fail cleanly at the `configure-aws-credentials` step. This is expected.

## AWS Infrastructure Prerequisites

Before the first deploy, the following must exist in your AWS account:

1. **ECS cluster** with EC2 capacity:
   - Create a cluster (e.g. `boutique-cluster`).
   - Register an Auto Scaling Group of EC2 instances (e.g. `t3.medium`) with
     the ECS-optimized AMI and an IAM instance profile that has
     `ecs:RegisterContainerInstance` and `ec2:DescribeInstances` permissions.
   - Attach a capacity provider to the cluster.

2. **ECR repositories** — one per service. The workflow auto-creates them if
   they don't exist, but the IAM role needs `ecr:CreateRepository` permission.

3. **ECS services** — one per service, each referencing the corresponding
   task definition family (`boutique-<service>`). The deploy workflow updates
   these services with new task definition revisions.

4. **Application Load Balancer** for the `frontend` service:
   - ALB with a listener on port 80.
   - Target group pointing to port 8080 on the EC2 instances.
   - The `frontend` ECS service should register tasks with this target group.

5. **Cloud Map service discovery** (for inter-service gRPC calls):
   - Create a private DNS namespace (e.g. `boutique.local`).
   - Create a service for each backend service with a DNS A record.
   - Configure each ECS service to use the corresponding Cloud Map service.
   - The DNS names must match the hostnames used in the environment variables
     (e.g. `productcatalogservice`, `currencyservice`, etc.).

6. **Security groups**:
   - ALB security group: allow inbound 80 from 0.0.0.0/0, outbound to
     instance SG on 8080.
   - Instance security group: allow inbound 8080 from ALB SG, allow all
     inbound between instances (for inter-service gRPC on ports 3550, 5050,
     7000, 8080, 9555, 50051, 7070).

## Notes

- **`shoppingassistantservice`** depends on Google Cloud (AlloyDB, Vertex AI).
  It will fail to start without GCP credentials. Set the
  `GCP_CREDENTIALS_SECRET_ARN` in the task definition's `secrets` section to
  an AWS Secrets Manager ARN containing the GCP service account JSON, and
  update the service code to read from that env var. Alternatively, exclude
  this service from the deploy matrix.
- **Multi-arch:** images are built for `linux/amd64` only (matching
  `docker-compose.yml`).
- **Cost:** EC2 instances run continuously. Use a capacity provider with auto
  scaling to reduce idle cost. Consider Fargate Spot for non-production.
