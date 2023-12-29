**Quick start**

Run the follwing commands:

```
minikube start --memory=15970 --cpus=6 --network-plugin=cni --cni=calico
istioctl install
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/grafana.yaml
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/jaeger.yaml
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/kiali.yaml
kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.20/samples/addons/prometheus.yaml

skaffold build
```

Enter the helm chart folder and install the App:

```
kubectl create namespace hipster-app
kubectl label namespace hipster-app istio-injection=enabled
helm install onlineboutique .
```
