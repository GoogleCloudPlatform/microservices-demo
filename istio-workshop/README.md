**Quick start**

Run the follwing commands:

```

minikube start --memory=15970 --cpus=6 --network-plugin=cni --cni=calico

skaffold build
```

Enter the helm chart folder and install the App:
Install Istio,kiali,prom,grafana using the following commands:
istioctl install
kubectl delete -f https://raw.githubusercontent.com/istio/istio/release-1.21/samples/addons/kiali.yaml
kubectl delete -f https://raw.githubusercontent.com/istio/istio/release-1.21/samples/addons/grafana.yaml
kubectl delete -f https://raw.githubusercontent.com/istio/istio/release-1.21/samples/addons/prometheus.yaml

```
kubectl create namespace hipster-app
kubectl label namespace hipster-app istio-injection=enabled
cd helm-chart
helm install onlineboutique . -n hipster-app
cd ../istio-workshop
    kubectl apply -f addons-ingress.yaml
kubectl apply -f frontend-ingress-gateway.yaml

Traffic splitting
kubectl apply -f frontend-v2.yaml
kubectl apply -f frontend-virtualservice-split.yaml
kubectl apply -f frontend-destinationrule.yaml

Istio Peer authentication(mTLS) - Permissive mode
kubectl apply -f hipster-app-mtls.yaml

Simulating traffic outside the mesh (unencrypted traffic)
kubectl create namespace test
kubectl apply -f redis.yaml

Enter to redis pod and run
wget frontend.hipster-app.svc.cluster.local
Istio Peer authentication -  Strict Mode  (Blocking access outside the mesh)
edit hipster-app-mtls.yaml to STRICT
Enter to redis pod and try again.
edit redis.yaml and change sidecar.istio.io/inject: "false" to true

Authorization Policies - Access from custom service to redis-cart
kubectl apply -f busybox.yaml
exec on busybox and run:
telnet redis-cart 6379

Authorization Policies - Enforce on redis-cart service only from cartservice
cd ../helm-chart
change values service account to True - This create service account each deployment and assosiate with SA by for example:
      serviceAccount: cartservice
helm upgrade onlineboutique . -n hipster-app
kubectl apply -f authorization-policy.yaml

Monitoring Egress Traffic
Enter busybox and wget to www.google.com
see kiali logs
Restrict Egress Traffic - Changed istio config from ALLOW_ALL to REGISTRY_ONLY
istioctl install --set meshConfig.outboundTrafficPolicy.mode=REGISTRY_ONLY
Try to access www.google.com

Restrict Egress Traffic - Allow only google.com
kubectl apply -f google-serviceentry.yaml
and try again


To access you should configure in /etc/hosts
127.0.0.1       control.test
127.0.0.1       app.test
To create a network tunnel to access Kubernetes services:
minikube tunnel -p profile_name
```
