// Sentiment chart component using Recharts
import React from "react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Legend,
  Tooltip,
} from "recharts";
import { getSentimentColor } from "../../utils/helpers";

interface SentimentChartProps {
  data: {
    positive: number;
    negative: number;
    neutral: number;
  };
}

export const SentimentChart: React.FC<SentimentChartProps> = ({ data }) => {
  const chartData = [
    {
      name: "Positive",
      value: data.positive,
      color: getSentimentColor("positive"),
    },
    {
      name: "Negative",
      value: data.negative,
      color: getSentimentColor("negative"),
    },
    {
      name: "Neutral",
      value: data.neutral,
      color: getSentimentColor("neutral"),
    },
  ].filter((item) => item.value > 0); // Only show segments with data

  interface TooltipPayload {
    name: string;
    value: number;
    payload: {
      color: string;
      name: string;
      value: number;
    };
  }

  interface LegendPayload {
    value: string;
    color: string;
    payload: {
      value: number;
    };
  }

  const CustomTooltip = ({
    active,
    payload,
  }: {
    active?: boolean;
    payload?: TooltipPayload[];
  }) => {
    if (active && payload && payload.length) {
      const data = payload[0];
      const total = chartData.reduce((sum, item) => sum + item.value, 0);
      const percentage =
        total > 0 ? ((data.value / total) * 100).toFixed(1) : "0";

      return (
        <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
          <p className="font-medium" style={{ color: data.payload.color }}>
            {data.name}
          </p>
          <p className="text-sm text-gray-600">
            Count: {data.value.toLocaleString()}
          </p>
          <p className="text-sm text-gray-600">Percentage: {percentage}%</p>
        </div>
      );
    }
    return null;
  };

  const CustomLegend = ({ payload }: { payload?: LegendPayload[] }) => {
    if (!payload) return null;

    return (
      <ul className="flex justify-center space-x-4 mt-4">
        {payload.map((entry: LegendPayload, index: number) => (
          <li key={index} className="flex items-center">
            <span
              className="w-3 h-3 rounded-full mr-2"
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-sm text-gray-600">
              {entry.value}: {entry.payload.value.toLocaleString()}
            </span>
          </li>
        ))}
      </ul>
    );
  };

  if (chartData.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="text-gray-400 mb-2">
            <svg
              className="w-12 h-12 mx-auto"
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
          <p className="text-gray-500 text-sm">No sentiment data available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={40}
            outerRadius={80}
            paddingAngle={2}
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend content={<CustomLegend />} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
