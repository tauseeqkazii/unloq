import { AreaChart, Area, ResponsiveContainer } from "recharts";
import type { HeadlineCardData } from "../types";
import { cn } from "../lib/utils";

export function HeadlineCard({ data }: { data: HeadlineCardData }) {
  // Transform array of numbers to objects for Recharts
  const chartData = data.sparkline?.points.map((val, i) => ({ i, val })) || [];
  const color = data.sparkline?.color === "rose" ? "#e11d48" : "#10b981";

  return (
    <div className="bg-white dark:bg-slate-800 rounded-2xl p-5 border border-gray-100 dark:border-slate-700 shadow-sm flex flex-col justify-between h-[160px] relative overflow-hidden group hover:shadow-md transition-shadow">
      <div className="z-10">
        <h3 className="text-sm font-medium text-slate-500 dark:text-slate-400 mb-1">
          {data.title}
        </h3>
        <div className="flex items-baseline gap-2">
          <span
            className={cn(
              "text-3xl font-bold tracking-tight",
              data.primary_value.status === "off_track"
                ? "text-red-600 dark:text-red-400"
                : data.primary_value.status === "at_risk"
                ? "text-amber-500"
                : "text-slate-900 dark:text-white"
            )}
          >
            {data.primary_value.text}
          </span>
        </div>
        <p className="text-xs font-medium text-slate-400 mt-1">
          {data.secondary_text}
        </p>
      </div>

      <div className="mt-auto z-10">
        <p className="text-xs text-slate-500 border-l-2 border-slate-200 pl-2 italic">
          "{data.insight_text}"
        </p>
      </div>

      {/* Sparkline in background */}
      {data.sparkline && (
        <div className="absolute bottom-0 right-0 w-1/2 h-16 opacity-20 group-hover:opacity-30 transition-opacity">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <Area
                type="monotone"
                dataKey="val"
                stroke={color}
                fill={color}
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
