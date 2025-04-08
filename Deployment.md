# 🚀 Deploying the Application to EKS
### 1. Login to AWS
Make sure you're authenticated with your AWS account.

### 2. Set up your kubeconfig
Run the following command to configure access to your EKS cluster:
```bash
aws eks --region eu-west-2 update-kubeconfig --name <cluster-name>
```

### 3.Deploy the application
Apply the Kubernetes manifests to start the deployment:
```bash
kubectl apply -f release/kubernetes-manifests.yaml
```

### 4. Get the load balancer address
Once the deployment is complete, retrieve the external IP:
```bash
kubectl get svc frontend-external
```

## 🔄 Updating the Application (after code changes)
If you've made changes to the app (e.g. added a new error message), you'll need to rebuild and push the Docker image for the updated service:
```bash
sudo docker build -t <app-name>:<tag> .
sudo docker tag <app-name>:<tag> 554043692091.dkr.ecr.eu-west-2.amazonaws.com/sre-agent:<tag>
docker push 554043692091.dkr.ecr.eu-west-2.amazonaws.com/sre-agent/<app-name>:<tag>
```

Finally, update the image reference in [kubernetes-manifests.yaml](release/kubernetes-manifests.yaml) to point to the new tag you just pushed.