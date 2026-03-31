# Black Friday Autoscaling Component

This component adds Horizontal Pod Autoscalers (HPA) to critical services for Black Friday load campaigns.

## Included HPAs

- `frontend`
- `checkoutservice`
- `cartservice`
- `recommendationservice`
- `productcatalogservice`
- `currencyservice`
- `paymentservice`

Each HPA uses CPU utilization targets and requires `metrics-server` to be installed.

## Enable

From the `kustomize/` directory:

```bash
kustomize edit add component components/blackfriday-autoscaling
kubectl apply -k .
kubectl get hpa
```

## Notes

- Start with conservative limits and tune `maxReplicas` after each load step.
- Combine with cluster autoscaling to avoid pending pods during high load.
