import React, { useState, useEffect, useCallback } from "react";
import { apiClient as apiCall } from "../lib/api";
import { useToast } from "./useToast";

import type { User } from "../types/context";
import { AuthContext } from "./AuthContextInstance";

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const { addToast } = useToast();

  const login = useCallback((token: string, userData: User) => {
    localStorage.setItem("token", token);
    localStorage.setItem("user", JSON.stringify(userData));
    setUser(userData);
    addToast(`Welcome back, ${userData.full_name || "User"}!`, "success");
  }, [addToast]);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      // Optimistic user load
      setUser({ email: "user@example.com" });
      const storedUser = localStorage.getItem("user");
      if (storedUser) {
        setUser(JSON.parse(storedUser));
      }
    } else if (import.meta.env.DEV) {
      // Auto-login for local development
      const demoUser = { email: "demo@unloq.ai", full_name: "Demo User" };
      login("demo-token", demoUser);
    }
    setIsLoading(false);
  }, [login]);

  const logout = async () => {
    try {
      await apiCall.post("/auth/logout");
    } catch {
      console.error("Logout failed");
    } finally {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      setUser(null);
      addToast("Successfully logged out", "info");
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};
