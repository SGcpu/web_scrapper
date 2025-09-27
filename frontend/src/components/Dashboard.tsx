// Dashboard component - Main overview page
import React from "react";
import { useDashboard } from "../hooks/index.ts";
import { LoadingSpinner } from "./common/LoadingSpinner.tsx";
import { ErrorMessage } from "./common/ErrorMessage.tsx";
import { DashboardStats } from "./dashboard/DashboardStats.tsx";
import { SentimentChart } from "./dashboard/SentimentChart.tsx";
import { RecentProducts } from "./dashboard/RecentProducts.tsx";
import { ApiHealthIndicator } from "./common/ApiHealthIndicator.tsx";

export const Dashboard: React.FC = () => {
  const { summary, recentProducts, isLoading, error, refresh } = useDashboard();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <ErrorMessage
          message={error}
          onRetry={refresh}
          title="Failed to load dashboard"
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Review Radar</h1>
              <p className="mt-1 text-sm text-gray-500">
                AI-powered review analysis dashboard
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={refresh}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              >
                Manual Refresh
              </button>
              <ApiHealthIndicator />
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Dashboard Stats */}
        {summary && (
          <div className="mb-8">
            <DashboardStats summary={summary} />
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Sentiment Analysis Chart */}
          {summary && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">
                Sentiment Overview
              </h2>
              {summary.sentiment_distribution ? (
                <SentimentChart data={summary.sentiment_distribution} />
              ) : (
                <div className="flex flex-col items-center justify-center p-6 text-center">
                  <div className="text-3xl font-bold mb-2">
                    {(summary.avg_sentiment * 100).toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-500">
                    Average Positive Sentiment
                  </div>
                  <p className="mt-4 text-gray-600">
                    Detailed sentiment distribution not available yet.
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Recent Products */}
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-900">
                Recent Products
              </h2>
              <button
                onClick={refresh}
                className="text-blue-600 hover:text-blue-800 text-sm font-medium"
              >
                Refresh
              </button>
            </div>
            <RecentProducts products={recentProducts} />
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Quick Actions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => (window.location.href = "/products/new")}
              className="flex items-center justify-center px-4 py-3 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                />
              </svg>
              Add New Product
            </button>
            <button
              onClick={() => (window.location.href = "/scraping")}
              className="flex items-center justify-center px-4 py-3 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
              Import Reviews
            </button>
            <button
              onClick={() => (window.location.href = "/analysis")}
              className="flex items-center justify-center px-4 py-3 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
              View Analytics
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};
