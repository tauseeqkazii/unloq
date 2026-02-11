import { useCallback, useEffect, useState } from "react";
import {
  Check,
  X,
  ArrowRight,
  Clock,
  CheckCircle,
  Loader2,
} from "lucide-react";
import { api } from "../lib/api";
import { useToast } from "../context/useToast";
import type { Recommendation } from "../types";

export default function ApprovalsPage() {
  const [items, setItems] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState<string | null>(null); // New State
  const { addToast } = useToast();

  const fetchApprovals = useCallback(async () => {
    try {
      const data = await api.getApprovals();
      setItems(data);
    } catch {
      addToast("Failed to load approvals", "error");
    } finally {
      setLoading(false);
    }
  }, [addToast]);

  useEffect(() => {
    fetchApprovals();
  }, [fetchApprovals]);

  const handleAction = async (id: string, action: "approve" | "reject") => {
    setProcessingId(id); // Start loading
    try {
      await api.submitApprovalAction(id, action);
      addToast(`Decision ${action}d successfully`, "success");
      setItems((prev) => prev.filter((i) => i.id !== id));
    } catch {
      addToast("Action failed. Please try again.", "error");
    } finally {
      setProcessingId(null); // Stop loading
    }
  };

  if (loading)
    return (
      <div className="p-10 flex justify-center">
        <Loader2 className="animate-spin h-8 w-8 text-indigo-500" />
      </div>
    );

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-12 animate-in fade-in duration-500">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          Decision Inbox
        </h1>
        <p className="text-slate-500 mt-1">
          Review and approve strategic recommendations.
        </p>
      </div>

      {items.length === 0 ? (
        <div className="text-center py-20 bg-slate-50 dark:bg-slate-900 rounded-2xl border border-dashed border-slate-300 dark:border-slate-700">
          <CheckCircle className="h-12 w-12 text-emerald-500 mx-auto opacity-50" />
          <h3 className="mt-4 text-lg font-medium text-slate-900 dark:text-white">
            All Caught Up
          </h3>
          <p className="text-slate-500">No pending decisions.</p>
        </div>
      ) : (
        <div className="grid gap-6">
          {items.map((item) => (
            <div
              key={item.id}
              className="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden"
            >
              <div className="absolute top-0 left-0 w-1 h-full bg-indigo-500" />

              <div className="flex flex-col md:flex-row gap-6">
                <div className="flex-1 space-y-4">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <span className="bg-indigo-50 text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300 text-[10px] uppercase font-bold px-2 py-1 rounded">
                        Strategic Rec
                      </span>
                      <span className="text-xs text-slate-400 flex items-center gap-1">
                        <Clock className="h-3 w-3" /> Generated today
                      </span>
                    </div>
                    <h3 className="text-lg font-semibold text-slate-900 dark:text-white leading-tight">
                      {item.title}
                    </h3>
                  </div>

                  <div className="bg-slate-50 dark:bg-slate-800/50 p-4 rounded-xl text-sm text-slate-700 dark:text-slate-300 leading-relaxed border border-slate-100 dark:border-slate-700">
                    <span className="font-semibold text-slate-900 dark:text-white block mb-1">
                      Rationale:
                    </span>
                    {item.rationale}
                  </div>

                  <div className="flex items-center gap-2 text-sm font-medium text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20 w-fit px-3 py-1.5 rounded-lg border border-emerald-100 dark:border-emerald-800">
                    <ArrowRight className="h-4 w-4" />
                    Expected Impact: {item.impact_estimate}
                  </div>
                </div>

                <div className="flex flex-row md:flex-col gap-3 justify-center border-t md:border-t-0 md:border-l border-slate-100 dark:border-slate-800 pt-4 md:pt-0 md:pl-6 min-w-[140px]">
                  <button
                    onClick={() => handleAction(item.id, "approve")}
                    disabled={!!processingId}
                    className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-medium py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-colors shadow-sm"
                  >
                    {processingId === item.id ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Check className="h-4 w-4" />
                    )}
                    Approve
                  </button>
                  <button
                    onClick={() => handleAction(item.id, "reject")}
                    disabled={!!processingId}
                    className="flex-1 bg-white hover:bg-slate-50 dark:bg-slate-800 dark:hover:bg-slate-700 disabled:opacity-50 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-600 font-medium py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-colors"
                  >
                    <X className="h-4 w-4" /> Reject
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
