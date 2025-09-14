import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Product } from '../types/Product';
import { ProductService } from '../services/productService';
import { formatPrice } from '../utils/formatters';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

const ProductDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [product, setProduct] = useState<Product | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProduct = async () => {
      if (!id) {
        setError('Product ID is required');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        console.log(`📦 Fetching product details for ID: ${id}`);
        const data = await ProductService.getProductById(id);

        console.log(`✅ Successfully loaded product: ${data.name}`);
        setProduct(data);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to load product';
        console.error('❌ Error loading product:', errorMessage);
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [id]);

  if (loading) {
    return <LoadingSpinner message="Loading product details..." />;
  }

  if (error) {
    return (
      <ErrorMessage
        message={error}
        onRetry={() => window.location.reload()}
      />
    );
  }

  if (!product) {
    return (
      <div className="empty-state">
        <h2>Product not found</h2>
        <p>The requested product could not be found.</p>
        <Link to="/" className="btn btn-primary">
          ← Back to Products
        </Link>
      </div>
    );
  }

  return (
    <div className="product-detail-container">
      <div className="breadcrumb">
        <Link to="/" className="breadcrumb-link">Products</Link>
        <span className="breadcrumb-separator">›</span>
        <span className="breadcrumb-current">{product.name}</span>
      </div>

      <div className="product-detail">
        <div className="product-detail-image">
          <img
            src={product.picture}
            alt={product.name}
            className="detail-image"
            onError={(e) => {
              const target = e.target as HTMLImageElement;
              if (!target.src.includes('placeholder-product.svg')) {
                target.src = '/placeholder-product.svg';
                target.onerror = null;
              }
            }}
          />
        </div>

        <div className="product-detail-info">
          <h1 className="product-title">{product.name}</h1>

          <div className="product-price-large">
            {formatPrice(product.priceUsd)}
          </div>

          <div className="product-description-full">
            <h3>Description</h3>
            <p>{product.description}</p>
          </div>

          {product.categories && product.categories.length > 0 && (
            <div className="product-categories-detail">
              <h3>Categories</h3>
              <div className="categories-list">
                {product.categories.map((category) => (
                  <span key={category} className="category-tag-large">
                    {category}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div className="product-meta">
            <div className="meta-item">
              <strong>Product ID:</strong> {product.id}
            </div>
            <div className="meta-item">
              <strong>Currency:</strong> {product.priceUsd.currencyCode}
            </div>
          </div>

          <div className="product-actions">
            <button className="btn btn-primary btn-large">
              🛒 Add to Cart
            </button>
            <Link to="/" className="btn btn-secondary">
              ← Back to Products
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductDetail;
