import React from 'react';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  showRetry?: boolean;
}

const ErrorMessage: React.FC<ErrorMessageProps> = ({
  message,
  onRetry,
  showRetry = true
}) => {
  return (
    <div className="error-container">
      <div className="error-content">
        <div className="error-icon">❌</div>
        <h2>Oops! Something went wrong</h2>
        <p className="error-message">{message}</p>

        {showRetry && onRetry && (
          <button onClick={onRetry} className="btn btn-primary">
            🔄 Try Again
          </button>
        )}

        <div className="error-help">
          <p>If the problem persists, please:</p>
          <ul>
            <li>Check your internet connection</li>
            <li>Refresh the page</li>
            <li>Contact support if needed</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default ErrorMessage;
