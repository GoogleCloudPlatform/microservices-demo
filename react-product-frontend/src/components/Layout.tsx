import React from 'react';
import { Link } from 'react-router-dom';
import SearchBar from './SearchBar';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="app-layout">
      <header className="app-header">
        <div className="header-content">
          <Link to="/" className="logo">
            <h1>🛍️ Product Catalog</h1>
          </Link>
          <SearchBar />
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          {children}
        </div>
      </main>

      <footer className="app-footer">
        <div className="container">
          <p>
            © 2024 Product Catalog Demo |
            Powered by React + Vite + gRPC |
            <a
              href="https://github.com/GoogleCloudPlatform/microservices-demo"
              target="_blank"
              rel="noopener noreferrer"
            >
              Source Code
            </a>
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
