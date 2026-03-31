# Black Friday Survival - Week 3 (Pre-Black Friday)

Week 3 objective from the cahier des charges:
- inject controlled failures (chaos)
- optimize cloud costs
- run a 70K rehearsal
- finalize incident runbooks and war room process

## 1. Chaos Engineering Drills

Start with safe Kubernetes-level chaos drills:

```bash
# Kill one frontend pod and watch recovery
kubectl delete pod -l app=frontend

# Restart recommendation deployment
kubectl rollout restart deployment/recommendationservice

# Observe rollout status
kubectl rollout status deployment/frontend
kubectl rollout status deployment/recommendationservice
```

Track during each drill:
- time to detect
- time to mitigate
- user impact window
- lessons learned

## 2. FinOps and Cost Optimization

Enable Spot nodes for non-critical pools during rehearsals by setting in `terraform/aws-module1/terraform.tfvars`:

```hcl
node_capacity_type = "SPOT"
```

Then apply:

```bash
cd terraform/aws-module1
terraform plan -var-file=terraform.tfvars
terraform apply -var-file=terraform.tfvars
```

Keep at least one reliable on-demand capacity path for critical workloads.

## 3. 70K General Rehearsal

From repo root:

```bash
./scripts/blackfriday/set-load-profile.sh week3-70k
```

Validate:
- no cascading crash
- acceptable error budget
- HPA + node scaling converge
- recovery remains automatic after injected incidents

## 4. Runbooks and Incident Procedures

Use and complete:
- [demo-war-room-runbook.md](demo-war-room-runbook.md)

Mandatory outputs before demo day:
- incident severities and escalation matrix
- who does what during incidents (roles)
- communication cadence every 15 minutes
- post-incident template ready

## 5. Week 3 Exit Criteria

- chaos drills executed and documented
- spot/on-demand cost strategy validated
- 70K rehearsal completed
- war room runbook complete and shared
