import * as grpc from '@grpc/grpc-js';
import * as protoLoader from '@grpc/proto-loader';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Types for our Product Catalog Service
export interface Money {
  currencyCode: string;
  units: number;
  nanos: number;
}

export interface Product {
  id: string;
  name: string;
  description: string;
  picture: string;
  priceUsd: Money;
  categories: string[];
}

// Raw gRPC response types (snake_case)
interface RawProduct {
  id: string;
  name: string;
  description: string;
  picture: string;
  price_usd: {
    currency_code: string;
    units: string | number;
    nanos: number;
  };
  categories: string[];
}

// Normalize function to convert snake_case to camelCase
function normalizeProduct(rawProduct: RawProduct): Product {
  return {
    id: rawProduct.id,
    name: rawProduct.name,
    description: rawProduct.description,
    picture: rawProduct.picture,
    priceUsd: {
      currencyCode: rawProduct.price_usd.currency_code,
      units: typeof rawProduct.price_usd.units === 'string'
        ? parseInt(rawProduct.price_usd.units, 10)
        : rawProduct.price_usd.units,
      nanos: rawProduct.price_usd.nanos,
    },
    categories: rawProduct.categories,
  };
}

interface RawListProductsResponse {
  products: RawProduct[];
}

interface ProductCatalogService {
  ListProducts(
    request: {},
    callback: (error: grpc.ServiceError | null, response?: RawListProductsResponse) => void
  ): void;

  GetProduct(
    request: { id: string },
    callback: (error: grpc.ServiceError | null, response?: RawProduct) => void
  ): void;

  SearchProducts(
    request: { query: string },
    callback: (error: grpc.ServiceError | null, response?: { results: RawProduct[] }) => void
  ): void;
}

export class ProductCatalogClient {
  private client: ProductCatalogService;
  private serviceAddr: string;

  constructor() {
    this.serviceAddr = process.env.PRODUCT_CATALOG_SERVICE_ADDR || 'productcatalogservice:3550';

    try {
      // Load the protobuf
      const protoPath = path.resolve(__dirname, '../../../../protos/demo.proto');
      console.log(`📋 Loading proto from: ${protoPath}`);

      const packageDefinition = protoLoader.loadSync(protoPath, {
        keepCase: true,
        longs: String,
        enums: String,
        defaults: true,
        oneofs: true
      });

      const protoDescriptor = grpc.loadPackageDefinition(packageDefinition) as any;
      const ProductCatalogService = protoDescriptor.hipstershop.ProductCatalogService;

      // Create gRPC client
      console.log(`🔌 Connecting to Product Catalog Service at: ${this.serviceAddr}`);
      this.client = new ProductCatalogService(
        this.serviceAddr,
        grpc.credentials.createInsecure()
      ) as ProductCatalogService;

      console.log('✅ gRPC client initialized successfully');
    } catch (error) {
      console.error('❌ Failed to initialize gRPC client:', error);
      throw error;
    }
  }

  async listProducts(): Promise<Product[]> {
    return new Promise((resolve, reject) => {
      this.client.ListProducts({}, (error, response) => {
        if (error) {
          console.error('gRPC ListProducts error:', error);
          reject(error);
          return;
        }

        if (!response || !response.products) {
          reject(new Error('Invalid response from Product Catalog Service'));
          return;
        }

        resolve(response.products.map(normalizeProduct));
      });
    });
  }

  async getProduct(id: string): Promise<Product> {
    return new Promise((resolve, reject) => {
      this.client.GetProduct({ id }, (error, response) => {
        if (error) {
          console.error(`gRPC GetProduct error for ID ${id}:`, error);
          reject(error);
          return;
        }

        if (!response) {
          reject(new Error('Invalid response from Product Catalog Service'));
          return;
        }

        resolve(normalizeProduct(response));
      });
    });
  }

  async searchProducts(query: string): Promise<Product[]> {
    return new Promise((resolve, reject) => {
      this.client.SearchProducts({ query }, (error, response) => {
        if (error) {
          console.error(`gRPC SearchProducts error for query "${query}":`, error);
          reject(error);
          return;
        }

        if (!response || !response.results) {
          reject(new Error('Invalid response from Product Catalog Service'));
          return;
        }

        resolve(response.results.map(normalizeProduct));
      });
    });
  }
}
