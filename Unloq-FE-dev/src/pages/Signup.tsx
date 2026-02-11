import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { apiClient as api } from "../lib/api";
import { motion } from "framer-motion";
import {
  Eye,
  EyeOff,
  Lock,
  Mail,
  User,
  ArrowRight,
  Sparkles,
} from "lucide-react";

export default function Signup() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await api.post("/auth/signup", {
        email,
        password,
        full_name: fullName,
      });
      navigate("/login");
    } catch (err: unknown) {
      console.error("=== SIGNUP ERROR DETAILS ===");
      console.error("Error object:", err);
      console.error("Error type:", typeof err);

      // Log network request details
      console.error(
        "Request URL:",
        `${
          import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1"
        }/auth/signup`
      );
      console.error("Request payload:", {
        email,
        password,
        full_name: fullName,
      });

      // Handle different types of errors
      if (err && typeof err === "object") {
        const errorObj = err as {
          response?: {
            status?: number;
            statusText?: string;
            data?: {
              detail?: string;
              message?: string;
              error?: string;
            };
          };
          message?: string;
          request?: unknown;
        };

        console.error("Response status:", errorObj.response?.status);
        console.error("Response status text:", errorObj.response?.statusText);
        console.error("Response data:", errorObj.response?.data);

        // More specific error handling
        if (errorObj.response?.status === 0) {
          setError(
            "Network error: Cannot connect to the server. Please check your internet connection."
          );
        } else if (errorObj.response?.status === 404) {
          setError("API endpoint not found. Please contact support.");
        } else if (errorObj.response?.status === 500) {
          setError("Server error. Please try again later.");
        } else if (errorObj.response?.data?.detail) {
          setError(errorObj.response.data.detail);
        } else if (errorObj.response?.data?.message) {
          setError(errorObj.response.data.message);
        } else if (errorObj.response?.data?.error) {
          setError(errorObj.response.data.error);
        } else if (errorObj.message) {
          setError(errorObj.message);
        } else if (errorObj.response) {
          setError(
            `Server responded with status ${errorObj.response.status}. Please try again.`
          );
        } else {
          setError(
            "Signup failed. Please check your connection and try again."
          );
        }
      } else {
        setError("Signup failed. Please try again.");
      }

      console.error("=== END ERROR DETAILS ===");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex w-full bg-[#020617] text-slate-100 font-sans selection:bg-indigo-500/30">
      {/* Left Panel - Visuals */}
      <div className="hidden lg:flex w-1/2 relative overflow-hidden bg-slate-900 items-center justify-center">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,var(--tw-gradient-stops))] from-violet-500/20 via-slate-900 to-slate-900"></div>
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-100 contrast-150"></div>

        <div className="relative z-10 max-w-lg px-12">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <div className="h-12 w-12 rounded-xl bg-gradient-to-tr from-violet-500 to-fuchsia-500 flex items-center justify-center mb-8 shadow-lg shadow-violet-500/20">
              <Sparkles className="text-white h-6 w-6" />
            </div>
            <h1 className="text-4xl font-bold tracking-tight mb-4 font-display text-white">
              Welcome to <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-violet-400 to-fuchsia-400">
                Oakfield Strategy Desk
              </span>
            </h1>
            <div className="flex items-center gap-0 mb-6">
              <span className="text-slate-400 text-lg">powered by</span>
              <img
                src="/unloq-logo.png"
                alt="Unloq Logo"
                className="h-14 w-auto rounded"
              />
            </div>
            <p className="text-slate-400 text-lg leading-relaxed">
              Experience the latest generation of Strategic Intelligence by
              Unloq®.
              <br />
              Secure, powerful and personalised to achieve your strategy goals.
            </p>
          </motion.div>
        </div>
      </div>

      {/* Right Panel - Signup Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 relative">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_right,var(--tw-gradient-stops))] from-violet-900/10 via-transparent to-transparent lg:hidden"></div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md space-y-8 relative z-10"
        >
          <div className="text-center lg:text-left">
            <Link to="/" className="lg:hidden inline-block mb-8">
              <div className="h-10 w-10 rounded-lg bg-gradient-to-tr from-violet-500 to-fuchsia-500 flex items-center justify-center shadow-lg shadow-violet-500/20 mx-auto">
                <Sparkles className="text-white h-5 w-5" />
              </div>
            </Link>
            <h2 className="text-3xl font-bold tracking-tight font-display text-white">
              Create Account
            </h2>
            <p className="mt-2 text-slate-400">
              Already a member?{" "}
              <Link
                to="/login"
                className="font-medium text-indigo-400 hover:text-indigo-300 transition-colors duration-200"
              >
                Sign in instead
              </Link>
            </p>
          </div>

          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            <div className="space-y-4">
              <div className="group relative">
                <label className="block text-xs font-medium text-slate-500 mb-1 ml-1 uppercase tracking-wider">
                  Full Name
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <User className="h-5 w-5 text-slate-500 group-focus-within:text-violet-400 transition-colors" />
                  </div>
                  <input
                    type="text"
                    className="block w-full rounded-xl border-0 bg-slate-800/50 py-3 pl-10 text-white shadow-sm ring-1 ring-inset ring-slate-700 placeholder:text-slate-600 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm sm:leading-6 transition-all duration-200 hover:bg-slate-800"
                    placeholder="John Doe"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                  />
                </div>
              </div>

              <div className="group relative">
                <label className="block text-xs font-medium text-slate-500 mb-1 ml-1 uppercase tracking-wider">
                  Email Address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-slate-500 group-focus-within:text-violet-400 transition-colors" />
                  </div>
                  <input
                    type="email"
                    required
                    className="block w-full rounded-xl border-0 bg-slate-800/50 py-3 pl-10 text-white shadow-sm ring-1 ring-inset ring-slate-700 placeholder:text-slate-600 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm sm:leading-6 transition-all duration-200 hover:bg-slate-800"
                    placeholder="you@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                  />
                </div>
              </div>

              <div className="group relative">
                <label className="block text-xs font-medium text-slate-500 mb-1 ml-1 uppercase tracking-wider">
                  Password
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="h-5 w-5 text-slate-500 group-focus-within:text-violet-400 transition-colors" />
                  </div>
                  <input
                    type={showPassword ? "text" : "password"}
                    required
                    className="block w-full rounded-xl border-0 bg-slate-800/50 py-3 pl-10 pr-10 text-white shadow-sm ring-1 ring-inset ring-slate-700 placeholder:text-slate-600 focus:ring-2 focus:ring-inset focus:ring-violet-500 sm:text-sm sm:leading-6 transition-all duration-200 hover:bg-slate-800"
                    placeholder="••••••••"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                  />
                  <button
                    type="button"
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                    onClick={() => setShowPassword(!showPassword)}
                  >
                    {showPassword ? (
                      <EyeOff className="h-5 w-5 text-slate-500 hover:text-slate-300 cursor-pointer transition-colors" />
                    ) : (
                      <Eye className="h-5 w-5 text-slate-500 hover:text-slate-300 cursor-pointer transition-colors" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="rounded-lg bg-red-500/10 border border-red-500/20 p-3 text-sm text-red-400 text-center"
              >
                {error}
              </motion.div>
            )}

            <div>
              <button
                type="submit"
                disabled={loading}
                className="group relative flex w-full justify-center items-center gap-2 rounded-xl bg-violet-600 px-4 py-3.5 text-sm font-semibold text-white shadow-lg shadow-violet-500/25 hover:bg-violet-500 hover:shadow-violet-500/40 transition-all duration-300 disabled:opacity-70 disabled:cursor-not-allowed overflow-hidden"
              >
                {loading ? (
                  <svg
                    className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                    ></circle>
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    ></path>
                  </svg>
                ) : (
                  <>
                    Create Account
                    <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
                <div className="absolute inset-0 -translate-x-full group-hover:animate-[shimmer_1.5s_infinite] bg-gradient-to-r from-transparent via-white/10 to-transparent z-10"></div>
              </button>
            </div>
          </form>
        </motion.div>
      </div>
    </div>
  );
}
