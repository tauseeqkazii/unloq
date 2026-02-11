import { motion, AnimatePresence } from "framer-motion";
import {
  ChevronRight,
  ChevronDown,
  Target,
  BarChart2,
  Zap,
} from "lucide-react";
import { useState } from "react";
import type { StrategyNode } from "../types";

const TreeNode = ({
  node,
  level = 0,
}: {
  node: StrategyNode;
  level?: number;
}) => {
  const [isOpen, setIsOpen] = useState(true);

  const icons = {
    objective: <Target className="w-4 h-4 text-blue-500" />,
    kpi: <BarChart2 className="w-4 h-4 text-emerald-500" />,
    programme: <Zap className="w-4 h-4 text-amber-500" />,
  };

  return (
    <div className="ml-4 md:ml-6 relative">
      {/* Connector Line (Vertical) */}
      {level > 0 && (
        <div className="absolute -left-4 md:-left-6 top-0 bottom-0 w-px bg-gray-200 dark:bg-slate-700" />
      )}

      <div className="relative">
        {/* Connector Line (Horizontal) */}
        {level > 0 && (
          <div className="absolute -left-4 md:-left-6 top-3 h-px w-4 md:w-6 bg-gray-200 dark:bg-slate-700" />
        )}

        <div className="flex items-center gap-2 py-2 group">
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="p-1 rounded hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors cursor-pointer z-10 relative"
          >
            {node.children && node.children.length > 0 ? (
              isOpen ? (
                <ChevronDown className="w-4 h-4 text-gray-400" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-400" />
              )
            ) : (
              <span className="w-4 h-4 block" />
            )}
          </button>

          <div className="flex items-center gap-3 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 px-3 py-2 rounded-lg shadow-sm hover:shadow-md transition-shadow min-w-[200px]">
            <div className="p-1.5 bg-gray-50 dark:bg-slate-700 rounded-md">
              {icons[node.type]}
            </div>
            <div>
              <h4 className="text-sm font-medium text-gray-900 dark:text-gray-100">
                {node.title}
              </h4>
              {node.meta && (
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {node.meta}
                </p>
              )}
            </div>
            {node.status && (
              <div
                className={`ml-auto w-2 h-2 rounded-full ${
                  node.status === "on_track"
                    ? "bg-green-500"
                    : node.status === "at_risk"
                    ? "bg-amber-500"
                    : "bg-red-500"
                }`}
              />
            )}
          </div>
        </div>
      </div>

      <AnimatePresence>
        {isOpen && node.children && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            {node.children.map((child) => (
              <TreeNode key={child.id} node={child} level={level + 1} />
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default function StrategyTree({ data }: { data: StrategyNode[] }) {
  if (!data || data.length === 0) return null;

  return (
    <div className="p-4 overflow-x-auto rounded-xl border border-gray-200 dark:border-slate-700 bg-gray-50/50 dark:bg-slate-900/50">
      {data.map((node) => (
        <TreeNode key={node.id} node={node} />
      ))}
    </div>
  );
}
