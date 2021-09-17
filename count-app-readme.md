Deploying an additional workload to launch attacks from inside the Cluster

1. ### **Create a cluster on the Google cloud platform with minimum requirements to run microservices.**

By default, Kubernetes has a flat networking schema, which means any pod/service within the cluster can talk to others without any restrictions. The namespaces within the cluster don’t have any network security restrictions by default, anyone in the namespace can talk to other namespaces.

### **Deploying simple services into Kubernetes**

We are going to deploy two different services (cache-db and count-app) and different namespaces.
1. ### **Deploy these two services with  different namespaces** 

Run the following command to deploy the **cache-db** service in **cache-db-ns** namespace.
```
Kubectl apply -f cache.yaml
```
Run the following command to deploy the **count-app** service in **count-app-ns** namespace.


```
Kubectl apply -f count.yaml
```
***Run the following command to expose the count application locally***


```
kubectl -n count-app-ns port-forward service/count-app-service --address 0.0.0.0 3000:3000 > /dev/null 2>&1 &
```



- Access the application in the custom-port 3000

Command to access the application:
```
curl localhost:3000
```

When you access the application, it will show the banner like  **Welcome to Kubernetes** and how many times you have visited the website.

Gaining access to the cache-db service from default namespace




- Run the hacker-container in default namespace


```
kubectl run -it hacker-container --image=madhuakula/hacker-container -- sh
```
- As we already know the cache-db-service name and namespace cache-db-ns we can use the below command to connect to cache-db

Enter the commands in the hacker-container > # redis-cli -h cache-db-service.cache-db-ns

`Then you will enter into the cache-db

`# KEYS \*

Here you can see the number of hits in cache-db. Due to no default network security policy in the Kubernetes, we can access the different services in the different namespace from the default namespace from hacker-container.

