**Quick start**

Run the follwing commands:

```

minikube start --memory=15970 --cpus=6 --network-plugin=cni --cni=calico

skaffold build
```

Enter the helm chart folder and install the App:
Install Istio,kiali,prom,grafana using the following commands:
istioctl install
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.21/samples/addons/kiali.yaml
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.21/samples/addons/grafana.yaml
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.21/samples/addons/prometheus.yaml

```
kubectl create namespace hipster-app
kubectl label namespace hipster-app istio-injection=enabled
cd helm-chart
helm install onlineboutique . -n hipster-app
cd ../istio-workshop
kubectl apply -f addons-ingress.yaml
kubectl apply -f frontend-ingress-gateway.yaml

canary deploy
kubectl apply -f frontend-v2.yaml
kubectl apply -f frontend-virtualservice-split.yaml
kubectl apply -f frontend-destinationrule.yaml



To access you should configure in /etc/hosts
127.0.0.1       control.test
127.0.0.1       app.test
To create a network tunnel to access Kubernetes services:
minikube tunnel -p profile_name
```
