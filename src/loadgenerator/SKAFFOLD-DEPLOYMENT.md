# Deploying Multicloud Load Generator with Skaffold

This guide shows you how to deploy the enhanced load generator with multicloud support using Skaffold.

## Prerequisites

1. **Get your service IP addresses** from terraform outputs:
   ```bash
   # In your terraform directories
   cd multicloud/aws/ && terraform output
   cd ../azure/ && terraform output  
   cd ../gcp/ && terraform output
   ```

2. **Have Skaffold installed** and a Kubernetes cluster configured

## Configuration Steps

### Step 1: Update Environment Variables

Replace the placeholder IP addresses in the Kubernetes manifests with your actual service IPs:

**In `kubernetes-manifests/loadgenerator.yaml`:**
```yaml
- name: AWS_ACCOUNTING_URL
  value: "http://YOUR_AWS_EC2_IP:8080"        # Replace with actual AWS IP
- name: AZURE_ANALYTICS_URL  
  value: "http://YOUR_AZURE_VM_IP:8080"       # Replace with actual Azure IP
- name: GCP_CRM_URL
  value: "http://YOUR_GCP_INSTANCE_IP:8080"   # Replace with actual GCP IP
```

**In `kustomize/base/loadgenerator.yaml`:** (if using kustomize)
```yaml
- name: AWS_ACCOUNTING_URL
  value: "http://YOUR_AWS_EC2_IP:8080"        # Replace with actual AWS IP
- name: AZURE_ANALYTICS_URL
  value: "http://YOUR_AZURE_VM_IP:8080"       # Replace with actual Azure IP  
- name: GCP_CRM_URL
  value: "http://YOUR_GCP_INSTANCE_IP:8080"   # Replace with actual GCP IP
```

### Step 2: Deploy with Skaffold

#### Option A: Deploy Everything (Recommended)
```bash
# Deploy the full boutique application + multicloud load generator
skaffold run
```

#### Option B: Deploy Only Load Generator
```bash
# Deploy just the load generator (requires main app to be running)
skaffold run -m loadgenerator
```

#### Option C: Development Mode
```bash
# Run in development mode with file watching
skaffold dev
```

#### Option D: Deploy Load Generator Only
```bash  
# Deploy only load generator module
skaffold dev -m loadgenerator
```

## Alternative Configuration Methods

### Method 1: Use Skaffold Profiles with Environment Substitution

Create a custom profile in `skaffold.yaml`:

```yaml
profiles:
- name: multicloud
  patches:
  - op: replace
    path: /manifests/rawYaml/0
    value: ./kubernetes-manifests/loadgenerator-multicloud.yaml
```

Then create `kubernetes-manifests/loadgenerator-multicloud.yaml` with environment substitution:

```yaml
# In the env section:
- name: AWS_ACCOUNTING_URL
  value: "http://$(AWS_IP):8080"
- name: AZURE_ANALYTICS_URL  
  value: "http://$(AZURE_IP):8080"
- name: GCP_CRM_URL
  value: "http://$(GCP_IP):8080"
```

Deploy with:
```bash
AWS_IP=your-aws-ip AZURE_IP=your-azure-ip GCP_IP=your-gcp-ip skaffold run -p multicloud
```

### Method 2: Use ConfigMap

Create a ConfigMap for configuration:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: multicloud-config
data:
  AWS_ACCOUNTING_URL: "http://your-aws-ip:8080"
  AZURE_ANALYTICS_URL: "http://your-azure-ip:8080"
  GCP_CRM_URL: "http://your-gcp-ip:8080"
```

Then reference it in the deployment:
```yaml
envFrom:
- configMapRef:
    name: multicloud-config
```

### Method 3: Use Kubernetes Secrets (for sensitive URLs)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: multicloud-secrets
type: Opaque
stringData:
  AWS_ACCOUNTING_URL: "http://your-aws-ip:8080"
  AZURE_ANALYTICS_URL: "http://your-azure-ip:8080"  
  GCP_CRM_URL: "http://your-gcp-ip:8080"
```

Reference in deployment:
```yaml
envFrom:
- secretRef:
    name: multicloud-secrets
```

## Verification

### Check Pod Status
```bash
kubectl get pods -l app=loadgenerator
```

### View Logs
```bash
# Check load generator logs
kubectl logs -f deployment/loadgenerator

# Look for multicloud task execution
kubectl logs -l app=loadgenerator | grep -E "(processTransaction|recordMetrics|manageCustomer)"
```

### Monitor Locust Statistics
```bash
# Watch for task execution stats
kubectl logs -l app=loadgenerator | grep -A 10 "Aggregated"
```

## Troubleshooting

### Common Issues

1. **Connection refused errors:**
   ```bash
   # Check if your services are accessible from the cluster
   kubectl run test-pod --image=busybox -it --rm -- wget -O- http://YOUR_AWS_IP:8080/transactions
   ```

2. **Pod not starting:**
   ```bash
   # Check pod events
   kubectl describe pod -l app=loadgenerator
   ```

3. **Environment variables not set:**
   ```bash
   # Check container environment
   kubectl exec deployment/loadgenerator -- env | grep -E "(AWS|AZURE|GCP)"
   ```

### Enable Debug Mode

Add debug environment variables:
```yaml
- name: LOCUST_LOGLEVEL
  value: "DEBUG"
```

## Load Testing Results

You should see output like:
```
Name                    # reqs    # fails  |   Avg     Min     Max  Median  |   req/s failures/s
addToCart                  45       0(0%)  |   156      89     289     150  |    2.1     0.0
browseProduct             450       0(0%)  |    98      67     187      95  |   21.0     0.0
processTransaction         45       0(0%)  |   134      76     245     125  |    2.1     0.0
recordMetrics              47       0(0%)  |    89      54     156      86  |    2.2     0.0
manageCustomer             46       0(0%)  |   167      92     298     155  |    2.1     0.0
```

This confirms that your multicloud services are being tested successfully alongside the boutique application! 