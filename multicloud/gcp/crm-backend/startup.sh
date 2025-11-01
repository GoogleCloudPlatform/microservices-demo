#!/bin/bash

# Update packages and install curl
sudo apt-get update
sudo apt-get install -y curl

# Install nvm (Node Version Manager) and Node.js v18
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install 18
nvm use 18

# Create symlinks to make node and pm2 available globally
sudo ln -s "$(which node)" "/usr/local/bin/node"
sudo ln -s "$(which npm)" "/usr/local/bin/npm"

# Install pm2, a production process manager for Node.js
npm install pm2 -g
sudo ln -s "$(which pm2)" "/usr/local/bin/pm2"

# Create a directory for the app
sudo mkdir -p /opt/app
sudo chown -R $(whoami):$(whoami) /opt/app
cd /opt/app

# Create the package.json file
cat <<'EOF' > package.json
{
  "name": "mock-crm-service",
  "version": "1.0.0",
  "description": "Mock CRM Backend Service with GCS Logging",
  "main": "app.js",
  "scripts": {
    "start": "node app.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "@google-cloud/storage": "^7.7.0"
  }
}
EOF

# Create the app.js file with the mock CRM logic
cat <<'EOF' > app.js
const express = require('express');
const { Storage } = require('@google-cloud/storage');

const app = express();
const port = 8080;

// Initialize Google Cloud Storage only in production
let storage, bucket;
if (process.env.NODE_ENV === 'production') {
  storage = new Storage();
  const BUCKET_NAME = 'crm-online-boutique-bucket';
  bucket = storage.bucket(BUCKET_NAME);
}

// Async logging function
async function logToGCS(logEntry) {
  if (!bucket) {
    // Silently fail in non-production environments
    return;
  }
  try {
    const date = new Date().toISOString().split('T')[0];
    const fileName = `logs/${date}/${Date.now()}-${Math.random().toString(36).substring(7)}.json`;
    await bucket.file(fileName).save(JSON.stringify(logEntry, null, 2));
  } catch (error) {
    console.error('Failed to write log to GCS:', error.message);
  }
}

// Middleware to parse JSON bodies
app.use(express.json());

// Logging middleware - runs for all requests
app.use((req, res, next) => {
  const startTime = Date.now();
  
  res.on('finish', () => {
    const logEntry = {
      timestamp: new Date().toISOString(),
      method: req.method,
      path: req.path,
      statusCode: res.statusCode,
      responseTimeMs: Date.now() - startTime,
      clientIp: req.ip,
      userAgent: req.get('user-agent') || 'unknown'
    };
    
    // Log asynchronously (don't wait)
    logToGCS(logEntry).catch(err => console.error('Logging error:', err));
  });
  
  next();
});

// In-memory data store with two hardcoded customers
let customers = [
  { name: 'John', surname: 'Doe' },
  { name: 'Jane', surname: 'Smith' }
];

// GET endpoint to list all customers
app.get('/customers', (req, res) => {
  console.log('GET /customers - Returning customer list');
  res.status(200).json(customers);
});

// POST endpoint to add a new customer
app.post('/customers', (req, res) => {
  const { name, surname } = req.body;

  if (!name || !surname) {
    console.log('POST /customers - Failed: Missing name or surname');
    return res.status(400).json({ error: 'Name and surname are required.' });
  }

  const newCustomer = { name, surname };
  customers.push(newCustomer);
  
  // Cleanup: Keep only the 10 most recent customers
  if (customers.length > 10) {
    const removedCount = customers.length - 10;
    customers = customers.slice(-10); // Keep last 10
    console.log(`POST /customers - Cleaned up ${removedCount} old customer(s), keeping 10 most recent`);
  }
  
  console.log(`POST /customers - Added new customer: ${name} ${surname}. Total: ${customers.length}`);
  res.status(201).json(newCustomer);
});

app.listen(port, '0.0.0.0', () => {
  console.log(`Mock CRM server listening on port ${port}`);
});
EOF

# Install application dependencies
npm install

# Start the application using pm2 to run it in the background with NODE_ENV set
NODE_ENV=production pm2 start app.js --name "crm-app"

# Save the PM2 process list and configure it to start on system boot
pm2 save
pm2 startup systemd -u root --hp /root

