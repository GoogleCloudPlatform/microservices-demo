# Week 1 Load Test Component

This component sets the `loadgenerator` deployment to a first-week baseline:

- `USERS=1000`
- `RATE=25`

Use it for the "Setup & Foundations" phase to validate initial scaling and stability.

## Enable

From the `kustomize/` directory:

```bash
kustomize edit add component components/blackfriday-week1-loadtest
kubectl apply -k .
```
