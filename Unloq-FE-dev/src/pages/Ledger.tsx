import { useEffect, useState } from "react";
import { ROIChart } from "../components/ROIChart";
import { apiClient as api } from "../lib/api";
import type { LedgerEntry, ChartData } from "../types";

export default function Ledger() {
  const [entries, setEntries] = useState<LedgerEntry[]>([]);
  const [chartData, setChartData] = useState<ChartData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [entriesRes, chartRes] = await Promise.all([
          api.get<LedgerEntry[]>("/oakfield/ledger"),
          api.get<ChartData[]>("/oakfield/analytics/roi"),
        ]);
        setEntries(entriesRes.data);
        setChartData(chartRes.data);
      } catch (error) {
        console.error("Failed to load ledger data", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading)
    return (
      <div className="p-12 text-center text-gray-500 dark:text-gray-400">
        Loading Ledger...
      </div>
    );

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
            Impact Ledger
          </h1>
          <p className="text-gray-500 dark:text-gray-400">
            Track the realized value of strategic decisions.
          </p>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800">
          <svg
            className="h-4 w-4 text-indigo-600 dark:text-indigo-400"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <div className="text-xs">
            <p className="font-medium text-indigo-900 dark:text-indigo-100">
              Strategy Refresh
            </p>
            <p className="text-indigo-600 dark:text-indigo-400">
              Updated 2 days ago
            </p>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <div className="rounded-xl border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-6 shadow-sm">
          <ROIChart data={chartData} />
        </div>

        <div className="rounded-xl border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-6 shadow-sm">
          <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-4">
            Recent Impact Events
          </h3>
          <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-slate-700">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-slate-700">
              <thead className="bg-gray-50 dark:bg-slate-900">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Event
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider whitespace-nowrap">
                    Impact
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-slate-800 divide-y divide-gray-200 dark:divide-slate-700">
                {entries.map((entry) => (
                  <tr key={entry.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {entry.date}
                    </td>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900 dark:text-white">
                      {entry.event}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 text-right">
                      {entry.impact}
                    </td>
                  </tr>
                ))}
                {entries.length === 0 && (
                  <tr>
                    <td
                      colSpan={3}
                      className="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400"
                    >
                      No realized impact events yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
