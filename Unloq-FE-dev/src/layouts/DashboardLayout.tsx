import { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Header from "../components/Header";

export default function DashboardLayout() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-[#0a0a0a] text-slate-900 dark:text-[#e4e4e7] font-sans transition-colors duration-300">
      <Sidebar isOpen={isSidebarOpen} setIsOpen={setIsSidebarOpen} />

      <div className="flex flex-1 flex-col overflow-hidden relative">
        <Header setSidebarOpen={setIsSidebarOpen} />

        <main className="flex-1 overflow-auto">
          <div className="mx-auto max-w-7xl animate-in fade-in duration-500 slide-in-from-bottom-2">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
