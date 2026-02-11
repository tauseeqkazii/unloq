import axios from "axios";
import { globalEvents, EVENTS } from "./events";
import type {
  DashboardResponse,
  Session,
  ChatMessage,
  Recommendation,
  LedgerEntry,
  Signal,
} from "../types";

let activeRequests = 0;

const startLoading = () => {
  if (activeRequests === 0) {
    globalEvents.emit(EVENTS.API_LOADING_START);
  }
  activeRequests++;
};

const stopLoading = () => {
  activeRequests--;
  if (activeRequests <= 0) {
    activeRequests = 0;
    globalEvents.emit(EVENTS.API_LOADING_END);
  }
};

// Ensure this environment variable is set in your .env
const API_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

// Debug logging for API configuration
if (typeof window !== "undefined") {
  console.log("=== API CONFIGURATION ===");
  console.log("VITE_API_BASE_URL from env:", import.meta.env.VITE_API_BASE_URL);
  console.log("Final API_URL being used:", API_URL);
  console.log("=== END API CONFIG ===");
}

export const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request Interceptor: Automatically attach Token
apiClient.interceptors.request.use(
  (config) => {
    startLoading();
    const token = localStorage.getItem("token");
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    stopLoading();
    return Promise.reject(error);
  }
);

// Response Interceptor: Handle 401s gracefully
apiClient.interceptors.response.use(
  (response) => {
    stopLoading();
    return response;
  },
  (error) => {
    stopLoading();
    if (error.response?.status === 401) {
      console.warn("Unauthorized access - redirecting to login");
    }
    return Promise.reject(error);
  }
);

export const api = {
  // --- DASHBOARD ---
  getDashboard: async (): Promise<DashboardResponse> => {
    const response = await apiClient.get<DashboardResponse>(
      "/oakfield/dashboard"
    );
    return response.data;
  },

  // --- CHAT SESSIONS ---
  getSessions: async (): Promise<Session[]> => {
    try {
      const response = await apiClient.get<Session[]>("/chat/sessions");
      return response.data;
    } catch (error) {
      console.error("Failed to fetch sessions:", error);
      return [];
    }
  },

  createSession: async (title = "New Strategy Chat"): Promise<Session> => {
    const response = await apiClient.post<Session>("/chat/sessions", { title });
    return response.data;
  },

  getSessionHistory: async (sessionId: string): Promise<ChatMessage[]> => {
    const response = await apiClient.get<ChatMessage[]>(
      `/chat/sessions/${sessionId}/messages`
    );
    return response.data;
  },

  // --- APPROVALS & LEDGER ---
  getApprovals: async (): Promise<Recommendation[]> => {
    const response = await apiClient.get<Recommendation[]>(
      "/oakfield/approvals"
    );
    return response.data;
  },

  submitApprovalAction: async (
    id: string,
    action: "approve" | "reject"
  ): Promise<void> => {
    await apiClient.post(`/oakfield/approvals/${id}/action`, {
      action,
    });
  },

  getLedger: async (): Promise<LedgerEntry[]> => {
    const response = await apiClient.get<LedgerEntry[]>("/oakfield/ledger");
    return response.data;
  },

  // --- SIGNALS ---
  getSignals: async (): Promise<Signal[]> => {
    const response = await apiClient.get<Signal[]>("/oakfield/signals");
    return response.data;
  },

  deleteSession: async (id: string): Promise<void> => {
    await apiClient.delete(`/chat/sessions/${id}`);
  },

  renameSession: async (id: string, title: string): Promise<Session> => {
    const response = await apiClient.patch<Session>(`/chat/sessions/${id}`, {
      title,
    });
    return response.data;
  },

  // Expose raw client if needed
  client: apiClient,
};
