# How to deploy the application to a local minikube cluster

starting at root directory:

```
minikube start --cpus=4 --memory=8192 --driver=docker
```

```
eval $(minikube -p minikube docker-env)
```

```
minikube tunnel
```

```
skaffold build
```

```
skaffold dev
```

```
minikube service frontend-external
```

---

This always works, because it uses the official images for the services

```
minikube start --cpus=4 --memory 4096 --disk-size 32g
```

```
kubectl apply -f ./release/kubernetes-manifests.yaml
```

```
minikube service frontend-external
```
