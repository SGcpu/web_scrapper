// API health indicator component
import React from "react";
import { useApiHealth } from "../../hooks";

export const ApiHealthIndicator: React.FC = () => {
  const { isHealthy, isLoading, checkHealth } = useApiHealth();

  if (isLoading) {
    return (
      <div className="flex items-center space-x-2">
        <div className="animate-pulse w-2 h-2 bg-gray-400 rounded-full"></div>
        <span className="text-sm text-gray-500">Checking...</span>
      </div>
    );
  }

  return (
    <div className="flex items-center space-x-2">
      <button
        onClick={checkHealth}
        className="flex items-center space-x-2 text-sm hover:opacity-75 transition-opacity"
        title="Click to refresh API status"
      >
        <div
          className={`w-2 h-2 rounded-full ${
            isHealthy === null
              ? "bg-gray-400"
              : isHealthy
                ? "bg-green-500"
                : "bg-red-500"
          }`}
        />
        <span
          className={`${
            isHealthy === null
              ? "text-gray-500"
              : isHealthy
                ? "text-green-600"
                : "text-red-600"
          }`}
        >
          {isHealthy === null
            ? "Unknown"
            : isHealthy
              ? "API Online"
              : "API Offline"}
        </span>
      </button>
    </div>
  );
};
