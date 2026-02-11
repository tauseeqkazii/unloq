export interface User {
  email: string;
  full_name?: string;
}

export interface AuthContextType {
  user: User | null;
  login: (token: string, userData: User) => void;
  logout: () => Promise<void>;
  isLoading: boolean;
}

export type Theme = "dark" | "light";

export interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

export type ToastType = "success" | "error" | "info";

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
}

export interface ToastContextType {
  toasts: Toast[];
  addToast: (message: string, type: ToastType) => void;
  removeToast: (id: string) => void;
}
