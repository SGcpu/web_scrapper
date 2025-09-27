// Analysis results visualization page
import React, { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Area,
  AreaChart,
} from "recharts";
import { useAnalysis } from "../hooks/index.ts";
import { LoadingSpinner } from "./common/LoadingSpinner.tsx";
import { ErrorMessage } from "./common/ErrorMessage.tsx";
import { getSentimentColor } from "../utils/helpers.ts";
import type { AnalysisResult } from "../types";

export const AnalysisPage: React.FC = () => {
  const [selectedProductId, setSelectedProductId] = useState<number | null>(
    null
  );
  const [analysisResults, setAnalysisResults] = useState<AnalysisResult | null>(
    null
  );
  const { isLoading, error, startAnalysis } = useAnalysis();

  // Mock data for demonstration - replace with real API calls
  const mockAnalysisResult: AnalysisResult = {
    product_id: 1,
    total_reviews: 1250,
    sentiment: {
      label: "POSITIVE",
      score: 0.72,
      distribution: {
        POSITIVE: 65,
        NEGATIVE: 20,
        NEUTRAL: 15,
      },
    },
    aspects: [
      { aspect: "Quality", sentiment: "POSITIVE", score: 0.8, mentions: 450 },
      { aspect: "Price", sentiment: "NEUTRAL", score: 0.5, mentions: 320 },
      { aspect: "Shipping", sentiment: "POSITIVE", score: 0.7, mentions: 280 },
      {
        aspect: "Customer Service",
        sentiment: "NEGATIVE",
        score: 0.3,
        mentions: 150,
      },
      {
        aspect: "Packaging",
        sentiment: "POSITIVE",
        score: 0.75,
        mentions: 200,
      },
    ],
    topics: [
      {
        topic_id: 1,
        label: "Product Quality",
        keywords: ["quality", "durable", "build"],
        probability: 0.85,
        review_count: 420,
      },
      {
        topic_id: 2,
        label: "Value for Money",
        keywords: ["price", "worth", "value"],
        probability: 0.78,
        review_count: 380,
      },
      {
        topic_id: 3,
        label: "User Experience",
        keywords: ["easy", "simple", "user-friendly"],
        probability: 0.65,
        review_count: 250,
      },
    ],
    keywords: [
      "excellent",
      "quality",
      "value",
      "recommend",
      "satisfied",
      "durable",
      "easy",
      "good",
    ],
    trust_score: 0.82,
    processing_time: 45.2,
  };

  // Sample sentiment trend data
  const sentimentTrendData = [
    { date: "2024-01", sentiment: 0.65, reviews: 120 },
    { date: "2024-02", sentiment: 0.68, reviews: 145 },
    { date: "2024-03", sentiment: 0.72, reviews: 160 },
    { date: "2024-04", sentiment: 0.69, reviews: 140 },
    { date: "2024-05", sentiment: 0.74, reviews: 180 },
    { date: "2024-06", sentiment: 0.71, reviews: 155 },
  ];

  const handleAnalyzeProduct = async (productId: number) => {
    try {
      await startAnalysis(productId);
      setSelectedProductId(productId);
      // For demo purposes, set mock data
      setAnalysisResults(mockAnalysisResult);
    } catch (error) {
      console.error("Failed to start analysis:", error);
    }
  };

  const SentimentDistributionChart = ({
    data,
  }: {
    data: AnalysisResult["sentiment"]["distribution"];
  }) => {
    const chartData = [
      {
        name: "Positive",
        value: data.POSITIVE,
        color: getSentimentColor("positive"),
      },
      {
        name: "Negative",
        value: data.NEGATIVE,
        color: getSentimentColor("negative"),
      },
      {
        name: "Neutral",
        value: data.NEUTRAL,
        color: getSentimentColor("neutral"),
      },
    ];

    return (
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={120}
            paddingAngle={2}
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip formatter={(value: number) => [`${value}%`, "Percentage"]} />
        </PieChart>
      </ResponsiveContainer>
    );
  };

  const AspectSentimentChart = ({
    aspects,
  }: {
    aspects: AnalysisResult["aspects"];
  }) => {
    const chartData = aspects.map((aspect) => ({
      name: aspect.aspect,
      score: aspect.score * 100,
      mentions: aspect.mentions,
      color: getSentimentColor(aspect.score),
    }));

    return (
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={chartData}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
          <YAxis domain={[0, 100]} />
          <Tooltip
            formatter={(value: number, name: string) => [
              name === "score"
                ? `${value.toFixed(1)}%`
                : value.toLocaleString(),
              name === "score" ? "Sentiment Score" : "Mentions",
            ]}
          />
          <Bar dataKey="score" fill="#3B82F6" />
        </BarChart>
      </ResponsiveContainer>
    );
  };

  const SentimentTrendChart = ({
    data,
  }: {
    data: typeof sentimentTrendData;
  }) => {
    return (
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart
          data={data}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis
            domain={[0, 1]}
            tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
          />
          <Tooltip
            formatter={(value: number, name: string) => [
              name === "sentiment"
                ? `${(value * 100).toFixed(1)}%`
                : value.toLocaleString(),
              name === "sentiment" ? "Sentiment Score" : "Reviews",
            ]}
          />
          <Area
            type="monotone"
            dataKey="sentiment"
            stroke="#10B981"
            fill="#10B981"
            fillOpacity={0.3}
          />
        </AreaChart>
      </ResponsiveContainer>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Analysis Results</h1>
          <p className="mt-1 text-sm text-gray-500">
            AI-powered sentiment analysis and insights from product reviews
          </p>
        </div>

        {/* Quick Start Analysis */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Quick Analysis
          </h2>
          <div className="flex items-center space-x-4">
            <input
              type="number"
              placeholder="Enter Product ID"
              className="flex-1 border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              onChange={(e) =>
                setSelectedProductId(parseInt(e.target.value) || null)
              }
            />
            <button
              onClick={() =>
                selectedProductId && handleAnalyzeProduct(selectedProductId)
              }
              disabled={!selectedProductId || isLoading}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <>
                  <LoadingSpinner size="small" color="white" className="mr-2" />
                  Analyzing...
                </>
              ) : (
                "Start Analysis"
              )}
            </button>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6">
            <ErrorMessage message={error} />
          </div>
        )}

        {/* Analysis Results */}
        {analysisResults && (
          <div className="space-y-8">
            {/* Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-blue-100 rounded-md flex items-center justify-center">
                      <svg
                        className="w-5 h-5 text-blue-600"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
                        />
                      </svg>
                    </div>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">
                      Total Reviews
                    </p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {analysisResults.total_reviews.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div
                      className={`w-8 h-8 rounded-md flex items-center justify-center ${
                        analysisResults.sentiment.score > 0.6
                          ? "bg-green-100"
                          : analysisResults.sentiment.score < 0.4
                            ? "bg-red-100"
                            : "bg-yellow-100"
                      }`}
                    >
                      <div
                        className={`w-5 h-5 rounded-full ${
                          analysisResults.sentiment.score > 0.6
                            ? "bg-green-500"
                            : analysisResults.sentiment.score < 0.4
                              ? "bg-red-500"
                              : "bg-yellow-500"
                        }`}
                      />
                    </div>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">
                      Overall Sentiment
                    </p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {(analysisResults.sentiment.score * 100).toFixed(1)}%
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-purple-100 rounded-md flex items-center justify-center">
                      <svg
                        className="w-5 h-5 text-purple-600"
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
                    </div>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">
                      Trust Score
                    </p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {(analysisResults.trust_score * 100).toFixed(0)}%
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-lg shadow p-6">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <div className="w-8 h-8 bg-gray-100 rounded-md flex items-center justify-center">
                      <svg
                        className="w-5 h-5 text-gray-600"
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
                    </div>
                  </div>
                  <div className="ml-4">
                    <p className="text-sm font-medium text-gray-500">
                      Processing Time
                    </p>
                    <p className="text-2xl font-semibold text-gray-900">
                      {analysisResults.processing_time.toFixed(1)}s
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Charts Row 1 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Sentiment Distribution */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Sentiment Distribution
                </h3>
                <SentimentDistributionChart
                  data={analysisResults.sentiment.distribution}
                />
              </div>

              {/* Aspect Sentiment */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Aspect-Based Sentiment
                </h3>
                <AspectSentimentChart aspects={analysisResults.aspects} />
              </div>
            </div>

            {/* Charts Row 2 */}
            <div className="grid grid-cols-1 gap-8">
              {/* Sentiment Trend */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Sentiment Trend Over Time
                </h3>
                <SentimentTrendChart data={sentimentTrendData} />
              </div>
            </div>

            {/* Topics and Keywords */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Topics */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Key Topics
                </h3>
                <div className="space-y-4">
                  {analysisResults.topics.map((topic) => (
                    <div
                      key={topic.topic_id}
                      className="border border-gray-200 rounded-lg p-4"
                    >
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-medium text-gray-900">
                          {topic.label}
                        </h4>
                        <span className="text-sm text-gray-500">
                          {topic.review_count} reviews
                        </span>
                      </div>
                      <div className="flex flex-wrap gap-1 mb-2">
                        {topic.keywords.map((keyword, index) => (
                          <span
                            key={index}
                            className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded"
                          >
                            {keyword}
                          </span>
                        ))}
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${topic.probability * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Keywords */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Key Terms
                </h3>
                <div className="flex flex-wrap gap-2">
                  {analysisResults.keywords.map((keyword, index) => (
                    <span
                      key={index}
                      className="inline-block bg-gray-100 text-gray-800 px-3 py-1 rounded-full text-sm"
                    >
                      {keyword}
                    </span>
                  ))}
                </div>

                {/* Detailed Aspects */}
                <div className="mt-6">
                  <h4 className="font-medium text-gray-900 mb-3">
                    Aspect Details
                  </h4>
                  <div className="space-y-2">
                    {analysisResults.aspects.map((aspect, index) => (
                      <div
                        key={index}
                        className="flex justify-between items-center p-2 border border-gray-200 rounded"
                      >
                        <span className="font-medium">{aspect.aspect}</span>
                        <div className="flex items-center space-x-2">
                          <div
                            className="w-3 h-3 rounded-full"
                            style={{
                              backgroundColor: getSentimentColor(aspect.score),
                            }}
                          />
                          <span className="text-sm text-gray-600">
                            {(aspect.score * 100).toFixed(0)}% (
                            {aspect.mentions} mentions)
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* No Results State */}
        {!analysisResults && !isLoading && (
          <div className="bg-white rounded-lg shadow p-12 text-center">
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
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              No Analysis Results
            </h3>
            <p className="text-gray-500 mb-6">
              Enter a product ID above to start analyzing reviews and generate
              insights.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
