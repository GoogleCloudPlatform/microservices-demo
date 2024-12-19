# Deployment of Google's Online Boutique on local Minikube cluster

This project is a fork of Google's Online Boutique, which is a demo for microservices architecture ([Github](https://github.com/GoogleCloudPlatform/microservices-demo)). As part of the course "Continuous Software Engineering" at Technical University of Berlin, this project is the result of the group work of Ivan Crespo Gadea, Javad Ismayilzada and Philip Morgner. We implemented the languageservice to make Online Boutique's content available in different languages. The functionality is limited to product names and descriptions and ad content. It serves as a demo of the integration of our languageservice microservice. In the frontend, there is a dropdown to select from three different languages, English, German and Spanish. The loadgenerator microservice is enhanced to select different languages as well. The default language is English.

Furthermore, we integrated the project with Ansible to enable a simple deployment process to a minikube cluster on a remote server. Currently it is only tested for localhost and prerequisites (docker, minikube, skaffold, kubectl) must be pre-installed. In a next step we created Github Actions to automate the deployment process and leverage Github's Container Registry (ghrc).

---

## Prerequisites

1. Make sure you have all dependencies installed: [minikube](https://minikube.sigs.k8s.io/docs/start/?arch=%2Flinux%2Fx86-64%2Fstable%2Fbinary+download), [kubectl](https://kubernetes.io/docs/reference/kubectl/), [skaffold](https://skaffold.dev/), [docker](https://www.docker.com/).

2. Open a terminal and clone this project:

```
git clone git@github.com:philip-morgner/microservices-demo.git
```

3. `cd` into this project

```
cd microservices-demo
```

4. Follow steps in `Getting started` section

---

## Getting started

**Note: This has been tested for Ubuntu 24.04 and Windows 10.**

1. Start local minikube cluster with sufficient resources. If a previous minikube cluster exists, delete it first (section `Delete previous minikube cluster`).

```
minikube start --cpus=4 --memory=8192 --driver=docker
```

2. Build docker images of microservices:

```
skaffold build
```

3. a) For development:

```
skaffold dev
```

3. b) For production:

```
skaffold run
```

4. Access the frontend in your browser:

```
minikube service frontend-external
```

---

## Deployment via Ansible

This has been tested for Ubuntu 24.04 with localhost as target server.

1. Install Ansible

```
sudo apt install ansible-core
```

2. Adjust the hosts file (currently configured to deploy on localhost)

3. Start the playbook

```
ansible-playbook .ansible/main.yaml -i hosts
```

---

## Debug

If there are any issues with the deployment process, inspect docker containers and kubernetes logs on minikube cluster

1. Start minikube cluster

```
minikube start --cpus=4 --memory=8192 --driver=docker
```

2. Access docker env inside minikube cluster

```
eval $(minikube -p minikube docker-env)
```

3. Create tunnel (when using services of type LoadBalancer)

```
minikube tunnel
```

4. Explicitly build images of services

```
skaffold build
```

5. Start development mode (autmatically rebuild images when code changes) and start microservices on minikube cluster

```
skaffold dev
```

6. a) If it worked, access the frontend like this:

```
minikube service frontend-external
```

6. b) Else: inspect pods, logs, docker containers etc.

```
kubectl get pods
```

```
kubectl describe pod <pod_id>
```

```
kubectl logs <pod_id>
```

```
docker container ls -a
```

---

## Delete previous Minikube cluster

If there was an existing minikube cluster with less resources, delete it and create a new one.

```
minikube stop
```

```
minikube delete
```

```
minikube start --cpus=4 --memory=8192 --driver=docker
```

---

## Run official images as provided by Google on local cluster

This should always work, because it uses the official images for the services. If it doesn't, it indicates that your local cluster needs more resources. See more info, check out [Google's README.md](https://github.com/GoogleCloudPlatform/microservices-demo/blob/main/docs/development-guide.md#option-2---local-cluster)

```
minikube start --cpus=4 --memory 4096 --disk-size 32g
```

```
kubectl apply -f ./release/kubernetes-manifests.yaml
```

```
minikube service frontend-external
```

---

## Start languageservice as standalone service

1. Open terminal and `cd` into languageservice directory

```
cd microservices-demo/src/languageservice
```

2. Start the service

   **Note: Use `PORT` env variable to change port it is running on (default: 3000)**

```
node index.js
```
