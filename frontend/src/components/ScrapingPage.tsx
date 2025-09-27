// Scraping management page
import React, { useState, useEffect } from "react";
import { useScraping } from "../hooks/index.ts";
import { LoadingSpinner } from "./common/LoadingSpinner.tsx";
import { ErrorMessage } from "./common/ErrorMessage.tsx";
import { isValidUrl } from "../utils/helpers.ts";
import type { ScrapeStatus } from "../types/index.ts";

export const ScrapingPage: React.FC = () => {
  const [newScrapeForm, setNewScrapeForm] = useState({
    url: "",
    maxReviews: 100,
    platform: "auto",
  });
  const [isFormValid, setIsFormValid] = useState(false);

  const {
    sessions,
    isLoading,
    error,
    startScraping,
    getSessionStatus,
    refreshSessions,
  } = useScraping();

  // Validate form
  useEffect(() => {
    setIsFormValid(
      isValidUrl(newScrapeForm.url) &&
        newScrapeForm.maxReviews > 0 &&
        newScrapeForm.maxReviews <= 1000
    );
  }, [newScrapeForm]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isFormValid) return;

    try {
      await startScraping(newScrapeForm.url, newScrapeForm.maxReviews);
      setNewScrapeForm({ url: "", maxReviews: 100, platform: "auto" });
    } catch (error) {
      console.error("Failed to start scraping:", error);
    }
  };

  const handleInputChange = (field: string, value: string | number) => {
    setNewScrapeForm((prev) => ({ ...prev, [field]: value }));
  };

  // Auto-refresh sessions every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      if (
        sessions.some((session) =>
          ["pending", "running"].includes(session.status)
        )
      ) {
        refreshSessions();
      }
    }, 5000);

    return () => clearInterval(interval);
  }, [sessions, refreshSessions]);

  const getProgressPercentage = (session: ScrapeStatus): number => {
    if (session.status === "completed") return 100;
    if (session.status === "failed") return 0;
    if (session.total_reviews_found === 0) return 0;
    return Math.round(
      (session.reviews_scraped / session.total_reviews_found) * 100
    );
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "pending":
        return (
          <svg
            className="w-5 h-5 text-yellow-500 animate-pulse"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        );
      case "running":
        return (
          <svg
            className="w-5 h-5 text-blue-500 animate-spin"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
        );
      case "completed":
        return (
          <svg
            className="w-5 h-5 text-green-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        );
      case "failed":
        return (
          <svg
            className="w-5 h-5 text-red-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        );
      default:
        return (
          <svg
            className="w-5 h-5 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Scraping Management
          </h1>
          <p className="mt-1 text-sm text-gray-500">
            Extract and manage product reviews from e-commerce platforms
          </p>
        </div>

        {/* New Scraping Form */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Start New Scraping Session
          </h2>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Product URL *
                </label>
                <input
                  type="url"
                  value={newScrapeForm.url}
                  onChange={(e) => handleInputChange("url", e.target.value)}
                  placeholder="https://www.amazon.com/dp/B08N5WRWNW"
                  className={`w-full border rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                    newScrapeForm.url && !isValidUrl(newScrapeForm.url)
                      ? "border-red-300 focus:border-red-500"
                      : "border-gray-300 focus:border-blue-500"
                  }`}
                  required
                />
                {newScrapeForm.url && !isValidUrl(newScrapeForm.url) && (
                  <p className="mt-1 text-sm text-red-600">
                    Please enter a valid URL
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Reviews
                </label>
                <input
                  type="number"
                  value={newScrapeForm.maxReviews}
                  onChange={(e) =>
                    handleInputChange(
                      "maxReviews",
                      parseInt(e.target.value) || 0
                    )
                  }
                  min="1"
                  max="1000"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  required
                />
              </div>
            </div>

            <div className="flex justify-between items-center">
              <div className="text-sm text-gray-500">
                Supported platforms: Amazon, eBay, Shopify, and generic
                e-commerce sites
              </div>
              <button
                type="submit"
                disabled={!isFormValid || isLoading}
                className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? (
                  <>
                    <LoadingSpinner
                      size="small"
                      color="white"
                      className="mr-2"
                    />
                    Starting...
                  </>
                ) : (
                  "Start Scraping"
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6">
            <ErrorMessage message={error} onRetry={refreshSessions} />
          </div>
        )}

        {/* Scraping Sessions */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-semibold text-gray-900">
                Scraping Sessions
              </h2>
              <button
                onClick={refreshSessions}
                disabled={isLoading}
                className="px-4 py-2 text-sm border border-gray-300 rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
              >
                <svg
                  className="w-4 h-4 mr-2 inline"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                  />
                </svg>
                Refresh
              </button>
            </div>
          </div>

          {sessions.length === 0 ? (
            <div className="p-12 text-center">
              <div className="text-gray-400 mb-4">
                <svg
                  className="w-16 h-16 mx-auto"
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
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                No scraping sessions
              </h3>
              <p className="text-gray-500">
                Start your first scraping session using the form above.
              </p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {sessions.map((session) => (
                <div key={session.session_id} className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(session.status)}
                      <div>
                        <h3 className="font-medium text-gray-900">
                          Session {session.session_id.slice(0, 8)}...
                        </h3>
                        <p
                          className={`text-sm capitalize ${
                            session.status === "completed"
                              ? "text-green-600"
                              : session.status === "failed"
                                ? "text-red-600"
                                : session.status === "running"
                                  ? "text-blue-600"
                                  : session.status === "pending"
                                    ? "text-yellow-600"
                                    : "text-gray-600"
                          }`}
                        >
                          {session.status}
                        </p>
                      </div>
                    </div>
                    <div className="text-right text-sm text-gray-500">
                      {/* TODO: Add timestamp from session data */}
                      Started recently
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mb-4">
                    <div className="flex justify-between text-sm text-gray-600 mb-1">
                      <span>Progress</span>
                      <span>{getProgressPercentage(session)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-300 ${
                          session.status === "completed"
                            ? "bg-green-500"
                            : session.status === "failed"
                              ? "bg-red-500"
                              : "bg-blue-500"
                        }`}
                        style={{ width: `${getProgressPercentage(session)}%` }}
                      />
                    </div>
                  </div>

                  {/* Statistics */}
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500">Found:</span>
                      <span className="ml-1 font-medium">
                        {session.total_reviews_found.toLocaleString()}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500">Scraped:</span>
                      <span className="ml-1 font-medium">
                        {session.reviews_scraped.toLocaleString()}
                      </span>
                    </div>
                    <div>
                      <span className="text-gray-500">Failed:</span>
                      <span className="ml-1 font-medium">
                        {session.reviews_failed.toLocaleString()}
                      </span>
                    </div>
                  </div>

                  {/* Error Message */}
                  {session.error_message && (
                    <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
                      <p className="text-sm text-red-800">
                        {session.error_message}
                      </p>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="mt-4 flex space-x-2">
                    <button
                      onClick={() => getSessionStatus(session.session_id)}
                      className="px-3 py-1 text-xs border border-gray-300 rounded text-gray-700 hover:bg-gray-50"
                    >
                      Refresh Status
                    </button>
                    {session.status === "completed" && (
                      <button className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700">
                        View Results
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
