#!/bin/bash
set -x
exec > >(tee /var/log/startup-script.log|logger -t startup-script -s 2>/dev/console) 2>&1

echo "Starting startup script execution"

# Install Node.js and npm (Node.js 20.x)
apt-get update
apt-get install -y ca-certificates curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list
apt-get update
apt-get install -y nodejs

echo "Node.js installation complete"

# Create application directory
mkdir -p /srv/furniture-app
cd /srv/furniture-app

# Initialize npm and install Express.js
npm init -y
npm install express

echo "NPM initialization and Express installation complete"

# Create the application file (index.js)
cat << 'EOF' > /srv/furniture-app/index.js
const express = require('express');
const app = express();
const port = 3000;

app.use(express.json());

let furnitureStock = {
    chairs: 100,
    tables: 35,
    sofa: 10
};

const initialStock = {
    chairs: 100,
    tables: 35,
    sofa: 10
};

// GET /furniture - List all items and quantities
app.get('/furniture', (req, res) => {
    console.log('GET /furniture called');
    res.json(furnitureStock);
});

// POST /book - Book an item
app.post('/book', (req, res) => {
    const { item, quantity } = req.body;
    console.log(`POST /book called with item: ${item}, quantity: ${quantity}`);
    if (!item || typeof quantity !== 'number' || !Number.isInteger(quantity) || quantity <= 0) {
        return res.status(400).send({ message: 'Invalid request. Provide item name and a positive integer quantity.' });
    }
    const lowerItem = item.toLowerCase();

    if (furnitureStock.hasOwnProperty(lowerItem)) {
        if (furnitureStock[lowerItem] >= quantity) {
            furnitureStock[lowerItem] -= quantity;
            console.log(`Booked ${quantity} ${lowerItem}(s). Remaining: ${furnitureStock[lowerItem]}`);
            res.status(200).send({ message: `Successfully booked ${quantity} ${lowerItem}(s).`, data: furnitureStock });
        } else {
            console.log(`Not enough stock for ${lowerItem}. Available: ${furnitureStock[lowerItem]}`);
            res.status(400).send({ message: `Not enough ${lowerItem} in stock. Available: ${furnitureStock[lowerItem]}` });
        }
    } else {
        console.log(`Item "${lowerItem}" not found`);
        res.status(404).send({ message: `Item "${lowerItem}" not found.` });
    }
});

// POST /replenish - Replenish an item to its initial stock if stock is 0
app.post('/replenish', (req, res) => {
    const { item } = req.body;
    console.log(`POST /replenish called with item: ${item}`);
    if (!item) {
        return res.status(400).send({ message: 'Invalid request. Provide item name.' });
    }
    const lowerItem = item.toLowerCase();

    if (furnitureStock.hasOwnProperty(lowerItem)) {
        if (furnitureStock[lowerItem] === 0) {
            furnitureStock[lowerItem] = initialStock[lowerItem];
            console.log(`${lowerItem} replenished to ${initialStock[lowerItem]}`);
            res.status(200).send({ message: `${lowerItem} replenished to ${initialStock[lowerItem]}.`, data: furnitureStock });
        } else {
            console.log(`${lowerItem} stock is not 0. Current: ${furnitureStock[lowerItem]}`);
            res.status(400).send({ message: `${lowerItem} stock is not 0. Current stock: ${furnitureStock[lowerItem]}` });
        }
    } else {
        console.log(`Item "${lowerItem}" not found for replenish`);
        res.status(404).send({ message: `Item "${lowerItem}" not found.` });
    }
});

app.listen(port, () => {
    console.log(`Furniture app listening on http://localhost:${port}`);
});
EOF

echo "Application file created"

# Create systemd service file
cat << EOF > /etc/systemd/system/furniture.service
[Unit]
Description=Furniture Node.js Service
After=network.target

[Service]
Type=simple
User=nobody
Group=nogroup
WorkingDirectory=/srv/furniture-app
ExecStart=/usr/bin/node /srv/furniture-app/index.js
Restart=on-failure
RestartSec=5
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=furniture-app

[Install]
WantedBy=multi-user.target
EOF

echo "Systemd service file created"

# Enable and start the service
systemctl daemon-reload
systemctl enable furniture.service
systemctl start furniture.service

echo "Furniture service started and enabled"
echo "Startup script finished"