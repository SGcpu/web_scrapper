// API connectivity test component
import React, { useEffect, useState } from "react";
import axios from "axios";

export const ApiConnectionTest: React.FC = () => {
  const [status, setStatus] = useState<"loading" | "success" | "error">(
    "loading"
  );
  const [result, setResult] = useState<{
    status?: string;
    service?: string;
  } | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    const testApi = async () => {
      try {
        console.log("Making API request to health endpoint...");
        const response = await axios.get("http://127.0.0.1:8000/health");
        console.log("Response received:", response);
        setResult(response.data);
        setStatus("success");
      } catch (error) {
        console.error("API request failed:", error);
        setStatus("error");
        if (error instanceof Error) {
          setErrorMsg(error.message);
        } else {
          setErrorMsg("Unknown error");
        }
      }
    };

    testApi();
  }, []);

  return (
    <div className="max-w-lg mx-auto my-8 p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-4">API Connection Test</h2>

      {status === "loading" && (
        <div className="flex items-center space-x-2">
          <div className="w-4 h-4 bg-blue-500 rounded-full animate-pulse"></div>
          <p>Testing connection to API...</p>
        </div>
      )}

      {status === "success" && (
        <div>
          <div className="flex items-center space-x-2 mb-4">
            <div className="w-4 h-4 bg-green-500 rounded-full"></div>
            <p className="text-green-700 font-medium">Connection successful!</p>
          </div>

          <div className="bg-gray-100 p-4 rounded">
            <pre className="whitespace-pre-wrap">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        </div>
      )}

      {status === "error" && (
        <div>
          <div className="flex items-center space-x-2 mb-4">
            <div className="w-4 h-4 bg-red-500 rounded-full"></div>
            <p className="text-red-700 font-medium">Connection failed</p>
          </div>

          <div className="bg-red-50 border border-red-200 p-4 rounded">
            <p className="text-red-600">{errorMsg}</p>
            <p className="mt-2 text-sm text-gray-600">
              Check if the backend server is running on port 8000 and that CORS
              is properly configured.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
