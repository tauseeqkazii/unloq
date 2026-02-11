import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { Radio, TrendingUp } from "lucide-react";
import type { Signal, LedgerEntry } from "../types";

export function SignalFeed() {
  const [signals, setSignals] = useState<Signal[]>([]);
  const [ledgerEntries, setLedgerEntries] = useState<LedgerEntry[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [sigRes, ledRes] = await Promise.all([
          api.getSignals(),
          api.getLedger(), // Assuming this returns array
        ]);
        setSignals(sigRes);
        setLedgerEntries(ledRes.slice(0, 3)); // Top 3
      } catch (e) {
        console.error("Feed Error", e);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      {/* 1. Signals Section */}
      <div className="space-y-3">
        <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider flex items-center gap-2">
          <Radio className="h-4 w-4" /> Market Signals
        </h3>
        {signals.map((s) => (
          <div
            key={s.id}
            className="bg-white dark:bg-slate-900 p-3 rounded-lg border border-slate-200 dark:border-slate-800 shadow-sm"
          >
            <div className="flex justify-between text-[10px] text-slate-400 mb-1">
              <span className="uppercase font-bold">{s.type}</span>
              <span>{s.timestamp}</span>
            </div>
            <div className="text-xs font-medium text-slate-800 dark:text-slate-200 line-clamp-2">
              {s.description}
            </div>
          </div>
        ))}
      </div>

      {/* 2. Mini Ledger Section (Restored) */}
      <div className="space-y-3 pt-4 border-t border-slate-200 dark:border-slate-800">
        <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider flex items-center gap-2">
          <TrendingUp className="h-4 w-4" /> Recent Impact
        </h3>
        {ledgerEntries.map((e) => (
          <div key={e.id} className="flex justify-between items-center text-xs">
            <span className="text-slate-600 dark:text-slate-400">
              ROI Event
            </span>
            <span className="font-mono font-bold text-emerald-600">
              {e.impact}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
