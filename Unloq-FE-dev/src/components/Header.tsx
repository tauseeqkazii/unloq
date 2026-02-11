import { Menu, Sun, Moon } from "lucide-react";
import { useAuth } from "../context/useAuth";
import { useTheme } from "../context/useTheme";

interface HeaderProps {
  setSidebarOpen: (open: boolean) => void;
}

export default function Header({ setSidebarOpen }: HeaderProps) {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const initials = user?.full_name
    ? user.full_name
        .split(" ")
        .map((n: string) => n[0])
        .join("")
        .substring(0, 2)
        .toUpperCase()
    : user?.email.substring(0, 2).toUpperCase() || "DU";

  const handleLogout = async () => {
    await logout();
  };

  return (
    <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white/80 px-6 backdrop-blur-md sticky top-0 z-40 dark:bg-[#111111]/90 dark:border-[#252525] transition-colors duration-300">
      <div className="flex items-center gap-4">
        <button
          onClick={() => setSidebarOpen(true)}
          className="lg:hidden text-slate-500 hover:text-slate-700 transition-colors"
        >
          <Menu className="h-6 w-6" />
        </button>
      </div>

      <div className="flex items-center gap-4">
        <button
          onClick={toggleTheme}
          className="p-2 text-slate-500 hover:bg-slate-100 hover:text-indigo-500 rounded-full transition-all duration-200 dark:text-slate-400 dark:hover:bg-[#1a1a1a] dark:hover:text-indigo-400 hover:shadow-md"
          aria-label="Toggle theme"
        >
          {theme === "light" ? (
            <Moon className="h-5 w-5" />
          ) : (
            <Sun className="h-5 w-5" />
          )}
        </button>

        <div className="flex items-center gap-3 pl-1 relative group">
          <div className="text-right hidden sm:block">
            <p className="text-sm font-medium text-slate-900 dark:text-white leading-none">
              {user?.full_name || user?.email}
            </p>
            <p className="text-xs text-slate-500 mt-1">
              Chief Strategy Officer
            </p>
          </div>
          <button
            className="h-8 w-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm shadow-md ring-2 ring-white dark:ring-[#252525] cursor-pointer hover:shadow-lg hover:scale-110 transition-all duration-200 relative"
            aria-label="User menu"
          >
            {initials}
          </button>

          <div className="absolute right-0 top-full mt-2 w-48 origin-top-right rounded-md bg-white dark:bg-[#1a1a1a] py-1 shadow-lg ring-1 ring-black ring-opacity-5 dark:ring-[#252525] focus:outline-none opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
            <div className="px-4 py-2 border-b border-gray-100 dark:border-slate-700">
              <p className="text-sm text-gray-900 dark:text-white font-medium truncate">
                {user?.full_name}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                {user?.email}
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="block w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-slate-700 cursor-pointer"
            >
              Sign out
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
