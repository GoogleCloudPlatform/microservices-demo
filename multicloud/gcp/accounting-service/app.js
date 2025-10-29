const express = require('express');
const app = express();
const port = process.env.PORT || 8080;

// Middleware to parse JSON bodies
app.use(express.json());

// Configuration for CRM service
const CRM_SERVICE_URL = process.env.CRM_SERVICE_URL || '';

// In-memory data store with hardcoded transactions
let transactions = [
  { id: 1, item: 'Office Supplies', price: 75.50, date: '2025-07-20', customer: 'Acme Corp' },
  { id: 2, item: 'Software License', price: 299.99, date: '2025-07-21', customer: 'Tech Solutions' },
  { id: 3, item: 'Cloud Services', price: 450.00, date: '2025-07-22', customer: 'StartupXYZ' },
  { id: 4, item: 'Consulting Hours', price: 1200.00, date: '2025-07-23', customer: 'Enterprise LLC' }
];

let nextId = 5;

// Helper function to call CRM service
async function getCustomers() {
  if (!CRM_SERVICE_URL) {
    console.log('CRM service URL not configured, skipping customer check');
    return null;
  }

  try {
    console.log(`Calling CRM service at: ${CRM_SERVICE_URL}/customers`);
    const response = await fetch(`${CRM_SERVICE_URL}/customers`, {
      signal: AbortSignal.timeout(5000) // 5 second timeout
    });
    if (!response.ok) {
      throw new Error(`CRM service returned ${response.status}: ${response.statusText}`);
    }
    const data = await response.json();
    console.log(`Successfully retrieved customer data: ${data.length} customers`);
    return data;
  } catch (error) {
    console.error(`Failed to check CRM: ${error.name} - ${error.message}`);
    console.error(`Error details:`, error);
    return null;
  }
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy', service: 'accounting-service' });
});

// GET endpoint to list all transactions (with CRM customer check)
app.get('/transactions', async (req, res) => {
  console.log('GET /transactions - Returning transaction list');
  
  // Call CRM service to get customers
  const customersData = await getCustomers();
  
  // Prepare response with transactions and customer data
  const response = {
    transactions: transactions,
    crmIntegration: customersData ? {
      connected: true,
      customers: customersData,
      timestamp: new Date().toISOString()
    } : {
      connected: false,
      message: 'CRM service not available'
    },
    summary: {
      totalTransactions: transactions.length,
      totalAmount: transactions.reduce((sum, t) => sum + t.price, 0).toFixed(2)
    }
  };
  
  res.status(200).json(response);
});

// GET endpoint to get a specific transaction by ID
app.get('/transactions/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const transaction = transactions.find(t => t.id === id);
  
  if (!transaction) {
    console.log(`GET /transactions/${id} - Not found`);
    return res.status(404).json({ error: 'Transaction not found' });
  }
  
  console.log(`GET /transactions/${id} - Returning transaction: ${transaction.item}`);
  res.status(200).json(transaction);
});

// POST endpoint to add a new transaction
app.post('/transactions', (req, res) => {
  const { item, price, date, customer } = req.body;

  if (!item || typeof price !== 'number' || !date) {
    console.log('POST /transactions - Failed: Missing required fields');
    return res.status(400).json({ error: 'Item, price, and date are required' });
  }

  const newTransaction = {
    id: nextId++,
    item,
    price: parseFloat(price),
    date,
    customer: customer || 'Unknown'
  };
  
  transactions.push(newTransaction);
  
  // Cleanup: Keep only the 50 most recent transactions
  if (transactions.length > 50) {
    const removedCount = transactions.length - 50;
    transactions = transactions.slice(-50);
    console.log(`POST /transactions - Cleaned up ${removedCount} old transaction(s), keeping 50 most recent`);
  }
  
  console.log(`POST /transactions - Added new transaction: ${item} ($${price}). Total: ${transactions.length}`);
  res.status(201).json(newTransaction);
});

// PUT endpoint to update a transaction
app.put('/transactions/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const transactionIndex = transactions.findIndex(t => t.id === id);
  
  if (transactionIndex === -1) {
    console.log(`PUT /transactions/${id} - Not found`);
    return res.status(404).json({ error: 'Transaction not found' });
  }
  
  const { item, price, date, customer } = req.body;
  const updatedTransaction = {
    ...transactions[transactionIndex],
    ...(item && { item }),
    ...(price !== undefined && { price: parseFloat(price) }),
    ...(date && { date }),
    ...(customer && { customer })
  };
  
  transactions[transactionIndex] = updatedTransaction;
  console.log(`PUT /transactions/${id} - Updated transaction: ${updatedTransaction.item}`);
  res.status(200).json(updatedTransaction);
});

// DELETE endpoint to remove a transaction
app.delete('/transactions/:id', (req, res) => {
  const id = parseInt(req.params.id);
  const transactionIndex = transactions.findIndex(t => t.id === id);
  
  if (transactionIndex === -1) {
    console.log(`DELETE /transactions/${id} - Not found`);
    return res.status(404).json({ error: 'Transaction not found' });
  }
  
  const deletedTransaction = transactions.splice(transactionIndex, 1)[0];
  console.log(`DELETE /transactions/${id} - Deleted transaction: ${deletedTransaction.item}`);
  res.status(200).json({ message: 'Transaction deleted', transaction: deletedTransaction });
});

app.listen(port, '0.0.0.0', () => {
  console.log(`Accounting service listening on port ${port}`);
  console.log(`Initial transactions: ${transactions.length} transactions`);
});

