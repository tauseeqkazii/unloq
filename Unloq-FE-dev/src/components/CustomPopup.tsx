import { useEffect } from "react";
import { X } from "lucide-react";
import { cn } from "../lib/utils";

interface CustomPopupProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children?: React.ReactNode;
  footer?: React.ReactNode;
  variant?: "default" | "destructive";
}

export function CustomPopup({
  isOpen,
  onClose,
  title,
  description,
  children,
  footer,
  variant = "default",
}: CustomPopupProps) {
// const overlayRef = useRef<HTMLDivElement>(null); // Not currently used

  // Close on Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    if (isOpen) document.addEventListener("keydown", handleEscape);
    return () => document.removeEventListener("keydown", handleEscape);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-slate-950/40 backdrop-blur-sm transition-opacity animate-in fade-in"
        onClick={onClose}
      />

      {/* Modal Content */}
      <div
        className={cn(
          "relative w-full max-w-md transform overflow-hidden rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 text-left shadow-xl transition-all animate-in zoom-in-95 slide-in-from-bottom-2",
          variant === "destructive" && "border-rose-100 dark:border-rose-900/30"
        )}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold leading-6 text-slate-900 dark:text-white">
            {title}
          </h3>
          <button
            onClick={onClose}
            className="rounded-full p-1 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-500 transition-colors focus:outline-none"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {description && (
          <p className="text-sm text-slate-500 dark:text-slate-400 mb-4">
            {description}
          </p>
        )}

        {children && <div className="mt-2">{children}</div>}

        {footer && (
          <div className="mt-6 flex flex-col-reverse sm:flex-row sm:justify-end gap-3">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
