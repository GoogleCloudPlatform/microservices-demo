#!/bin/bash

# Update packages and install Node.js and npm
sudo apt-get update
sudo apt-get install -y nodejs npm

# Install pm2, a production process manager for Node.js
sudo npm install pm2 -g

# Create a directory for the app
sudo mkdir -p /opt/crm-frontend
sudo chown -R $(whoami):$(whoami) /opt/crm-frontend
cd /opt/crm-frontend

# Create the package.json file
cat <<'EOF' > package.json
{
  "name": "crm-frontend",
  "version": "1.0.0",
  "description": "CRM Customer Dashboard Frontend",
  "main": "app.js",
  "dependencies": {
    "express": "^4.18.2",
    "node-fetch": "^3.3.2"
  }
}
EOF

# Create the frontend app.js file
cat <<'APPJS' > app.js
const express = require('express');
const app = express();
const port = 8080;

// Middleware to parse JSON bodies
app.use(express.json());

app.get('/', (req, res) => {
  res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CRM Customer Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 40px 0; }
        .container { max-width: 900px; }
        .card { border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .card-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 15px 15px 0 0 !important; padding: 20px; }
        .customer-card { transition: transform 0.2s, box-shadow 0.2s; border-left: 4px solid #667eea; }
        .customer-card:hover { transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
        .customer-initials { width: 50px; height: 50px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem; }
        .loading { text-align: center; padding: 40px; }
        .spinner-border { width: 3rem; height: 3rem; }
        .error-message { background: #f8d7da; border: 1px solid #f5c6cb; color: #721c24; padding: 15px; border-radius: 10px; margin: 20px 0; }
        .refresh-btn { transition: all 0.3s; }
        .refresh-btn:hover { transform: rotate(180deg); }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-header">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h2 class="mb-1">CRM Customer Dashboard</h2>
                        <p class="mb-0 opacity-75">Live customer data from backend service</p>
                    </div>
                    <button onclick="loadCustomers()" class="btn btn-light refresh-btn" title="Refresh">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 16 16">
                            <path fill-rule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z"/>
                            <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z"/>
                        </svg>
                    </button>
                </div>
            </div>
            <div class="card-body">
                <div id="loading" class="loading">
                    <div class="spinner-border text-primary" role="status"></div>
                    <p class="mt-3 text-muted">Fetching customer data...</p>
                </div>
                <div id="error" class="error-message" style="display: none;"></div>
                <div id="customers" style="display: none;">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="mb-0">Total Customers: <span id="customerCount" class="badge bg-primary">0</span></h5>
                        <small class="text-muted">Last updated: <span id="lastUpdate"></span></small>
                    </div>
                    <div id="customerList" class="row g-3"></div>
                </div>
            </div>
        </div>
        <div class="text-center mt-4">
            <p class="text-white"><small>Backend API: <code id="backendUrl" class="text-white bg-dark px-2 py-1 rounded">Loading...</code></small></p>
        </div>
    </div>
    <script>
        const BACKEND_URL = '/api/customers';
        
        // Display backend URL (showing the proxied endpoint)
        document.getElementById('backendUrl').textContent = BACKEND_URL + ' → http://10.3.0.2:8080/customers';
        
        function getInitials(name, surname) { return (name.charAt(0) + surname.charAt(0)).toUpperCase(); }
        
        function getRandomColor(name) {
            const colors = [
                'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
                'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
            ];
            return colors[name.charCodeAt(0) % colors.length];
        }
        
        function formatTime() { return new Date().toLocaleTimeString(); }
        
        async function loadCustomers() {
            const loadingEl = document.getElementById('loading');
            const errorEl = document.getElementById('error');
            const customersEl = document.getElementById('customers');
            
            loadingEl.style.display = 'block';
            errorEl.style.display = 'none';
            customersEl.style.display = 'none';
            
            try {
                const response = await fetch(BACKEND_URL);
                if (!response.ok) throw new Error(\`HTTP error! status: \${response.status}\`);
                
                const customers = await response.json();
                document.getElementById('customerCount').textContent = customers.length;
                document.getElementById('lastUpdate').textContent = formatTime();
                
                const customerList = document.getElementById('customerList');
                customerList.innerHTML = '';
                
                if (customers.length === 0) {
                    customerList.innerHTML = '<div class="col-12 text-center py-5"><p class="text-muted">No customers found.</p></div>';
                } else {
                    customers.forEach((customer, index) => {
                        const initials = getInitials(customer.name, customer.surname);
                        const bgGradient = getRandomColor(customer.name);
                        customerList.innerHTML += \`
                            <div class="col-md-6">
                                <div class="card customer-card h-100">
                                    <div class="card-body">
                                        <div class="d-flex align-items-center">
                                            <div class="customer-initials me-3" style="background: \${bgGradient}">\${initials}</div>
                                            <div class="flex-grow-1">
                                                <h5 class="card-title mb-1">\${customer.name} \${customer.surname}</h5>
                                                <p class="card-text text-muted mb-0"><small>Customer #\${index + 1}</small></p>
                                            </div>
                                            <div><span class="badge bg-success">Active</span></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        \`;
                    });
                }
                
                loadingEl.style.display = 'none';
                customersEl.style.display = 'block';
            } catch (error) {
                console.error('Error:', error);
                loadingEl.style.display = 'none';
                errorEl.style.display = 'block';
                errorEl.innerHTML = '<strong>Error loading customers!</strong><br>' + error.message;
            }
        }
        
        loadCustomers();
        setInterval(loadCustomers, 30000);
    </script>
</body>
</html>
  `);
});

// Proxy API endpoints to backend
// GET endpoint - fetch all customers
app.get('/api/customers', async (req, res) => {
  try {
    // Use node-fetch for HTTP requests (compatible with Node < 18)
    const fetch = (await import('node-fetch')).default;
    const response = await fetch('http://10.3.0.2:8080/customers');
    const data = await response.json();
    res.status(response.status).json(data);
  } catch (error) {
    console.error('Error proxying GET /api/customers:', error);
    res.status(500).json({ error: 'Failed to fetch customers: ' + error.message });
  }
});

// POST endpoint - add a new customer
app.post('/api/customers', async (req, res) => {
  try {
    const fetch = (await import('node-fetch')).default;
    const response = await fetch('http://10.3.0.2:8080/customers', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body)
    });
    const data = await response.json();
    res.status(response.status).json(data);
  } catch (error) {
    console.error('Error proxying POST /api/customers:', error);
    res.status(500).json({ error: 'Failed to add customer: ' + error.message });
  }
});

app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy' });
});

app.listen(port, '0.0.0.0', () => {
  console.log(`CRM Frontend server listening on port ${port}`);
});
APPJS

# Install application dependencies
npm install

# Start the application using pm2
pm2 start app.js --name "crm-frontend"
pm2 startup
pm2 save

