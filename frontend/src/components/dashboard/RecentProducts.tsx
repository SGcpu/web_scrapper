// Recent products component
import React from "react";
import type { ProductSummary } from "../../types";
import { formatDate, getPlatformIcon } from "../../utils/helpers";

interface RecentProductsProps {
  products: ProductSummary[];
}

export const RecentProducts: React.FC<RecentProductsProps> = ({ products }) => {
  if (products.length === 0) {
    return (
      <div className="flex items-center justify-center h-32">
        <div className="text-center">
          <div className="text-gray-400 mb-2">
            <svg
              className="w-8 h-8 mx-auto"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"
              />
            </svg>
          </div>
          <p className="text-gray-500 text-sm">No products found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4 max-h-96 overflow-y-auto">
      {products.map((product) => (
        <div
          key={product.id}
          className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <div className="flex items-center space-x-3 flex-1 min-w-0">
            <div className="flex-shrink-0">
              {getPlatformIcon(product.platform)}
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-medium text-gray-900 truncate">
                {product.name}
              </h3>
              <div className="flex items-center space-x-2 mt-1">
                <span className="text-xs text-gray-500 capitalize">
                  {product.platform}
                </span>
                <span className="text-xs text-gray-400">•</span>
                <span className="text-xs text-gray-500">
                  {product.total_reviews.toLocaleString()} reviews
                </span>
                {product.avg_rating && (
                  <>
                    <span className="text-xs text-gray-400">•</span>
                    <div className="flex items-center">
                      <svg
                        className="w-3 h-3 text-yellow-400 mr-1"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.518 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                      </svg>
                      <span className="text-xs text-gray-600">
                        {product.avg_rating.toFixed(1)}
                      </span>
                    </div>
                  </>
                )}
              </div>
              {product.last_analyzed && (
                <div className="mt-1">
                  <span className="text-xs text-gray-400">
                    Last analyzed: {formatDate(product.last_analyzed)}
                  </span>
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {product.sentiment_score !== undefined && (
              <div className="text-center">
                <div className="text-xs text-gray-500">Sentiment</div>
                <div
                  className={`text-sm font-medium ${
                    product.sentiment_score > 0.6
                      ? "text-green-600"
                      : product.sentiment_score < 0.4
                        ? "text-red-600"
                        : "text-yellow-600"
                  }`}
                >
                  {(product.sentiment_score * 100).toFixed(0)}%
                </div>
              </div>
            )}

            <button
              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              onClick={() => {
                // TODO: Navigate to product details
                console.log("Navigate to product:", product.id);
              }}
            >
              View
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};
