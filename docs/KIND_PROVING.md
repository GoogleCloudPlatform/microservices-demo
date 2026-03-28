# KIND Operational Proving

This document captures the live `kind`-based operational proving pass for the non-ML runtime path.

## Validated Scenarios

1. Pod kill and controller recovery
- `recommendationservice` pod deletion was recovered by Kubernetes.
- AEGIS emitted `runtime_degradation_detected` and `runtime_recovered`.
- No unnecessary automated remediation was triggered for the transient recovery case.

2. Persistent crash and containment
- A forced `recommendationservice` crash loop triggered runtime detection, bounded retries, containment, and an operator acknowledgement flow.
- The incident remained active for manual ownership and emitted a persisted `incident_acknowledged` event.

3. Redis dependency break
- A broken `redis-cart` workload was classified as `dependency_failure`.
- The incident correctly targeted the shared dependency root cause and preserved the dependency-oriented decision path.
- Containment produced a persisted remediation trail instead of silently failing.

## Core Commands

```bash
bash infra/k8s/bootstrap-kind.sh
bash infra/k8s/build-kind-images.sh
bash infra/k8s/deploy-kind.sh
kubectl -n aegis-system port-forward svc/aegis-backend 8001:8001
```

Representative failure injections:

```bash
kubectl -n default delete pod -l app=recommendationservice --wait=false

kubectl -n default patch deployment recommendationservice --type='json' -p='[
  {"op":"replace","path":"/spec/template/spec/containers/0/image","value":"busybox:1.36"},
  {"op":"add","path":"/spec/template/spec/containers/0/command","value":["/bin/sh","-c","exit 1"]}
]'

kubectl -n default patch deployment redis-cart --type='json' -p='[
  {"op":"add","path":"/spec/template/spec/containers/0/command","value":["/bin/sh","-c","sleep 3600"]},
  {"op":"add","path":"/spec/template/spec/containers/0/args","value":[]}
]'
```

Useful verification endpoints:

```bash
curl -s http://localhost:8001/health
curl -s http://localhost:8001/incidents/active
curl -s "http://localhost:8001/events?limit=40"
curl -s http://localhost:8001/infrastructure
```

## What Changed During Proving

- Kubernetes runtime telemetry now comes from Prometheus/cAdvisor in Kubernetes mode rather than Docker-only collection.
- Cold or empty telemetry no longer produces fake model confidence.
- Predictive alerts remain visible, but generic LSTM-only spikes no longer trigger automatic remediation.
- Runtime monitoring now records transient workload degradation and recovery as first-class events.
- Automated runtime remediation is delayed during backend warm-up to avoid startup churn.
- Dependency failures now preserve dependency-aware decisions instead of being downgraded by unrelated memory matches.

## Remaining Notes

- Contained incidents remain active until acknowledged or the backend process is restarted; this is intentional for operator ownership, but it means a proving run can leave active incidents in memory until cleared.
- `reroute_service` remains best-effort and requires an explicitly configured healthy alternative target.
