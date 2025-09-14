import axios from 'axios';
import { Product, ProductsResponse, ProductResponse } from '../types/Product';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for logging
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export class ProductService {
  static async getAllProducts(): Promise<Product[]> {
    try {
      const response = await api.get<ProductsResponse>('/products');

      if (!response.data.success) {
        throw new Error(response.data.error || 'Failed to fetch products');
      }

      return response.data.data;
    } catch (error) {
      console.error('Error fetching products:', error);
      throw error;
    }
  }

  static async getProductById(id: string): Promise<Product> {
    try {
      const response = await api.get<ProductResponse>(`/products/${id}`);

      if (!response.data.success) {
        throw new Error(response.data.error || 'Failed to fetch product');
      }

      return response.data.data;
    } catch (error) {
      console.error(`Error fetching product ${id}:`, error);
      throw error;
    }
  }

  static async searchProducts(query: string): Promise<Product[]> {
    try {
      const response = await api.get<ProductsResponse>('/search', {
        params: { q: query }
      });

      if (!response.data.success) {
        throw new Error(response.data.error || 'Failed to search products');
      }

      return response.data.data;
    } catch (error) {
      console.error(`Error searching products with query "${query}":`, error);
      throw error;
    }
  }
}

export default ProductService;
