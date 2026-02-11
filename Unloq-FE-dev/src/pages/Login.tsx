import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import { apiClient as api } from "../lib/api";
import { motion } from "framer-motion";
import { Eye, EyeOff, Lock, Mail, ArrowRight, Sparkles } from "lucide-react";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const response = await api.post("/auth/login", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });
      const { access_token } = response.data as { access_token: string };

      login(access_token, { email });
      navigate("/");
    } catch (err: unknown) {
      setError(
        (err as { response?: { data?: { detail?: string } } }).response?.data
          ?.detail || "Invalid credentials. Please try again."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex w-full bg-[#020617] text-slate-100 font-sans selection:bg-indigo-500/30">
      {/* Left Panel - Abstract Visuals */}
      <div className="hidden lg:flex w-1/2 relative overflow-hidden bg-slate-900 items-center justify-center">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,var(--tw-gradient-stops))] from-indigo-500/20 via-slate-900 to-slate-900"></div>
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-100 contrast-150"></div>

        <div className="relative z-10 max-w-lg px-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <div className="h-12 w-12 rounded-xl bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center mb-8 shadow-lg shadow-indigo-500/20">
              <Sparkles className="text-white h-6 w-6" />
            </div>
            <h1 className="text-4xl font-bold tracking-tight mb-4 font-display text-white">
              Welcome to <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-cyan-400">
                Oakfield Strategy Desk
              </span>
            </h1>
            <div className="flex items-center gap-0 mb-6">
              <span className="text-slate-400 text-lg">powered by</span>
              <img
                src="/unloq-logo.png"
                alt="Unloq Logo"
                className="h-12 w-auto rounded"
              />
            </div>
            <p className="text-slate-400 text-lg leading-relaxed">
              Experience the latest generation of Strategic Intelligence by
              Unloq®.
              <br />
              Secure, powerful and personalised to achieve your strategy goals.
            </p>
          </motion.div>

          {/* Floating elements animation */}
          <motion.div
            animate={{ y: [0, -10, 0] }}
            transition={{ repeat: Infinity, duration: 5, ease: "easeInOut" }}
            className="absolute -top-20 -right-20 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl"
          />
          <motion.div
            animate={{ y: [0, 15, 0] }}
            transition={{
              repeat: Infinity,
              duration: 7,
              ease: "easeInOut",
              delay: 1,
            }}
            className="absolute bottom-10 left-10 w-48 h-48 bg-violet-500/10 rounded-full blur-3xl"
          />
        </div>
      </div>

      {/* Right Panel - Login Form */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-8 relative">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_left,var(--tw-gradient-stops))] from-indigo-900/10 via-transparent to-transparent lg:hidden"></div>

        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md space-y-8 relative z-10"
        >
          <div className="text-center lg:text-left">
            <Link to="/" className="lg:hidden inline-block mb-8">
              <div className="h-10 w-10 rounded-lg bg-gradient-to-tr from-indigo-500 to-violet-500 flex items-center justify-center shadow-lg shadow-indigo-500/20 mx-auto">
                <Sparkles className="text-white h-5 w-5" />
              </div>
            </Link>
            <h2 className="text-3xl font-bold tracking-tight font-display text-white">
              Sign in
            </h2>
            <p className="mt-2 text-slate-400">
              Don't have an account?{" "}
              <Link
                to="/signup"
                className="font-medium text-indigo-400 hover:text-indigo-300 transition-colors duration-200"
              >
                Create one now
              </Link>
            </p>
          </div>

          <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
            <div className="space-y-4">
              <div className="group relative">
                <label className="block text-xs font-medium text-slate-500 mb-1 ml-1 uppercase tracking-wider">
                  Email Address
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="h-5 w-5 text-slate-500 group-focus-within:text-indigo-400 transition-colors" />
                  </div>
                  <input
                    type="email"
                    required
                    className="block w-full rounded-xl border-0 bg-slate-800/50 py-3 pl-10 text-white shadow-sm ring-1 ring-inset ring-slate-700 placeholder:text-slate-600 focus:ring-2 focus:ring-inset focus:ring-indigo-500 sm:text-sm sm:leading-6 transition-all duration-200 hover:bg-slate-800"
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
                    <Lock className="h-5 w-5 text-slate-500 group-focus-within:text-indigo-400 transition-colors" />
                  </div>
                  <input
                    type={showPassword ? "text" : "password"}
                    required
                    className="block w-full rounded-xl border-0 bg-slate-800/50 py-3 pl-10 pr-10 text-white shadow-sm ring-1 ring-inset ring-slate-700 placeholder:text-slate-600 focus:ring-2 focus:ring-inset focus:ring-indigo-500 sm:text-sm sm:leading-6 transition-all duration-200 hover:bg-slate-800"
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
                className="group relative flex w-full justify-center items-center gap-2 rounded-xl bg-indigo-600 px-4 py-3.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/25 hover:bg-indigo-500 hover:shadow-indigo-500/40 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600 transition-all duration-300 disabled:opacity-70 disabled:cursor-not-allowed overflow-hidden"
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
                    Sign in
                    <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                  </>
                )}

                <div className="absolute inset-0 -translate-x-full group-hover:animate-[shimmer_1.5s_infinite] bg-gradient-to-r from-transparent via-white/10 to-transparent z-10"></div>
              </button>
            </div>
          </form>

          <div className="mt-8 text-center text-xs text-slate-600">
            Protected by Oakfield Secure Auth. <br />
            By continuing, you agree to our Terms of Service and Privacy Policy.
          </div>
        </motion.div>
      </div>
    </div>
  );
}
