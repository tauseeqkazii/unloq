import { useState } from "react";
import {
  Database,
  Check,
  Loader2,
  Cloud,
  Server,
  Share2,
  Layers,
} from "lucide-react";

export function ConnectorsPanel() {
  const [connecting, setConnecting] = useState<string | null>(null);
  const [connected, setConnected] = useState<string[]>([
    "salesforce",
    "postgres",
  ]); // Defaults

  const toggleConnect = (id: string) => {
    if (connected.includes(id)) {
      setConnected((prev) => prev.filter((c) => c !== id));
      return;
    }
    setConnecting(id);
    setTimeout(() => {
      setConnected((prev) => [...prev, id]);
      setConnecting(null);
    }, 1500);
  };

  const connectors = [
    {
      id: "salesforce",
      name: "Salesforce CRM",
      icon: <Cloud className="h-4 w-4 text-sky-500" />,
    },
    {
      id: "postgres",
      name: "Production DB",
      icon: <Server className="h-4 w-4 text-indigo-500" />,
    },
    {
      id: "google_ads",
      name: "Google Ads",
      icon: <Share2 className="h-4 w-4 text-amber-500" />,
    },
    {
      id: "jira",
      name: "Jira Software",
      icon: <Layers className="h-4 w-4 text-blue-600" />,
    },
  ];

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider flex items-center gap-2">
        <Database className="h-4 w-4" /> Data Sources
      </h3>
      <div className="space-y-2">
        {connectors.map((c) => (
          <div
            key={c.id}
            className="flex items-center justify-between p-3 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg shadow-sm"
          >
            <div className="flex items-center gap-3">
              <span className="p-2 bg-slate-50 dark:bg-slate-800 rounded-md">
                {c.icon}
              </span>
              <span className="text-sm font-medium text-slate-700 dark:text-slate-300">
                {c.name}
              </span>
            </div>
            <button
              onClick={() => toggleConnect(c.id)}
              disabled={connecting === c.id}
              className={`text-[10px] uppercase font-bold px-3 py-1.5 rounded-md transition-all flex items-center gap-1 ${
                connected.includes(c.id)
                  ? "bg-emerald-50 text-emerald-600 border border-emerald-100"
                  : "bg-slate-100 text-slate-500 hover:bg-slate-200"
              }`}
            >
              {connecting === c.id ? (
                <Loader2 className="h-3 w-3 animate-spin" />
              ) : connected.includes(c.id) ? (
                <>
                  <Check className="h-3 w-3" /> Active
                </>
              ) : (
                "Connect"
              )}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
