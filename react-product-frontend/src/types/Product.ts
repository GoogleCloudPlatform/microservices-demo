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

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  total?: number;
  query?: string;
  error?: string;
}

export interface ProductsResponse {
  success: boolean;
  data: Product[];
  total: number;
}

export interface ProductResponse {
  success: boolean;
  data: Product;
}
