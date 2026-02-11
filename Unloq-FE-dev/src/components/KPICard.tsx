import { TrendingUp, TrendingDown, Minus } from "lucide-react";
import { cn } from "../lib/utils";

interface KPICardProps {
  title: string;
  value: string | number;
  unit?: string;
  trend?: {
    value: number;
    direction: "up" | "down" | "neutral";
  };
  status?: "on_track" | "at_risk" | "off_track";
  secondaryText?: string;
  insight?: string;
  onClick?: () => void;
}

export function KPICard({
  title,
  value,
  unit,
  trend,
  status = "on_track",
  secondaryText,
  insight,
  onClick,
}: KPICardProps) {
  const statusColors = {
    on_track:
      "bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 border-emerald-100 dark:border-emerald-800",
    at_risk:
      "bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300 border-amber-100 dark:border-amber-800",
    off_track:
      "bg-rose-50 dark:bg-rose-900/30 text-rose-700 dark:text-rose-300 border-rose-100 dark:border-rose-800",
  };

  const trendColor =
    trend?.direction === "up"
      ? "text-emerald-600"
      : trend?.direction === "down"
      ? "text-rose-600"
      : "text-gray-500";
  const TrendIcon =
    trend?.direction === "up"
      ? TrendingUp
      : trend?.direction === "down"
      ? TrendingDown
      : Minus;

  return (
    <div
      onClick={onClick}
      role={onClick ? "button" : "article"}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={
        onClick
          ? (e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onClick();
              }
            }
          : undefined
      }
      className={cn(
        "rounded-xl border p-5 shadow-sm transition-all duration-200 hover:-translate-y-1 hover:shadow-lg bg-white dark:bg-[#22223a] dark:border-[#33334d] select-none hover-glow",
        onClick ? "cursor-pointer active:scale-[0.98]" : "",
        statusColors[status]
      )}
    >
      <div className="flex justify-between items-start">
        <h3 className="text-sm font-medium opacity-80">{title}</h3>
        {status === "at_risk" && (
          <span className="inline-flex items-center rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">
            At Risk
          </span>
        )}
      </div>

      <div className="mt-4 flex flex-col">
        <div className="flex items-baseline">
          <span className="text-2xl font-bold tracking-tight">{value}</span>
          {unit && (
            <span className="ml-1 text-sm font-medium opacity-60">{unit}</span>
          )}
        </div>
        {secondaryText && (
          <p className="text-xs text-slate-500 mt-1">{secondaryText}</p>
        )}
        {insight && (
          <p className="text-xs text-indigo-600 mt-2 font-medium bg-indigo-50 dark:bg-indigo-900/20 p-2 rounded">
            💡 {insight}
          </p>
        )}
      </div>

      {trend && (
        <div
          className={cn(
            "mt-2 flex items-center text-sm font-medium",
            trendColor
          )}
        >
          <TrendIcon className="mr-1 h-3 w-3" aria-hidden="true" />
          <span>{Math.abs(trend.value)}%</span>
          <span className="ml-1 opacity-60 text-current">vs last month</span>
        </div>
      )}
    </div>
  );
}
