'use client';

/**
 * Error Boundary component for React error handling.
 *
 * This component wraps components to catch JavaScript errors and display
 * a fallback UI instead of crashing the entire application.
 */

import React, { ReactNode, ReactElement } from 'react';
import { AlertTriangle } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * Error Boundary component for catching and handling React errors.
 *
 * @example
 * <ErrorBoundary fallback={<ErrorFallback />}>
 *   <MyComponent />
 * </ErrorBoundary>
 */
export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error to console for debugging
    console.error('Error caught by boundary:', error, errorInfo);

    // Call optional error callback
    this.props.onError?.(error, errorInfo);
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="w-full p-4 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h2 className="font-semibold text-red-900">Something went wrong</h2>
                <p className="text-sm text-red-700 mt-1">
                  {this.state.error?.message || 'An unexpected error occurred'}
                </p>
              </div>
            </div>
          </div>
        )
      );
    }

    return this.props.children;
  }
}

/**
 * Default fallback component for error boundary.
 */
export function ErrorFallback({ error, resetError }: { error?: Error; resetError?: () => void }) {
  return (
    <div className="w-full max-w-md mx-auto p-6 bg-white rounded-lg shadow">
      <div className="flex items-center gap-3 mb-4">
        <AlertTriangle className="w-6 h-6 text-red-600" />
        <h2 className="text-lg font-semibold text-gray-900">Error</h2>
      </div>
      <p className="text-sm text-gray-600 mb-4">
        {error?.message || 'An unexpected error occurred. Please try again.'}
      </p>
      {resetError && (
        <button
          onClick={resetError}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          Try Again
        </button>
      )}
    </div>
  );
}
