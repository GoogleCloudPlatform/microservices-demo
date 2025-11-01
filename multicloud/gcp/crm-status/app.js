const express = require('express');
const app = express();
const port = 80;

const BACKEND_URL = 'http://10.3.0.2:8080/customers';

app.get('/', (req, res) => {
  res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CRM Status Monitor</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            min-height: 100vh;
            padding: 40px 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .container {
            max-width: 800px;
        }
        .status-card {
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            background: white;
        }
        .card-header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            border-radius: 15px 15px 0 0 !important;
            padding: 25px;
        }
        .status-indicator {
            width: 20px;
            height: 20px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 10px;
            animation: pulse 2s infinite;
        }
        .status-up {
            background-color: #2ecc71;
            box-shadow: 0 0 10px #2ecc71;
        }
        .status-down {
            background-color: #e74c3c;
            box-shadow: 0 0 10px #e74c3c;
        }
        .status-checking {
            background-color: #f39c12;
            box-shadow: 0 0 10px #f39c12;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .metric-card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin: 10px 0;
            border-left: 4px solid #3498db;
        }
        .metric-label {
            font-size: 0.9rem;
            color: #7f8c8d;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
            color: #2c3e50;
            margin-top: 5px;
        }
        .btn-check {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            border: none;
            padding: 12px 30px;
            font-size: 1.1rem;
            transition: all 0.3s;
            display: inline-block !important;
            visibility: visible !important;
            opacity: 1 !important;
            z-index: 9999 !important;
            position: relative !important;
            color: white !important;
            cursor: pointer !important;
            pointer-events: auto !important;
        }
        .btn-check:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
        }
        #statusDisplay {
            pointer-events: auto !important;
        }
        .card-body {
            pointer-events: auto !important;
        }
        .endpoint-info {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
        }
        .loading {
            text-align: center;
            padding: 20px;
        }
        .spinner-border {
            width: 2rem;
            height: 2rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="status-card">
            <div class="card-header">
                <h2 class="mb-2">
                    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="currentColor" class="bi bi-activity" viewBox="0 0 16 16" style="vertical-align: middle; margin-right: 10px;">
                        <path fill-rule="evenodd" d="M6 2a.5.5 0 0 1 .47.33L10 12.036l1.53-4.208A.5.5 0 0 1 12 7.5h3.5a.5.5 0 0 1 0 1h-3.15l-1.88 5.17a.5.5 0 0 1-.94.02L6 3.964 4.47 8.171A.5.5 0 0 1 4 8.5H.5a.5.5 0 0 1 0-1h3.15l1.88-5.17A.5.5 0 0 1 6 2Z"/>
                    </svg>
                    CRM Status Monitor
                </h2>
                <p class="mb-0 opacity-75">Real-time health monitoring of CRM backend service</p>
            </div>
            <div class="card-body p-4">
                <div id="statusDisplay">
                    <div class="text-center py-4">
                        <p class="text-muted">Click "Check Status" to monitor the CRM backend service</p>
                        <button onclick="checkStatus()" class="btn btn-primary btn-check">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16" style="vertical-align: middle; margin-right: 5px;">
                                <path d="M8 15A7 7 0 1 1 8 1a7 7 0 0 1 0 14zm0 1A8 8 0 1 0 8 0a8 8 0 0 0 0 16z"/>
                                <path d="M10.97 4.97a.235.235 0 0 0-.02.022L7.477 9.417 5.384 7.323a.75.75 0 0 0-1.06 1.06L6.97 11.03a.75.75 0 0 0 1.079-.02l3.992-4.99a.75.75 0 0 0-1.071-1.05z"/>
                            </svg>
                            Check Status
                        </button>
                    </div>
                </div>

                <div id="loading" class="loading" style="display: none;">
                    <div class="spinner-border text-primary" role="status"></div>
                    <p class="mt-3 text-muted">Checking backend status...</p>
                </div>

                <div id="results" style="display: none;">
                    <div class="text-center mb-4">
                        <h4>
                            <span id="statusIndicator" class="status-indicator status-checking"></span>
                            <span id="statusText">Checking...</span>
                        </h4>
                    </div>

                    <div class="row">
                        <div class="col-md-4">
                            <div class="metric-card">
                                <div class="metric-label">HTTP Status</div>
                                <div class="metric-value" id="httpStatus">-</div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="metric-card">
                                <div class="metric-label">Response Time</div>
                                <div class="metric-value" id="responseTime">-</div>
                            </div>
                        </div>
                        <div class="col-md-4">
                            <div class="metric-card">
                                <div class="metric-label">Customers</div>
                                <div class="metric-value" id="customerCount">-</div>
                            </div>
                        </div>
                    </div>

                    <div class="mt-4">
                        <div class="metric-card">
                            <div class="metric-label">Last Check</div>
                            <div style="font-size: 1.2rem; color: #2c3e50; margin-top: 5px;" id="lastCheck">-</div>
                        </div>
                    </div>

                    <div class="text-center mt-4">
                        <button onclick="checkStatus()" class="btn btn-primary btn-check">
                            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" fill="currentColor" viewBox="0 0 16 16" style="vertical-align: middle; margin-right: 5px;">
                                <path fill-rule="evenodd" d="M8 3a5 5 0 1 0 4.546 2.914.5.5 0 0 1 .908-.417A6 6 0 1 1 8 2v1z"/>
                                <path d="M8 4.466V.534a.25.25 0 0 1 .41-.192l2.36 1.966c.12.1.12.284 0 .384L8.41 4.658A.25.25 0 0 1 8 4.466z"/>
                            </svg>
                            Refresh Status
                        </button>
                    </div>
                </div>

                <div class="mt-4 pt-4 border-top">
                    <h6 class="text-muted mb-3">Monitored Endpoint</h6>
                    <div class="endpoint-info">
                        ${BACKEND_URL}
                    </div>
                </div>
            </div>
        </div>

        <div class="text-center mt-4">
            <p class="text-white-50">
                <small>CRM Status Monitor • Direct VM-to-VM Communication</small>
            </p>
        </div>
    </div>

    <script>
        async function checkStatus() {
            const loadingEl = document.getElementById('loading');
            const statusDisplayEl = document.getElementById('statusDisplay');
            const resultsEl = document.getElementById('results');
            
            statusDisplayEl.style.display = 'none';
            loadingEl.style.display = 'block';
            resultsEl.style.display = 'none';

            const startTime = performance.now();
            
            try {
                const response = await fetch('${BACKEND_URL}');
                const endTime = performance.now();
                const responseTime = Math.round(endTime - startTime);

                const statusIndicator = document.getElementById('statusIndicator');
                const statusText = document.getElementById('statusText');
                const httpStatus = document.getElementById('httpStatus');
                const responseTimeEl = document.getElementById('responseTime');
                const customerCount = document.getElementById('customerCount');
                const lastCheck = document.getElementById('lastCheck');

                if (response.ok) {
                    const data = await response.json();
                    
                    statusIndicator.className = 'status-indicator status-up';
                    statusText.textContent = 'Service Operational';
                    statusText.style.color = '#2ecc71';
                    
                    httpStatus.textContent = response.status;
                    httpStatus.style.color = '#2ecc71';
                    
                    responseTimeEl.textContent = responseTime + ' ms';
                    responseTimeEl.style.color = responseTime < 100 ? '#2ecc71' : responseTime < 300 ? '#f39c12' : '#e74c3c';
                    
                    customerCount.textContent = data.length || 0;
                    customerCount.style.color = '#3498db';
                } else {
                    statusIndicator.className = 'status-indicator status-down';
                    statusText.textContent = 'Service Degraded';
                    statusText.style.color = '#e74c3c';
                    
                    httpStatus.textContent = response.status;
                    httpStatus.style.color = '#e74c3c';
                    
                    responseTimeEl.textContent = responseTime + ' ms';
                    customerCount.textContent = 'N/A';
                }

                lastCheck.textContent = new Date().toLocaleString();

            } catch (error) {
                const statusIndicator = document.getElementById('statusIndicator');
                const statusText = document.getElementById('statusText');
                const httpStatus = document.getElementById('httpStatus');
                const responseTimeEl = document.getElementById('responseTime');
                const customerCount = document.getElementById('customerCount');
                const lastCheck = document.getElementById('lastCheck');

                statusIndicator.className = 'status-indicator status-down';
                statusText.textContent = 'Service Unavailable';
                statusText.style.color = '#e74c3c';
                
                httpStatus.textContent = 'Error';
                httpStatus.style.color = '#e74c3c';
                
                responseTimeEl.textContent = 'Timeout';
                responseTimeEl.style.color = '#e74c3c';
                
                customerCount.textContent = 'N/A';
                
                lastCheck.textContent = new Date().toLocaleString() + ' (Failed: ' + error.message + ')';
            }

            loadingEl.style.display = 'none';
            resultsEl.style.display = 'block';
        }
    </script>
</body>
</html>
  `);
});

app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy' });
});

app.listen(port, '0.0.0.0', () => {
  console.log(`CRM Status Monitor listening on port ${port}`);
});

