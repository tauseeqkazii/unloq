import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  MessageSquare,
  CheckSquare,
  FileText,
  X,
} from "lucide-react";
import { cn } from "../lib/utils";

interface SidebarProps {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

export default function Sidebar({ isOpen, setIsOpen }: SidebarProps) {
  const navItems = [
    { name: "Dashboard", href: "/", icon: LayoutDashboard },
    { name: "Strategist", href: "/strategist", icon: MessageSquare },
    { name: "Approvals", href: "/approvals", icon: CheckSquare },
    { name: "Impact Ledger", href: "/ledger", icon: FileText },
  ];

  return (
    <aside
      className={cn(
        "fixed inset-y-0 left-0 z-50 w-64 bg-[#0a0a0a] text-white transition-transform duration-300 ease-in-out lg:relative lg:translate-x-0 border-r border-[#1a1a1a]",
        !isOpen && "-translate-x-full lg:hidden"
      )}
    >
      <div className="flex h-16 items-center justify-between px-6 border-b border-[#1a1a1a] bg-[#060606]/80 backdrop-blur-sm">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-lg bg-gradient-to-tr from-indigo-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-indigo-500/20 hover:shadow-indigo-500/40 transition-shadow duration-300">
            <span className="text-white font-bold text-lg">O</span>
          </div>
          <div className="flex flex-col">
            <span className="text-xl font-bold tracking-tight text-white leading-none">
              Oakfield
            </span>
            <span className="text-[10px] font-medium text-indigo-400 uppercase tracking-wider mt-0.5">
              Strategy Desk
            </span>
          </div>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          className="lg:hidden text-[#8b8b8b] hover:text-white transition-colors"
        >
          <X className="h-6 w-6" />
        </button>
      </div>

      <div className="px-3 py-6">
        <div className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-[#8b8b8b]">
          Platform
        </div>
        <nav className="space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.name}
              to={item.href}
              className={({ isActive }) =>
                cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all duration-200",
                  isActive
                    ? "bg-indigo-600/15 text-indigo-400 border border-indigo-500/25 shadow-sm shadow-indigo-500/10"
                    : "text-[#8b8b8b] hover:bg-[#1a1a1a] hover:text-white hover:translate-x-0.5"
                )
              }
            >
              <item.icon className={cn("h-5 w-5", "opacity-70")} />
              {item.name}
            </NavLink>
          ))}
        </nav>
      </div>

      <div className="absolute bottom-0 w-full p-6 border-t border-[#1a1a1a] bg-[#060606]/50">
        <div className="flex items-center gap-3 mb-4">
          <div className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></div>
          <span className="text-xs text-[#8b8b8b]">System Operational</span>
        </div>

        <div className="flex items-center gap-0 pt-4 border-t border-[#1a1a1a]/50">
          <span className="text-[10px] text-[#8b8b8b] font-medium">
            Powered by
          </span>
          <img
            src="/unloq-logo.png"
            alt="Unloq"
            className="h-7 w-auto opacity-70 grayscale hover:grayscale-0 hover:opacity-100 transition-all duration-300 rounded px-1"
          />
        </div>
      </div>
    </aside>
  );
}
