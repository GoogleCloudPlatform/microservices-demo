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
helm upgrade --install appdeployment ./release/app-deployment \
  --set image.repository_uri=<account-id>.dkr.ecr.<region>.amazonaws.com/<namespace>

# e.g. if you have a ecr namespace 
helm upgrade --install appdeployment ./release/app-deployment \
  --set image.repository_uri=12345678.dkr.ecr.eu-west-2.amazonaws.com/my-ecr-namespace
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
sudo docker tag <app-name>:<tag> <ecr-uri>/<app-name>:<tag>
docker push <ecr-uri>/<app-name>:<tag>
```

Finally, update the image reference in [kubernetes-manifests.yaml](release/app-deployment/templates/kubernetes-manifests.yaml) to point to the new tag you just pushed.