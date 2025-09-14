import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Product } from '../types/Product';
import { ProductService } from '../services/productService';
import { formatPrice, truncateText } from '../utils/formatters';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

const ProductList: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        setError(null);

        console.log('📦 Fetching products from API...');
        const data = await ProductService.getAllProducts();

        console.log(`✅ Successfully loaded ${data.length} products`);
        setProducts(data);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load products';
        console.error('❌ Error loading products:', errorMessage);
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  if (loading) {
    return <LoadingSpinner message="Loading products..." />;
  }

  if (error) {
    return (
      <ErrorMessage
        message={error}
        onRetry={() => window.location.reload()}
      />
    );
  }

  if (products.length === 0) {
    return (
      <div className="empty-state">
        <h2>No products found</h2>
        <p>The product catalog is currently empty.</p>
      </div>
    );
  }

  return (
    <div className="product-list-container">
      <div className="page-header">
        <h1>🛍️ Hot Products</h1>
        <p className="product-count">Showing {products.length} products</p>
      </div>

      <div className="product-grid">
        {products.map((product) => (
          <div key={product.id} className="product-card">
            <Link to={`/product/${product.id}`} className="product-link">
              <div className="product-image-container">
                <img
                  src={product.picture}
                  alt={product.name}
                  className="product-image"
                  onError={(e) => {
                    const target = e.target as HTMLImageElement;
                    if (!target.src.includes('placeholder-product.svg')) {
                      target.src = '/placeholder-product.svg';
                      target.onerror = null;
                    }
                  }}
                />
              </div>

              <div className="product-info">
                <h3 className="product-name">{product.name}</h3>

                <p className="product-description">
                  {truncateText(product.description, 120)}
                </p>

                <div className="product-price">
                  {formatPrice(product.priceUsd)}
                </div>

                {product.categories && product.categories.length > 0 && (
                  <div className="product-categories">
                    {product.categories.map((category) => (
                      <span key={category} className="category-tag">
                        {category}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProductList;
