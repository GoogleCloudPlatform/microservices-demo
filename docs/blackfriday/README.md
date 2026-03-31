# Black Friday Survival - Delivery Hub

This folder translates the project cahier des charges into concrete repo deliverables.

## Global Goal

Maintain platform availability while scaling up to **90K concurrent users** during the final simulation.

## Delivery Timeline

1. Week 1 - Setup & foundations:
   - [week1-setup-foundations.md](week1-setup-foundations.md)
   - [week1-loadtest-1k-monitoring-runbook.md](week1-loadtest-1k-monitoring-runbook.md)
   - [week_1_livrable.md](week_1_livrable.md)
2. Week 2 - Hardening & optimization:
   - [week2-hardening-optimization.md](week2-hardening-optimization.md)
   - [week2-livrable.md](week2-livrable.md)
   - [week2_commands_explication.md](week2_commands_explication.md)
3. Week 3 - Pre-Black Friday readiness:
   - [week3-pre-blackfriday.md](week3-pre-blackfriday.md)
4. Demo days - War Room execution:
   - [demo-war-room-runbook.md](demo-war-room-runbook.md)

## Traceability

For requirement-by-requirement status, see:
- [requirements-traceability.md](requirements-traceability.md)

## AWS Access Runbook

For full copy/paste commands from Terraform bootstrap to accessing the live web app:
- [README-aws-webapp-access.md](README-aws-webapp-access.md)

## Fast Execution Flow

From repository root:

```bash
# 1) Deploy app baseline
kubectl apply -k kustomize

# 2) Enable security + autoscaling components
cd kustomize
kustomize edit add component components/network-policies
kustomize edit add component components/blackfriday-autoscaling
kubectl apply -k .

# 3) Run progressive load profiles
cd ..
./scripts/blackfriday/set-load-profile.sh week2-5k
./scripts/blackfriday/set-load-profile.sh week2-20k
./scripts/blackfriday/set-load-profile.sh week2-50k
./scripts/blackfriday/set-load-profile.sh week3-70k
./scripts/blackfriday/set-load-profile.sh demo-90k
```

## Related Repo Assets

- AWS infra foundation: `terraform/aws-module1/`
- Week 1 load test component: `kustomize/components/blackfriday-week1-loadtest/`
- Week 2 autoscaling component: `kustomize/components/blackfriday-autoscaling/`
- Security scans workflow: `.github/workflows/blackfriday-security-scans.yaml`
