import React, { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { Product } from '../types/Product';
import { ProductService } from '../services/productService';
import { formatPrice, truncateText } from '../utils/formatters';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

const SearchResults: React.FC = () => {
  const [searchParams] = useSearchParams();
  const query = searchParams.get('q') || '';

  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const searchProducts = async () => {
      if (!query.trim()) {
        setProducts([]);
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        setError(null);

        console.log(`🔍 Searching for products with query: "${query}"`);
        const data = await ProductService.searchProducts(query);

        console.log(`✅ Found ${data.length} products`);
        setProducts(data);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to search products';
        console.error('❌ Error searching products:', errorMessage);
        setError(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    searchProducts();
  }, [query]);

  if (!query.trim()) {
    return (
      <div className="empty-state">
        <h2>Search Products</h2>
        <p>Enter a search term to find products.</p>
        <Link to="/" className="btn btn-primary">
          ← View All Products
        </Link>
      </div>
    );
  }

  if (loading) {
    return <LoadingSpinner message={`Searching for "${query}"...`} />;
  }

  if (error) {
    return (
      <ErrorMessage
        message={error}
        onRetry={() => window.location.reload()}
      />
    );
  }

  return (
    <div className="search-results-container">
      <div className="page-header">
        <h1>🔍 Search Results</h1>
        <p className="search-info">
          {products.length > 0
            ? `Found ${products.length} result${products.length === 1 ? '' : 's'} for "${query}"`
            : `No results found for "${query}"`
          }
        </p>
      </div>

      {products.length === 0 ? (
        <div className="empty-state">
          <h2>No products found</h2>
          <p>Try searching with different keywords.</p>
          <div className="suggestions">
            <p><strong>Suggestions:</strong></p>
            <ul>
              <li>Check your spelling</li>
              <li>Try more general terms</li>
              <li>Try different keywords</li>
            </ul>
          </div>
          <Link to="/" className="btn btn-primary">
            ← View All Products
          </Link>
        </div>
      ) : (
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
      )}
    </div>
  );
};

export default SearchResults;
