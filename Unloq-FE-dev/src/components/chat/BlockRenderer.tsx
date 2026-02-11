import {
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  Legend,
  CartesianGrid,
} from "recharts";
import {
  ArrowUpRight,
  ArrowDownRight,
  Lightbulb,
  Workflow,
} from "lucide-react";

import type { ChatAction } from "../../types";

export interface Block {
  type: "summary" | "metrics" | "chart" | "recommendation" | "flow";
  text?: string;
  title?: string;
  items?: { label: string; value: string; change: string | null }[];
  data?: Record<string, unknown>[];
  chartType?: "area" | "bar" | "pie";
  unit?: string;
  color?: "rose" | "emerald" | "indigo" | "amber";
  steps?: { step: number; label: string; status: string }[];
  actions?: ChatAction[];
}

const COLORS = {
  rose: "#f43f5e",
  emerald: "#10b981",
  indigo: "#6366f1",
  amber: "#f59e0b",
  slate: "#64748b",
};

interface RendererProps {
  blocks: Block[];
  onAction?: (action: ChatAction) => void;
}

export function BlockRenderer({ blocks }: RendererProps) {
  if (!blocks || !Array.isArray(blocks)) return null;

  return (
    <div className="space-y-6 w-full animate-in fade-in duration-500">
      {blocks.map((block, idx) => {
        switch (block.type) {
          case "summary":
            return (
              <div
                key={idx}
                className="bg-slate-50 dark:bg-slate-900/50 p-5 rounded-xl border border-slate-100 dark:border-slate-800"
              >
                <div className="prose prose-sm dark:prose-invert max-w-none text-slate-700 dark:text-slate-300 leading-relaxed whitespace-pre-wrap">
                  {block.text}
                </div>
              </div>
            );

          case "metrics":
            return (
              <div
                key={idx}
                className="grid grid-cols-1 sm:grid-cols-3 gap-3 my-4"
              >
                {block.items?.map((item, i) => {
                  const changeText = item.change || "";
                  const isNegative =
                    changeText.includes("-") ||
                    changeText.toLowerCase().includes("down");

                  return (
                    <div
                      key={i}
                      className="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm"
                    >
                      <div className="text-[10px] uppercase tracking-wider text-slate-500 font-semibold">
                        {item.label}
                      </div>
                      <div className="text-xl font-bold text-slate-900 dark:text-white mt-1">
                        {item.value}
                      </div>
                      <div
                        className={`text-xs flex items-center mt-2 font-medium ${
                          isNegative ? "text-rose-600" : "text-emerald-600"
                        }`}
                      >
                        {isNegative ? (
                          <ArrowDownRight className="h-3 w-3 mr-1" />
                        ) : (
                          <ArrowUpRight className="h-3 w-3 mr-1" />
                        )}
                        {changeText}
                      </div>
                    </div>
                  );
                })}
              </div>
            );

          case "chart": {
            const chartColor =
              COLORS[(block.color as keyof typeof COLORS) || "indigo"];
            const rawData = block.data || [];
            const hasData = rawData.length > 0;

            // 1. Sanitize Data (Ensure value is number)
            const cleanData = rawData.map((d) => ({
              ...d,
              value:
                typeof d.value === "string"
                  ? parseFloat(d.value.replace(/[^0-9.-]/g, ""))
                  : d.value,
            }));

            // 2. Auto-detect X-Axis Key (ts, date, name, label)
            const firstItem = cleanData[0] || {};
            const xAxisKey =
              Object.keys(firstItem).find((k) =>
                ["ts", "date", "name", "label", "month"].includes(k)
              ) || "name";

            return (
              <div
                key={idx}
                className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-5 my-4 shadow-sm"
              >
                <div className="flex justify-between items-center mb-6">
                  <div className="text-xs font-bold text-slate-500 uppercase tracking-wide">
                    {block.title}
                  </div>
                  {block.unit && (
                    <div className="text-[10px] font-mono text-slate-500 bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">
                      {block.unit}
                    </div>
                  )}
                </div>

                <div
                  style={{ width: "100%", height: "300px", minHeight: "300px" }}
                >
                  {hasData ? (
                    <ResponsiveContainer width="100%" height="100%">
                      {block.chartType === "bar" ? (
                        <BarChart
                          data={cleanData}
                          margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
                        >
                          <CartesianGrid
                            strokeDasharray="3 3"
                            vertical={false}
                            stroke="#e2e8f0"
                            opacity={0.5}
                          />
                          <XAxis
                            dataKey={xAxisKey}
                            tick={{ fontSize: 10, fill: "#94a3b8" }}
                            axisLine={false}
                            tickLine={false}
                            interval="preserveStartEnd"
                          />
                          <YAxis
                            tick={{ fontSize: 10, fill: "#94a3b8" }}
                            axisLine={false}
                            tickLine={false}
                          />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: "#1e293b",
                              border: "none",
                              borderRadius: "8px",
                              color: "#fff",
                              fontSize: "12px",
                            }}
                            cursor={{ fill: "rgba(255,255,255,0.05)" }}
                          />
                          <Bar
                            dataKey="value"
                            fill={chartColor}
                            radius={[4, 4, 0, 0]}
                            animationDuration={1500}
                          />
                        </BarChart>
                      ) : block.chartType === "pie" ? (
                        <PieChart>
                          <Pie
                            data={cleanData}
                            innerRadius={60}
                            outerRadius={80}
                            paddingAngle={5}
                            dataKey="value"
                            nameKey={xAxisKey} // Use detected key for names
                          >
                            {cleanData.map((_, index) => (
                              <Cell
                                key={`cell-${index}`}
                                fill={Object.values(COLORS)[index % 5]}
                              />
                            ))}
                          </Pie>
                          <Tooltip
                            contentStyle={{
                              backgroundColor: "#1e293b",
                              border: "none",
                              borderRadius: "8px",
                              color: "#fff",
                            }}
                          />
                          <Legend
                            verticalAlign="bottom"
                            height={36}
                            iconType="circle"
                            formatter={(value) => (
                              <span className="text-slate-500 text-xs">
                                {value}
                              </span>
                            )}
                          />
                        </PieChart>
                      ) : (
                        <AreaChart
                          data={cleanData}
                          margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
                        >
                          <defs>
                            <linearGradient
                              id={`grad-${idx}`}
                              x1="0"
                              y1="0"
                              x2="0"
                              y2="1"
                            >
                              <stop
                                offset="5%"
                                stopColor={chartColor}
                                stopOpacity={0.2}
                              />
                              <stop
                                offset="95%"
                                stopColor={chartColor}
                                stopOpacity={0}
                              />
                            </linearGradient>
                          </defs>
                          <CartesianGrid
                            strokeDasharray="3 3"
                            vertical={false}
                            stroke="#e2e8f0"
                            opacity={0.5}
                          />
                          <XAxis
                            dataKey={xAxisKey}
                            tick={{ fontSize: 10, fill: "#94a3b8" }}
                            axisLine={false}
                            tickLine={false}
                            minTickGap={30}
                            tickFormatter={(v) => {
                              // Try to format dates like '2023-01-01' -> '01-01'
                              if (
                                typeof v === "string" &&
                                v.length > 5 &&
                                v.includes("-")
                              )
                                return v.slice(5);
                              return v;
                            }}
                          />
                          <YAxis
                            tick={{ fontSize: 10, fill: "#94a3b8" }}
                            axisLine={false}
                            tickLine={false}
                          />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: "#1e293b",
                              border: "none",
                              borderRadius: "8px",
                              color: "#fff",
                              fontSize: "12px",
                            }}
                          />
                          <Area
                            type="monotone"
                            dataKey="value"
                            stroke={chartColor}
                            fill={`url(#grad-${idx})`}
                            strokeWidth={2}
                            animationDuration={1500}
                          />
                        </AreaChart>
                      )}
                    </ResponsiveContainer>
                  ) : (
                    <div className="h-full flex items-center justify-center text-slate-400 text-sm">
                      No data available for visualization
                    </div>
                  )}
                </div>
              </div>
            );
          }

          case "flow":
            return (
              <div
                key={idx}
                className="my-4 p-5 bg-slate-50 dark:bg-slate-900/50 rounded-xl border border-slate-200 dark:border-slate-800"
              >
                <div className="flex items-center gap-2 mb-6 text-xs font-bold text-slate-500 uppercase tracking-wider">
                  <Workflow className="h-4 w-4" />{" "}
                  {block.title || "Strategic Process"}
                </div>
                <div className="flex flex-col md:flex-row gap-4 justify-between relative isolate">
                  <div className="hidden md:block absolute top-1/2 left-0 w-full h-0.5 bg-slate-200 dark:bg-slate-700 -z-10 -translate-y-1/2" />
                  {block.steps?.map((step, sIdx) => (
                    <div
                      key={sIdx}
                      className="flex-1 flex flex-col items-center text-center gap-3 bg-white dark:bg-slate-900 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm transition-transform hover:-translate-y-1"
                    >
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-white shadow-sm ring-4 ring-white dark:ring-slate-900 ${
                          step.status === "completed"
                            ? "bg-emerald-500"
                            : step.status === "current"
                            ? "bg-indigo-500"
                            : "bg-slate-300 dark:bg-slate-700"
                        }`}
                      >
                        {step.step}
                      </div>
                      <span className="text-xs font-semibold text-slate-700 dark:text-slate-300">
                        {step.label}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            );

          case "recommendation":
            return (
              <div
                key={idx}
                className="mt-6 overflow-hidden rounded-xl border border-indigo-100 dark:border-indigo-900/50 bg-white dark:bg-slate-900 shadow-sm"
              >
                <div className="bg-indigo-50/50 dark:bg-indigo-900/20 p-4 border-b border-indigo-100 dark:border-indigo-900/30 flex items-center gap-2">
                  <Lightbulb className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
                  <h4 className="font-semibold text-indigo-900 dark:text-indigo-200 text-sm">
                    {block.title || "Strategic Recommendation"}
                  </h4>
                </div>
                <div className="p-5">
                  <div className="prose prose-sm dark:prose-invert max-w-none text-slate-600 dark:text-slate-400 whitespace-pre-wrap">
                    {block.text}
                  </div>

                  {/* {block.actions && block.actions.length > 0 && (
                    <div className="mt-4 flex gap-2">
                      {block.actions.map((action, i) => (
                        <button
                          key={i}
                          onClick={() => onAction && onAction(action)}
                          className={`text-xs font-medium px-3 py-1.5 rounded-lg transition-colors shadow-sm ${
                            i === 0
                              ? "bg-indigo-600 text-white hover:bg-indigo-700"
                              : "bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-50"
                          }`}
                        >
                          {action.label}
                        </button>
                      ))}
                    </div>
                  )} */}
                </div>
              </div>
            );

          default:
            return null;
        }
      })}
    </div>
  );
}
