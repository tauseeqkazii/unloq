import { motion } from "framer-motion";
import {
  Database,
  FileText,
  ArrowRight,
  CheckCircle,
  Loader2,
} from "lucide-react";
import { useState, useEffect } from "react";

const steps = [
  { id: 1, label: "Reading unstructured PDF...", icon: FileText },
  { id: 2, label: "Extracting strategic signals...", icon: Database },
  { id: 3, label: "Updating Strategy OS...", icon: ArrowRight },
  { id: 4, label: "Synchronization Complete", icon: CheckCircle },
];

export function IngestionAnimation({
  onComplete,
}: {
  onComplete?: () => void;
}) {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev >= steps.length - 1) {
          clearInterval(timer);
          setTimeout(() => onComplete?.(), 1000);
          return prev;
        }
        return prev + 1;
      });
    }, 1500);
    return () => clearInterval(timer);
  }, [onComplete]);

  return (
    <div className="rounded-xl border-0 w-full h-[calc(100vh-11vh)] border-indigo-100 dark:border-indigo-800 bg-indigo-50/50 dark:bg-indigo-900/20 p-6 flex flex-col items-center justify-center min-h-[200px]">
      <div className="w-full max-w-xs space-y-6">
        {steps.map((step, index) => {
          const isActive = index === currentStep;
          const isCompleted = index < currentStep;
          const Icon = step.icon;

          return (
            <motion.div
              key={step.id}
              initial={{ opacity: 0.5, x: -10 }}
              animate={{
                opacity: isActive || isCompleted ? 1 : 0.3,
                x: 0,
                scale: isActive ? 1.05 : 1,
              }}
              className="flex items-center gap-3"
            >
              <div
                className={`
                h-8 w-8 rounded-full flex items-center justify-center border
                ${
                  isCompleted
                    ? "bg-indigo-600 border-indigo-600 text-white dark:bg-indigo-500 dark:border-indigo-500"
                    : isActive
                    ? "bg-white dark:bg-slate-800 border-indigo-600 dark:border-indigo-400 text-indigo-600 dark:text-indigo-400 ring-2 ring-indigo-200 dark:ring-indigo-800"
                    : "bg-white dark:bg-slate-800 border-gray-200 dark:border-slate-700 text-gray-300 dark:text-gray-600"
                }
              `}
              >
                {isCompleted ? (
                  <CheckCircle className="h-4 w-4" />
                ) : isActive ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Icon className="h-4 w-4" />
                )}
              </div>
              <span
                className={`text-sm font-medium ${
                  isActive
                    ? "text-indigo-900 dark:text-indigo-200"
                    : "text-gray-500 dark:text-gray-400"
                }`}
              >
                {step.label}
              </span>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
