#!/bin/bash

# Update packages and install Node.js and npm
sudo apt-get update
sudo apt-get install -y nodejs npm

# Install pm2, a production process manager for Node.js
sudo npm install pm2 -g

# Create a directory for the app
sudo mkdir -p /opt/app
sudo chown -R $(whoami):$(whoami) /opt/app
cd /opt/app

# Create the package.json file
cat <<'EOF' > package.json
{
  "name": "mock-crm-service",
  "version": "1.0.0",
  "main": "app.js",
  "dependencies": {
    "express": "^4.18.2"
  }
}
EOF

# Create the app.js file with the mock CRM logic
cat <<'EOF' > app.js
const express = require('express');
const app = express();
const port = 8080;

// Middleware to parse JSON bodies
app.use(express.json());

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

# Start the application using pm2 to run it in the background
pm2 start app.js --name "crm-app"

