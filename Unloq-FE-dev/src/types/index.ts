export interface SparklineData {
  period: string;
  points: number[];
  direction: "up" | "down";
  color: "rose" | "emerald";
}

export interface HeadlineCardData {
  card_id: string;
  title: string;
  primary_value: { text: string; status: "off_track" | "at_risk" | "on_track" };
  secondary_text: string;
  insight_text: string;
  sparkline: SparklineData | null;
}

export interface IssueData {
  issue_id: string;
  status: "off_track" | "at_risk";
  title: string;
  metric_text: string;
  driver_text: string;
}

export interface DecisionData {
  recommendation_id: string;
  title: string;
  status: "pending_approval";
  expected_impact: string;
  linked_kpis: string;
  confidence: string;
}

export interface LedgerRow {
  title: string;
  expected: string;
  actual: string;
  status: "Realized" | "In Progress";
  note: string;
}

export interface DashboardResponse {
  company: { data_updated_at: string; mode: string };
  headline_cards: HeadlineCardData[];
  top_issues: IssueData[];
  decision_inbox_preview: DecisionData[];
  ledger_summary: {
    totals: {
      expected_roi_value: string;
      actual_roi_value: string;
      in_progress_value: string;
    };
    rows: LedgerRow[];
  };
}

// Chat Block Types
export type BlockType =
  | "summary"
  | "metrics"
  | "chart"
  | "evidence"
  | "recommended_action";

export interface ChatBlock {
  type: BlockType;
  text?: string; // for summary or recommended_action
  title?: string; // for chart or action
  items?: unknown[]; // for metrics or evidence
  data?: unknown[]; // for charts
  unit?: string;
  cta?: { label: string; target: string; params: Record<string, unknown> };
}

export interface NavigationAction {
  type: "navigation";
  label: string;
  route: string;
}

export interface ApiAction {
  type: "api";
  label: string;
  action_id: string;
  method: "POST" | "GET" | "PUT" | "DELETE";
  body?: Record<string, unknown>;
}

export type ChatAction = NavigationAction | ApiAction;

export interface CopilotResponse {
  type: "analysis_response";
  title: string;
  blocks: ChatBlock[];
}

export interface LedgerEntry {
  id: string | number;
  date: string;
  event: string;
  impact: string;
}

export interface ChartData {
  name: string;
  investment: number;
  return_value: number;
}

export interface StrategyNode {
  id: string;
  type: "objective" | "kpi" | "programme";
  title: string;
  meta?: string;
  status?: "on_track" | "at_risk" | "off_track";
  children?: StrategyNode[];
}

export interface Session {
  session_id: string;
  title: string;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export interface Recommendation {
  id: string;
  title: string;
  rationale: string;
  status: string;
  impact_estimate: string;
}

export interface Signal {
  id: string;
  type: string;
  title: string;
  description: string;
  timestamp: string;
}
