# CRM Frontend Dashboard

A beautiful, responsive customer dashboard that displays CRM customer data from the backend service.

## Features

- **Real-time Customer Display**: Fetches and displays customer list from CRM backend
- **Auto-refresh**: Automatically updates every 30 seconds
- **Responsive Design**: Works on desktop and mobile devices
- **Beautiful UI**: Modern gradient design with Bootstrap 5
- **Customer Cards**: Visual representation with initials and colors
- **Health Check**: `/health` endpoint for load balancer health checks

## Architecture

```
Internet → L7 Load Balancer → Frontend VM → Backend VM
           (external IP)       (10.3.0.x)    (10.3.0.2:8080)
```

## API Integration

The frontend calls the CRM backend API:
- **Backend URL**: `http://10.3.0.2:8080/customers`
- **Method**: GET
- **Response**: JSON array of customer objects

## Local Development

```bash
npm install
npm start
```

Server runs on `http://localhost:8080`

## Deployment

The frontend is deployed via Terraform as part of `crm.tf`:
1. VM instance created with startup script
2. Script installs Node.js and dependencies
3. Frontend code embedded in startup script
4. L7 Load Balancer provides external access
5. Health checks ensure availability

## Endpoints

- **`/`** - Main customer dashboard
- **`/health`** - Health check endpoint (returns JSON)

## Tech Stack

- **Backend**: Node.js + Express
- **Frontend**: HTML5 + JavaScript (Vanilla)
- **UI Framework**: Bootstrap 5 (CDN)
- **Icons**: Bootstrap Icons (inline SVG)

