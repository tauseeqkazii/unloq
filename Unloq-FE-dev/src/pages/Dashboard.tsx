import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import {
  Activity,
  AlertTriangle,
  CheckCircle,
  TrendingUp,
  // Loader2,
} from "lucide-react"; // Import Loader2
import { IngestionAnimation } from "../components/IngestionAnimation";
import { KPICard } from "../components/KPICard";

// ... (KEEP ALL INTERFACES AS THEY WERE IN PREVIOUS VERSIONS) ...
interface HeadlineCardData {
  card_id: string;
  title: string;
  primary_value: { text: string; status: "off_track" | "at_risk" | "on_track" };
  secondary_text: string;
  insight_text: string;
  sparkline: { points: number[]; direction: "up" | "down" } | null;
}
interface IssueData {
  issue_id: string;
  title: string;
  status: string;
  metric_text: string;
  driver_text: string;
}
interface DecisionPreview {
  recommendation_id: string;
  title: string;
  status: string;
  confidence?: string;
  expected_impact?: string;
}
interface LedgerRow {
  title: string;
  note: string;
  expected: string;
  actual: string;
  status: "Realized" | "Pending" | "In Progress";
}
interface LedgerSummary {
  totals: {
    expected_roi_value: string;
    actual_roi_value: string;
    in_progress_value: string;
  };
  rows: LedgerRow[];
}
interface DashboardResponse {
  company: { data_updated_at: string; mode: string };
  headline_cards: HeadlineCardData[];
  top_issues: IssueData[];
  decision_inbox_preview: DecisionPreview[];
  ledger_summary: LedgerSummary;
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  // const [processingId, setProcessingId] = useState<string | null>(null); // NEW STATE
  const navigate = useNavigate();

  const dataFetchedRef = useRef(false);

