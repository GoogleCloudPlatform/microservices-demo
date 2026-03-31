# Black Friday Cahier Des Charges - Traceability Matrix

Source: `BlackFriday_CahierDesCharges MT5.pdf`.

Status legend:
- Done: available in repo as runnable asset
- Partial: foundation exists but still needs project-specific completion
- Pending: not yet implemented in this repo

| Requirement | Status | Existing Artifacts | Next Action |
| --- | --- | --- | --- |
| Terraform modules + remote state + workspaces | Done | `terraform/aws-module1/`, `terraform/aws-module1/bootstrap-state/`, `.github/workflows/aws-module1-terraform.yaml` | Keep environment-specific tfvars updated |
| EKS deployment baseline (multi-AZ infra) | Done | `terraform/aws-module1/modules/vpc/`, `terraform/aws-module1/modules/eks/` | Validate quotas and target sizing on final account |
| CI/CD + GitOps | Partial | `.github/workflows/*`, `gitops/argocd/*` | Set real repository URL and environment promotion flow |
| IAM/policies least privilege | Partial | baseline AWS provider + EKS module | Add IAM role boundaries and explicit least-privilege policies |
| Network security | Partial | `kustomize/components/network-policies/` | Add AWS SG/NACL/WAF hardening for public ingress path |
| Secrets management + rotation | Pending | N/A | Integrate AWS Secrets Manager + rotation policy |
| Vulnerability scanning (Trivy / OWASP ZAP) | Done | `.github/workflows/blackfriday-security-scans.yaml` | Connect workflow outputs to team reporting |
| HPA / autoscaling | Done | `kustomize/components/blackfriday-autoscaling/` | Tune thresholds from production load metrics |
| Cluster autoscaler strategy | Partial | Terraform node group sizing + `node_capacity_type` | Add/validate Cluster Autoscaler deployment and policies |
| Load tests 5K -> 90K | Done | `scripts/blackfriday/set-load-profile.sh`, `kustomize/components/blackfriday-week1-loadtest/` | Run full campaign and archive evidence |
| Observability (CloudWatch + Prom/Grafana/Jaeger) | Partial | `kustomize/components/google-cloud-operations/`, docs playbooks | Deploy AWS-native dashboards and alerting in final env |
| Chaos engineering | Partial | Week 3 playbook (`docs/blackfriday/week3-pre-blackfriday.md`) | Implement repeatable chaos scenarios and evidence logs |
| FinOps (cost control, Spot, rightsizing) | Partial | Terraform `node_capacity_type`, docs playbooks | Add budget alarms and scaling guardrails per environment |
| Runbooks and war room process | Done | `docs/blackfriday/demo-war-room-runbook.md` | Complete with team names and real escalation channels |
