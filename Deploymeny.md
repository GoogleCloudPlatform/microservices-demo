# To Deploy The Application To EKS

1. Make sure you are login to AWS.
2. Set the Kube Config:
```bash
aws eks --region eu-west-2 update-kubeconfig --name <cluster-name>
```
3. Apply the manifest to deploy:
```bash
kubectl apply -f release/kubernetes-manifests.yaml
```
4. Wait until deployment is complete, get the load balancer address:
```bash
kubectl get svc frontend-external
```