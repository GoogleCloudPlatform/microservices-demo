const express = require('express');
const path = require('path');
const app = express();
const port = 8080;

// Serve static files
app.use(express.static('public'));

// Main route - serve the frontend
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
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 0;
        }
        .container {
            max-width: 900px;
        }
        .card {
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .card-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px 15px 0 0 !important;
            padding: 20px;
        }
        .customer-card {
            transition: transform 0.2s, box-shadow 0.2s;
            border-left: 4px solid #667eea;
        }
        .customer-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .customer-initials {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.2rem;
        }
        .badge {
            font-size: 0.9rem;
        }
        .loading {
            text-align: center;
            padding: 40px;
        }
        .spinner-border {
            width: 3rem;
            height: 3rem;
        }
        .error-message {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
        }
        .refresh-btn {
            transition: all 0.3s;
        }
        .refresh-btn:hover {
            transform: rotate(180deg);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-header">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h2 class="mb-1">
                            <i class="bi bi-people-fill"></i> CRM Customer Dashboard
                        </h2>
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
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-3 text-muted">Fetching customer data...</p>
                </div>
                <div id="error" class="error-message" style="display: none;"></div>
                <div id="customers" style="display: none;">
                    <div class="d-flex justify-content-between align-items-center mb-3">
                        <h5 class="mb-0">
                            Total Customers: <span id="customerCount" class="badge bg-primary">0</span>
                        </h5>
                        <small class="text-muted">Last updated: <span id="lastUpdate"></span></small>
                    </div>
                    <div id="customerList" class="row g-3"></div>
                </div>
            </div>
        </div>
        
        <div class="text-center mt-4">
            <p class="text-white">
                <small>Backend API: <code id="backendUrl" class="text-white bg-dark px-2 py-1 rounded">Loading...</code></small>
            </p>
        </div>
    </div>

    <script>
        const BACKEND_URL = 'http://10.3.0.4:8080/customers';
        
        // Display backend URL
        document.getElementById('backendUrl').textContent = BACKEND_URL;
        
        function getInitials(name, surname) {
            return (name.charAt(0) + surname.charAt(0)).toUpperCase();
        }
        
        function getRandomColor(name) {
            const colors = [
                'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
                'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
                'linear-gradient(135deg, #30cfd0 0%, #330867 100%)',
            ];
            const index = name.charCodeAt(0) % colors.length;
            return colors[index];
        }
        
        function formatTime() {
            return new Date().toLocaleTimeString();
        }
        
        async function loadCustomers() {
            const loadingEl = document.getElementById('loading');
            const errorEl = document.getElementById('error');
            const customersEl = document.getElementById('customers');
            
            // Show loading state
            loadingEl.style.display = 'block';
            errorEl.style.display = 'none';
            customersEl.style.display = 'none';
            
            try {
                const response = await fetch(BACKEND_URL);
                
                if (!response.ok) {
                    throw new Error(\`HTTP error! status: \${response.status}\`);
                }
                
                const customers = await response.json();
                
                // Update customer count
                document.getElementById('customerCount').textContent = customers.length;
                document.getElementById('lastUpdate').textContent = formatTime();
                
                // Render customer cards
                const customerList = document.getElementById('customerList');
                customerList.innerHTML = '';
                
                if (customers.length === 0) {
                    customerList.innerHTML = \`
                        <div class="col-12 text-center py-5">
                            <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" fill="currentColor" class="text-muted mb-3" viewBox="0 0 16 16">
                                <path d="M15 14s1 0 1-1-1-4-5-4-5 3-5 4 1 1 1 1h8zm-7.978-1A.261.261 0 0 1 7 12.996c.001-.264.167-1.03.76-1.72C8.312 10.629 9.282 10 11 10c1.717 0 2.687.63 3.24 1.276.593.69.758 1.457.76 1.72l-.008.002a.274.274 0 0 1-.014.002H7.022zM11 7a2 2 0 1 0 0-4 2 2 0 0 0 0 4zm3-2a3 3 0 1 1-6 0 3 3 0 0 1 6 0zM6.936 9.28a5.88 5.88 0 0 0-1.23-.247A7.35 7.35 0 0 0 5 9c-4 0-5 3-5 4 0 .667.333 1 1 1h4.216A2.238 2.238 0 0 1 5 13c0-1.01.377-2.042 1.09-2.904.243-.294.526-.569.846-.816zM4.92 10A5.493 5.493 0 0 0 4 13H1c0-.26.164-1.03.76-1.724.545-.636 1.492-1.256 3.16-1.275zM1.5 5.5a3 3 0 1 1 6 0 3 3 0 0 1-6 0zm3-2a2 2 0 1 0 0 4 2 2 0 0 0 0-4z"/>
                            </svg>
                            <p class="text-muted">No customers found. Add some customers to the CRM system!</p>
                        </div>
                    \`;
                } else {
                    customers.forEach((customer, index) => {
                        const initials = getInitials(customer.name, customer.surname);
                        const bgGradient = getRandomColor(customer.name);
                        
                        const card = \`
                            <div class="col-md-6">
                                <div class="card customer-card h-100">
                                    <div class="card-body">
                                        <div class="d-flex align-items-center">
                                            <div class="customer-initials me-3" style="background: \${bgGradient}">
                                                \${initials}
                                            </div>
                                            <div class="flex-grow-1">
                                                <h5 class="card-title mb-1">\${customer.name} \${customer.surname}</h5>
                                                <p class="card-text text-muted mb-0">
                                                    <small>Customer #\${index + 1}</small>
                                                </p>
                                            </div>
                                            <div>
                                                <span class="badge bg-success">Active</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        \`;
                        customerList.innerHTML += card;
                    });
                }
                
                // Show customers section
                loadingEl.style.display = 'none';
                customersEl.style.display = 'block';
                
            } catch (error) {
                console.error('Error loading customers:', error);
                loadingEl.style.display = 'none';
                errorEl.style.display = 'block';
                errorEl.innerHTML = \`
                    <strong>Error loading customers!</strong><br>
                    \${error.message}<br>
                    <small>Make sure the backend service is running at: \${BACKEND_URL}</small>
                \`;
            }
        }
        
        // Load customers on page load
        loadCustomers();
        
        // Auto-refresh every 30 seconds
        setInterval(loadCustomers, 30000);
    </script>
</body>
</html>
  `);
});

// Health check endpoint for load balancer
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy' });
});

app.listen(port, '0.0.0.0', () => {
  console.log(`CRM Frontend server listening on port ${port}`);
});

