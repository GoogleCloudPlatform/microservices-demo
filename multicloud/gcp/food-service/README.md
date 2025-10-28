# Food Service

A simple REST API service for managing food items, designed to run on Google Cloud Run. This service integrates with the Inventory Service to check inventory status when listing food items.

## Features

- RESTful API for food item management
- Automatic inventory checking via Inventory Service integration
- Cloud Run deployment ready
- Container-based deployment with Cloud Build

## API Endpoints

- `GET /health` - Health check endpoint
- `GET /food` - List all food items (also calls Inventory Service to check stock)
- `GET /food/:id` - Get a specific food item
- `POST /food` - Add a new food item
- `PUT /food/:id` - Update a food item
- `DELETE /food/:id` - Delete a food item

## Environment Variables

- `PORT` - Server port (default: 8080)
- `INVENTORY_SERVICE_URL` - URL of the inventory service (optional, for inventory integration)

## Local Development

```bash
npm install
npm start
```

The service will be available at `http://localhost:8080`

### Testing with Inventory Integration

To test the inventory integration locally:

```bash
export INVENTORY_SERVICE_URL=http://your-inventory-service:8080
npm start
```

## Building and Deploying

### Prerequisites

1. Create an Artifact Registry repository:
```bash
gcloud artifacts repositories create food-repo \
  --repository-format=docker \
  --location=europe-west1 \
  --description="Food service container images"
```

2. Enable required APIs:
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

### Build and Push to Artifact Registry

From the `multicloud/gcp/food-service` directory:

```bash
# Submit build to Cloud Build
gcloud builds submit --config=cloudbuild.yaml

# Or build manually
docker build -t europe-west1-docker.pkg.dev/PROJECT_ID/food-repo/food-service:latest .
docker push europe-west1-docker.pkg.dev/PROJECT_ID/food-repo/food-service:latest
```

### Deploy with Terraform

From the `multicloud/gcp` directory:

```bash
terraform init
terraform apply
```

The terraform configuration will:
- Enable necessary Google Cloud APIs
- Deploy the container to Cloud Run
- Configure public access
- Output the service URL

