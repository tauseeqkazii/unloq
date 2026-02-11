import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { ChartData } from "../types";

export function ROIChart({ data }: { data: ChartData[] }) {
  // Tranform data for Recharts if needed, or mapped directly
  const chartData = data.map((d) => ({
    ...d,
    return: d.return_value,
  }));

  return (
    <div className="h-[300px] w-full mt-4">
      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-4">
        Impact ROI Analysis
      </h3>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={chartData}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            vertical={false}
            stroke="#E5E7EB"
          />
          <XAxis
            dataKey="name"
            tick={{ fontSize: 12, fill: "#6B7280" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 12, fill: "#6B7280" }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(value) => `$${value}`}
          />
          <Tooltip
            cursor={{ fill: "#F3F4F6" }}
            contentStyle={{
              borderRadius: "8px",
              border: "none",
              boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
            }}
          />
          <Bar
            dataKey="investment"
            name="Investment"
            fill="#E5E7EB"
            radius={[4, 4, 0, 0]}
          />
          <Bar
            dataKey="return"
            name="Projected Return"
            fill="#4F46E5"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
