## **Docker Setup for Local Development**

This directory contains all necessary Docker configurations for running the Microservices Demo project locally. The original project primarily relies on Kubernetes and GCP-specific deployments, but these modifications enable  local execution using Docker and Docker Compose.
---

## **What Changes are Made: 

### **Created a `docker/` Directory**
- Centralized all Docker-related files.

### **Added Dockerfiles for Each Microservice**
- Each microservice now has a dedicated Dockerfile.
- Image sizes have been reduced to improve efficiency.

### **Introduced `docker-compose.yaml` for Local Deployment**
- Enables running all services locally with a single command.

### **Modify GCP-Specific Dependencies**
- This project is tightly depends on GCP-Specific dependencies that's why in local test container are failed to running, so made some changes to make GCP-Specific Dependencies optional and fix for local testing.
- Ensures a fully functional local setup without external cloud dependencies.

---

## Running the Project Locally

### **Build Docker Images**
Run the following command to build images for all services:
```sh
docker-compose build
```

### **Step 2: Start the Services**
Use Docker Compose to launch all microservices:
```sh
docker-compose up -d
```

### **Verify Running Containers**
Check if all services are running:
```sh
docker ps
```

### ** Access the Application**
Once all containers are up, access the microservices via their respective endpoints:
```sh
http://localhost:8080
```

---

## Stopping and Cleaning Up
To stop all services:
```sh
docker-compose down
```

To remove all images, volumes, and containers:
```sh
docker system prune -a
```

---

---

**Maintainer:** [Bharat suthar](@https://github.com/bharatsutharx)

