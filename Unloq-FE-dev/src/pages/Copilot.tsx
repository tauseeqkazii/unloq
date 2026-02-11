import { Sparkles } from "lucide-react";
import ChatInterface from "../components/ChatInterface";

export default function Copilot() {
  return (
    <div className="flex h-[calc(100vh-6rem)] flex-col bg-white dark:bg-[#22223a] rounded-xl shadow-sm border-gray-200 dark:border-[#33334d] overflow-hidden">
      <div className="border-b border-gray-200 dark:border-[#33334d] bg-gray-50/50 dark:bg-[#1a1a2e]/50 px-6 py-4 flex items-center gap-2 border-0">
        <Sparkles className="h-5 w-5 text-indigo-600 dark:text-indigo-400" />
        <div>
          <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
            Oakfield Strategist
          </h1>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            AI-powered strategy assistant
          </p>
        </div>
      </div>

      <div className="flex-1 overflow-hidden flex flex-col">
        <ChatInterface />
      </div>
    </div>
  );
}
