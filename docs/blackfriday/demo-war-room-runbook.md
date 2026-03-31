# Black Friday Survival - Demo War Room Runbook

Use this runbook on the two final simulation days.

## 1. Team Roles

Assign one owner per role:
- Incident Commander: prioritization and decisions
- Platform Lead: EKS, nodes, networking, ingress
- App Lead: service health and rollout actions
- Observability Lead: dashboards, alerts, timelines
- Scribe: timeline, actions, decisions, post-mortem notes

## 2. Severity Levels

- SEV-1: checkout unavailable, major outage, or sustained high error rate
- SEV-2: partial degradation, rising latency with user impact
- SEV-3: non-critical degradation, no direct user loss yet

## 3. 8-Hour Operations Rhythm

- T0 kickoff: confirm dashboards and alert channels are live
- Every 15 minutes: health checkpoint (latency, error rate, saturation)
- Every incident: open incident log entry immediately
- End of day: freeze timeline and publish summary

## 4. Standard Incident Loop

1. Detect and classify severity
2. Assign owner and mitigation action
3. Communicate status update
4. Validate service recovery
5. Record root cause hypothesis and follow-up

## 5. Mandatory Metrics During Demo

- frontend p95 latency
- checkout error rate
- HPA replica counts for critical deployments
- node count and pending pods
- recovery time after injected fault

## 6. Communication Template

```text
[Time] [Severity] [Service]
Impact: ...
Hypothesis: ...
Action in progress: ...
Next update ETA: 15 min
```

## 7. Post-Mortem Template (Day 2)

1. Incident summary
2. Timeline
3. Root cause
4. Detection and response quality
5. What worked well
6. What failed
7. Immediate corrective actions
8. Long-term preventive actions
