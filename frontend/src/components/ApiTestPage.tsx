// Comprehensive API Integration Test
import React, { useState, useEffect } from "react";

interface TestResult {
  status: number | string;
  success: boolean;
  data?: unknown;
  error?: string;
}

export const ApiTestPage: React.FC = () => {
  const [results, setResults] = useState<Record<string, TestResult>>({});
  const [isLoading, setIsLoading] = useState(false);

  const testEndpoints = async () => {
    setIsLoading(true);
    const endpoints = [
      { name: "Health Check", url: "/health" },
      { name: "Dashboard Summary", url: "/api/dashboard/summary" },
      { name: "Recent Products", url: "/api/products/recent?limit=5" },
      { name: "All Products", url: "/api/products?limit=10" },
    ];

    const testResults: Record<string, TestResult> = {};

    for (const endpoint of endpoints) {
      try {
        const response = await fetch(`http://127.0.0.1:8000${endpoint.url}`);
        const data = await response.json();
        testResults[endpoint.name] = {
          status: response.status,
          success: response.ok,
          data: data,
        };
      } catch (error) {
        testResults[endpoint.name] = {
          status: "ERROR",
          success: false,
          error: error instanceof Error ? error.message : "Unknown error",
        };
      }
    }

    setResults(testResults);
    setIsLoading(false);
  };

  useEffect(() => {
    testEndpoints();
  }, []);

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">
            API Integration Test
          </h1>
          <button
            onClick={testEndpoints}
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? "Testing..." : "Run Tests"}
          </button>
        </div>

        <div className="space-y-4">
          {Object.entries(results).map(([name, result]) => (
            <div
              key={name}
              className={`border rounded-lg p-4 ${
                result.success
                  ? "border-green-200 bg-green-50"
                  : "border-red-200 bg-red-50"
              }`}
            >
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-semibold">{name}</h3>
                <span
                  className={`px-2 py-1 rounded text-sm ${
                    result.success
                      ? "bg-green-100 text-green-800"
                      : "bg-red-100 text-red-800"
                  }`}
                >
                  {result.status}
                </span>
              </div>
              <pre className="text-sm overflow-x-auto bg-white p-2 rounded border">
                {JSON.stringify(result.data || result.error, null, 2)}
              </pre>
            </div>
          ))}
        </div>

        {Object.keys(results).length === 0 && !isLoading && (
          <div className="text-center text-gray-500 py-8">
            No test results yet. Click "Run Tests" to start.
          </div>
        )}
      </div>
    </div>
  );
};
