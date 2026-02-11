import {
  useState,
  useCallback,
  type ReactNode,
} from "react";
import { X, CheckCircle, AlertCircle, Info } from "lucide-react";
import { cn } from "../lib/utils";

import type { Toast, ToastType } from "../types/context";
import { ToastContext } from "./ToastContextInstance";

export const ToastProvider: React.FC<{ children: ReactNode }> = ({
  children,
}) => {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((message: string, type: ToastType = "info") => {
    const id = Math.random().toString(36).substring(2, 9);
    setToasts((prev) => [...prev, { id, type, message }]);

    // Auto remove after 3 seconds
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id));
    }, 3000);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  return (
    <ToastContext.Provider value={{ toasts, addToast, removeToast }}>
      {children}
      <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={cn(
              "flex items-center gap-3 rounded-lg px-4 py-3 shadow-lg transition-all animate-in slide-in-from-right-full",
              toast.type === "success" &&
                "bg-emerald-50 text-emerald-800 border border-emerald-100",
              toast.type === "error" &&
                "bg-rose-50 text-rose-800 border border-rose-100",
              toast.type === "info" && "bg-slate-800 text-white"
            )}
          >
            {toast.type === "success" && <CheckCircle className="h-5 w-5" />}
            {toast.type === "error" && <AlertCircle className="h-5 w-5" />}
            {toast.type === "info" && <Info className="h-5 w-5" />}
            <p className="text-sm font-medium">{toast.message}</p>
            <button
              onClick={() => removeToast(toast.id)}
              className="ml-auto text-current opacity-70 hover:opacity-100"
            >
              <X className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
};
