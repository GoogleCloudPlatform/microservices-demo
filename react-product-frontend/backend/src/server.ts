import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import { ProductCatalogClient } from './grpc/productCatalogClient.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());

// Initialize gRPC client
const productCatalogClient = new ProductCatalogClient();

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    service: 'product-catalog-bff'
  });
});

// Get all products
app.get('/api/products', async (req, res) => {
  try {
    console.log('📦 Fetching all products from Product Catalog Service...');
    const products = await productCatalogClient.listProducts();

    console.log(`✅ Retrieved ${products.length} products`);
    res.json({
      success: true,
      data: products,
      total: products.length
    });
  } catch (error) {
    console.error('❌ Error fetching products:', error);
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      details: error
    });
  }
});

// Get product by ID
app.get('/api/products/:id', async (req, res) => {
  try {
    const { id } = req.params;
    console.log(`📦 Fetching product with ID: ${id}`);

    const product = await productCatalogClient.getProduct(id);

    console.log(`✅ Retrieved product: ${product.name}`);
    res.json({
      success: true,
      data: product
    });
  } catch (error) {
    console.error(`❌ Error fetching product ${req.params.id}:`, error);

    if (error instanceof Error && error.message.includes('NotFound')) {
      res.status(404).json({
        success: false,
        error: `Product with ID ${req.params.id} not found`
      });
    } else {
      res.status(500).json({
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      });
    }
  }
});

// Search products
app.get('/api/search', async (req, res) => {
  try {
    const { q } = req.query;

    if (!q || typeof q !== 'string') {
      return res.status(400).json({
        success: false,
        error: 'Query parameter "q" is required'
      });
    }

    console.log(`🔍 Searching products with query: "${q}"`);
    const products = await productCatalogClient.searchProducts(q);

    console.log(`✅ Found ${products.length} products`);
    res.json({
      success: true,
      data: products,
      total: products.length,
      query: q
    });
  } catch (error) {
    console.error('❌ Error searching products:', error);
    res.status(500).json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error'
    });
  }
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 BFF Server running on port ${PORT}`);
  console.log(`📡 Product Catalog Service: ${process.env.PRODUCT_CATALOG_SERVICE_ADDR || 'productcatalogservice:3550'}`);
  console.log(`🌐 CORS enabled for frontend development`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('🛑 Received SIGTERM, shutting down gracefully...');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('🛑 Received SIGINT, shutting down gracefully...');
  process.exit(0);
});
