import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { CheckCircle, ExternalLink } from "lucide-react";
import type { ChatBlock } from "../types";
import { cn } from "../lib/utils";

export function BlockRenderer({ blocks }: { blocks: ChatBlock[] }) {
  return (
    <div className="space-y-4 w-full">
      {blocks.map((block, idx) => {
        switch (block.type) {
          case "summary":
            return (
              <p
                key={idx}
                className="text-gray-800 dark:text-gray-200 leading-relaxed"
              >
                {block.text}
              </p>
            );

          case "metrics":
            return (
              <div key={idx} className="grid grid-cols-3 gap-2 my-2">
                {(block.items as { label: string; value: string; change: string }[] | undefined)?.map((item, i: number) => (
                  <div
                    key={i}
                    className="bg-slate-50 dark:bg-slate-900/50 p-3 rounded-lg border border-slate-100 dark:border-slate-800"
                  >
                    <div className="text-xs text-slate-500 uppercase font-medium">
                      {item.label}
                    </div>
                    <div className="text-lg font-bold text-slate-900 dark:text-white mt-1">
                      {item.value}
                    </div>
                    <div
                      className={cn(
                        "text-xs flex items-center mt-1",
                        item.change.includes("-") || item.change === "down"
                          ? "text-red-600"
                          : "text-emerald-600"
                      )}
                    >
                      {item.change}
                    </div>
                  </div>
                ))}
              </div>
            );

          case "chart":
            return (
              <div
                key={idx}
                className="h-48 w-full bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-xl p-4 my-2"
              >
                <div className="text-xs font-semibold text-slate-500 mb-2">
                  {block.title}
                </div>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={block.data}>
                    <XAxis dataKey="ts" hide />
                    <YAxis hide domain={["auto", "auto"]} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: "#1e293b",
                        border: "none",
                        borderRadius: "8px",
                        color: "#fff",
                      }}
                      itemStyle={{ color: "#fff" }}
                    />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke="#6366f1"
                      strokeWidth={2}
                      dot={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            );

          case "recommended_action":
            return (
              <div
                key={idx}
                className="bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-100 dark:border-indigo-900 rounded-xl p-4 mt-2"
              >
                <div className="flex items-start gap-3">
                  <div className="bg-indigo-100 dark:bg-indigo-900 p-2 rounded-lg">
                    <CheckCircle className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-indigo-900 dark:text-indigo-100 text-sm">
                      {block.title}
                    </h4>
                    <p className="text-sm text-indigo-700 dark:text-indigo-300 mt-1 mb-3">
                      {block.text}
                    </p>
                    <button className="bg-indigo-600 hover:bg-indigo-700 text-white text-sm px-4 py-2 rounded-lg font-medium transition-colors shadow-sm">
                      {block.cta?.label || "Approve Action"}
                    </button>
                  </div>
                </div>
              </div>
            );

          case "evidence":
            return (
              <div key={idx} className="flex flex-wrap gap-2 mt-2">
                {(block.items as { label: string }[] | undefined)?.map((item, i: number) => (
                  <span
                    key={i}
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-xs text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700"
                  >
                    <ExternalLink className="h-3 w-3" />
                    {item.label}
                  </span>
                ))}
              </div>
            );

          default:
            return null;
        }
      })}
    </div>
  );
}