  useEffect(() => {
    if (dataFetchedRef.current) return;
    dataFetchedRef.current = true;

    const loadData = async () => {
      try {
        const res = await api.getDashboard();
        setData(res);
      } catch (e) {
        console.error("Dashboard Load Failed", e);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  // const handleApprove = async (id: string) => {
  //   setProcessingId(id); // Start loading
  //   try {
  //     await api.submitApprovalAction(id, "approve");
  //     const res = await api.getDashboard();
  //     setData(res);
  //   } catch (e) {
  //     console.error("Approval failed", e);
  //   } finally {
  //     setProcessingId(null); // Stop loading
  //   }
  // };

  const handleAnalyze = (issueTitle: string) => {
    navigate("/strategist", {
      state: {
        initialQuery: `Analyze the strategic issue: "${issueTitle}". What are the root causes and recommendations?`,
      },
    });
  };

  if (loading) return <IngestionAnimation onComplete={() => {}} />;

  if (!data)
    return (
      <div className="p-12 text-center text-slate-500 font-medium">
        Unable to load dashboard data. Please check connection.
      </div>
    );

  return (
    <div className="space-y-8 pb-10 max-w-[1600px] mx-auto p-6 md:p-10 animate-in fade-in duration-500">
      {/* HEADER */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 dark:border-[#252525] pb-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white tracking-tight">
            Oakfield Dynamics
          </h1>
          <p className="text-slate-500 mt-1 flex items-center gap-2 text-sm">
            <Activity className="h-4 w-4 text-indigo-500" /> Strategy Operating
            System
          </p>
        </div>
        <div className="flex flex-col items-end gap-1">
          <div className="px-3 py-1 bg-slate-100 dark:bg-[#1a1a1a] rounded-full text-xs font-mono text-slate-500 border border-slate-200 dark:border-[#33334d]">
            UPDATED: {new Date(data.company.data_updated_at).toLocaleString()}
          </div>
          <div className="text-[10px] uppercase font-bold text-indigo-500 tracking-wider">
            {data.company.mode} MODE
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {data.headline_cards.map((card) => (
          <KPICard
            key={card.card_id}
            title={card.title}
            value={card.primary_value.text}
            status={card.primary_value.status}
            secondaryText={card.secondary_text}
            insight={card.insight_text}
          />
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <div className="xl:col-span-2 space-y-4">
          <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider flex items-center gap-2">
            <AlertTriangle className="h-4 w-4" /> Top Strategic Issues
          </h3>
          <div className="bg-white dark:bg-[#111111] rounded-xl border border-slate-200 dark:border-[#33334d] shadow-sm overflow-hidden">
            {data.top_issues.map((issue) => (
              <div
                key={issue.issue_id}
                className="p-5 border-b border-slate-100 dark:border-[#1a1a1a] last:border-0 hover:bg-slate-50 dark:hover:bg-[#2a2a45] transition-all duration-200 flex gap-4 group hover:-translate-x-0.5"
              >
                <div
                  className={`w-1.5 rounded-full ${
                    issue.status === "off_track" ? "bg-red-500" : "bg-amber-500"
                  }`}
                />
                <div className="flex-1 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className={`px-2 py-0.5 text-[10px] font-bold uppercase rounded ${
                          issue.status === "off_track"
                            ? "bg-red-50 text-red-600"
                            : "bg-amber-50 text-amber-600"
                        }`}
                      >
                        {issue.status.replace("_", " ")}
                      </span>
                      <h4 className="font-semibold text-slate-900 dark:text-white">
                        {issue.title}
                      </h4>
                    </div>
                    <div className="text-sm text-slate-600 dark:text-slate-300 mt-1 font-medium">
                      {issue.metric_text}
                    </div>
                    <div className="text-xs text-slate-400 mt-1 flex items-center gap-1">
                      <Activity className="h-3 w-3" /> Driver:{" "}
                      {issue.driver_text}
                    </div>
                  </div>
                  <button
                    onClick={() => handleAnalyze(issue.title)}
                    className="text-xs bg-slate-50 dark:bg-[#1a1a1a] hover:bg-white border border-slate-200 dark:border-[#33334d] px-4 py-2 rounded-lg font-medium text-slate-600 dark:text-slate-300 transition-all duration-200 shadow-sm whitespace-nowrap hover:text-indigo-600 hover:border-indigo-200 dark:hover:border-indigo-500/40 dark:hover:text-indigo-400 hover:shadow-md"
                  >
                    Explore with Strategist
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider flex items-center gap-2">
            <CheckCircle className="h-4 w-4" /> Decision Inbox
          </h3>
          <div className="space-y-3">
            {/* {data.decision_inbox_preview.map((dec) => (
              <div
                key={dec.recommendation_id}
                className="bg-white dark:bg-slate-900 p-5 rounded-xl border border-slate-200 dark:border-slate-800 shadow-sm relative group hover:border-indigo-200 transition-colors"
              >
                <div className="absolute top-4 right-4">
                  <span className="text-[10px] font-bold text-indigo-600 bg-indigo-50 px-2 py-1 rounded">
                    {dec.confidence || "High Confidence"}
                  </span>
                </div>
                <div className="mt-2">
                  <h4 className="font-semibold text-slate-900 dark:text-white text-sm pr-16 leading-snug">
                    {dec.title}
                  </h4>
                  {dec.expected_impact && (
                    <p className="text-xs text-slate-500 mt-2 line-clamp-2">
                      Impact: {dec.expected_impact}
                    </p>
                  )}
                  <div className="mt-4 flex gap-2">
                    <button
                      onClick={() => handleApprove(dec.recommendation_id)}
                      disabled={!!processingId}
                      className="flex-1 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-xs py-2 rounded-lg font-medium transition-colors shadow-sm flex items-center justify-center gap-2"
                    >
                      {processingId === dec.recommendation_id ? (
                        <Loader2 className="h-3 w-3 animate-spin" />
                      ) : (
                        "Approve"
                      )}
                    </button>
                    <button
                      disabled={!!processingId}
                      className="px-3 bg-white border border-slate-200 hover:bg-slate-50 disabled:opacity-50 text-slate-600 text-xs py-2 rounded-lg font-medium transition-colors"
                    >
                      Review
                    </button>
                  </div>
                </div>
              </div>
            ))} */}
          </div>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider flex items-center gap-2">
          <TrendingUp className="h-4 w-4" /> Impact Ledger (Realised Receipts)
        </h3>
        <div className="bg-white dark:bg-[#111111] rounded-xl border border-slate-200 dark:border-[#33334d] shadow-sm overflow-hidden">
          <div className="grid grid-cols-3 border-b border-slate-100 dark:border-[#33334d] divide-x divide-slate-100 dark:divide-[#252525]">
            <div className="p-6 text-center">
              <div className="text-xs text-slate-400 uppercase font-semibold tracking-wider">
                Expected ROI
              </div>
              <div className="text-2xl font-bold text-slate-900 dark:text-white mt-1">
                {data.ledger_summary.totals.expected_roi_value}
              </div>
            </div>
            <div className="p-6 text-center bg-emerald-50/30 dark:bg-emerald-900/10">
              <div className="text-xs text-emerald-600 dark:text-emerald-400 uppercase font-semibold tracking-wider">
                Realised So Far
              </div>
              <div className="text-2xl font-bold text-emerald-700 dark:text-emerald-400 mt-1">
                {data.ledger_summary.totals.actual_roi_value}
              </div>
            </div>
            <div className="p-6 text-center">
              <div className="text-xs text-slate-400 uppercase font-semibold tracking-wider">
                In Progress
              </div>
              <div className="text-2xl font-bold text-slate-900 dark:text-white mt-1">
                {data.ledger_summary.totals.in_progress_value}
              </div>
            </div>
          </div>
          <div className="divide-y divide-slate-100 dark:divide-[#252525]">
            {data.ledger_summary.rows.map((row, i) => (
              <div
                key={i}
                className="p-4 flex flex-col sm:flex-row sm:items-center justify-between hover:bg-slate-50 dark:hover:bg-[#1a1a1a] transition-all duration-200 gap-4"
              >
                <div className="flex-1">
                  <div className="font-medium text-slate-900 dark:text-white text-sm">
                    {row.title}
                  </div>
                  <div className="text-xs text-slate-500 mt-0.5">
                    {row.note}
                  </div>
                </div>
                <div className="flex items-center gap-6 text-sm w-full sm:w-auto justify-between sm:justify-end">
                  <div className="text-right">
                    <div className="text-[10px] text-slate-400 uppercase">
                      Expected
                    </div>
                    <div className="font-mono text-slate-700 dark:text-slate-300">
                      {row.expected}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-[10px] text-slate-400 uppercase">
                      Actual
                    </div>
                    <div
                      className={`font-mono font-bold ${
                        row.status === "Realized"
                          ? "text-emerald-600"
                          : "text-slate-400"
                      }`}
                    >
                      {row.actual}
                    </div>
                  </div>
                  <div className="w-24 text-right">
                    <span
                      className={`px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wide ${
                        row.status === "Realized"
                          ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
                          : "bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                      }`}
                    >
                      {row.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
