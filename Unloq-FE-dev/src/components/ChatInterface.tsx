import {
  useState,
  useEffect,
  useRef,
  type FormEvent,
  type MouseEvent,
  type KeyboardEvent,
} from "react";
import {
  Send,
  Plus,
  MessageSquare,
  Loader2,
  Bot,
  User,
  Trash2,
  Pencil,
  Check,
  X,
  ArrowDown,
} from "lucide-react";
import { useLocation, useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { cn } from "../lib/utils";
import { BlockRenderer, type Block } from "./chat/BlockRenderer";
import type { ChatAction } from "../types";
import { CustomPopup } from "./CustomPopup";

// --- STRICT TYPES ---

interface Session {
  session_id: string;
  title: string;
  created_at: string;
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

interface LLMResponse {
  type: string;
  blocks?: Block[];
  text?: string;
}

interface ApiError {
  response?: {
    status: number;
  };
}

const generateId = () => {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
};

const safeParseJSON = (text: string): LLMResponse | null => {
  const trimmed = text.trim();
  try {
    const data = JSON.parse(trimmed);
    if (data && data.blocks) return data as LLMResponse;
  } catch {
    /* continue */
  }

  // 2. Try removing markdown code fences
  try {
    const clean = trimmed.replace(/^```json\s*/, "").replace(/\s*```$/, "");
    const data = JSON.parse(clean);
    if (data && data.blocks) return data as LLMResponse;
  } catch {
    /* continue */
  }

  // 3. Brute force extraction
  try {
    const start = trimmed.indexOf("{");
    const end = trimmed.lastIndexOf("}");
    if (start !== -1 && end > start) {
      const jsonStr = trimmed.substring(start, end + 1);
      const data = JSON.parse(jsonStr);
      if (data && data.blocks) return data as LLMResponse;
    }
  } catch {
    /* continue */
  }

  return null;
};

const VALID_ROUTES = [
  "/dashboard",
  "/approvals",
  "/ledger",
  "/contracts",
  "/copilot",
  "/connectors",
];

export default function ChatInterface() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [, setActionLoading] = useState<string | null>(null);

  // Scroll & UI State
  const [showScrollButton, setShowScrollButton] = useState(false);
  const [autoScroll, setAutoScroll] = useState(true);

  // Edit/Delete State
  const [editingSessionId, setEditingSessionId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");
  const [sessionToDelete, setSessionToDelete] = useState<string | null>(null);

  // Refs
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const isMounted = useRef(true);
  const intentHandled = useRef(false);
  const abortControllerRef = useRef<AbortController | null>(null);

  const location = useLocation();
  const navigate = useNavigate();

  const activeSessionIdRef = useRef<string | null>(null);

  useEffect(() => {
    isMounted.current = true;
    return () => {
      isMounted.current = false;
      // Abort any pending requests on unmount
      if (abortControllerRef.current) abortControllerRef.current.abort();
    };
  }, []);

  // Keep ref in sync with state for async operations
  useEffect(() => {
    activeSessionIdRef.current = activeSessionId;
  }, [activeSessionId]);

  // 1. Unified Initialization
  useEffect(() => {
    const init = async () => {
      try {
        if (location.state?.initialQuery && !intentHandled.current) {
          intentHandled.current = true;
          const query = location.state.initialQuery as string;
          window.history.replaceState({}, document.title);
          const existing = await api.getSessions();
          if (isMounted.current) setSessions(existing);
          await handleNewChat(query);
          return;
        }

        if (!intentHandled.current) {
          const data = await api.getSessions();
          if (isMounted.current) {
            setSessions(data);
            if (data.length > 0 && !activeSessionId) {
              selectSession(data[0].session_id);
            }
          }
        }
      } catch (e) {
        console.error("Init failed", e);
      }
    };
    init();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // --- SCROLL LOGIC ---
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    setAutoScroll(true);
    setShowScrollButton(false);
  };

  const handleScroll = () => {
    if (!scrollContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } =
      scrollContainerRef.current;

    // If user is near bottom (within 100px), enable auto-scroll
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 100;

    setAutoScroll(isAtBottom);
    setShowScrollButton(!isAtBottom);
  };

  // Auto-scroll effect
  useEffect(() => {
    if (autoScroll) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, autoScroll]); // Updates on stream chunks IF autoScroll is true

  // --- CORE LOGIC ---

  const abortCurrentRequest = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  };

  const handleNewChat = async (initialPrompt?: string) => {
    if (isLoading && !initialPrompt) return; // Allow if forcing new prompt

    abortCurrentRequest();
    setMessages([]);
    setActiveSessionId(null);
    setIsLoading(true);

    try {
      const title = initialPrompt
        ? initialPrompt.substring(0, 30) + "..."
        : "New Strategy Chat";

      const newSession = await api.createSession(title);

      if (isMounted.current) {
        setSessions((prev) => [newSession, ...prev]);
        setActiveSessionId(newSession.session_id);
      }

      if (initialPrompt) {
        await executeSendMessage(newSession.session_id, initialPrompt);
      } else {
        setIsLoading(false);
      }
    } catch (e) {
      console.error(e);
      if (isMounted.current) setIsLoading(false);
    }
  };

  const selectSession = async (id: string) => {
    if (editingSessionId === id || activeSessionId === id) return;

    abortCurrentRequest(); // Stop any pending stream in previous chat
    setActiveSessionId(id);
    setIsLoading(true);
    setMessages([]);
    setAutoScroll(true); // Reset scroll for new chat

    try {
      const history = await api.getSessionHistory(id);
      if (isMounted.current) {
        setMessages(history);
        // Small timeout to allow render before scrolling
        setTimeout(scrollToBottom, 50);
      }
    } catch (e) {
      const error = e as ApiError;
      if (error?.response?.status === 404 && isMounted.current) {
        setSessions((prev) => prev.filter((s) => s.session_id !== id));
      }
    } finally {
      if (isMounted.current) setIsLoading(false);
    }
  };

  // --- ACTIONS ---
  const handleBlockAction = async (action: ChatAction) => {
    const actionKey = action.type === "api" ? action.action_id : action.label;
    setActionLoading(actionKey);

    try {
      if (action.type === "navigation" && action.route) {
        if (VALID_ROUTES.includes(action.route)) {
          navigate(action.route);
        } else {
          setMessages((prev) => [
            ...prev,
            {
              id: generateId(),
              role: "assistant",
              content: `ℹ️ **Simulation Note**: The page \`${action.route}\` is a placeholder.`,
            },
          ]);
        }
      } else if (action.type === "api") {
        await new Promise((r) => setTimeout(r, 600));
        if (action.action_id) {
          await api.submitApprovalAction(action.action_id, "approve");
        }
        setMessages((prev) => [
          ...prev,
          {
            id: generateId(),
            role: "assistant",
            content: `✅ **Success**: ${action.label} executed successfully.`,
          },
        ]);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: generateId(),
          role: "assistant",
          content: `⚠️ **Error**: Failed to execute "${action.label}".`,
        },
      ]);
    } finally {
      if (isMounted.current) setActionLoading(null);
    }
  };

  // --- DELETE & RENAME ---
  const triggerDelete = (id: string) => setSessionToDelete(id);

  const confirmDelete = async () => {
    if (!sessionToDelete) return;
    try {
      await api.deleteSession(sessionToDelete);
      if (isMounted.current) {
        setSessions((prev) =>
          prev.filter((s) => s.session_id !== sessionToDelete),
        );
        if (activeSessionId === sessionToDelete) {
          setActiveSessionId(null);
          setMessages([]);
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      if (isMounted.current) setSessionToDelete(null);
    }
  };

  const startEditing = (e: MouseEvent, session: Session) => {
    e.stopPropagation();
    setEditingSessionId(session.session_id);
    setEditTitle(session.title);
  };

  const cancelEditing = (e?: MouseEvent | KeyboardEvent) => {
    e?.stopPropagation();
    setEditingSessionId(null);
    setEditTitle("");
  };

  const saveTitle = async (e?: MouseEvent | KeyboardEvent) => {
    e?.stopPropagation();
    if (!editingSessionId || !editTitle.trim()) return;
    try {
      const sid = editingSessionId;
      setSessions((prev) =>
        prev.map((s) =>
          s.session_id === sid ? { ...s, title: editTitle } : s,
        ),
      );
      setEditingSessionId(null);
      await api.renameSession(sid, editTitle);
    } catch (error) {
      console.error(error);
    }
  };

  const executeSendMessage = async (sessionId: string, text: string) => {
    const userMsg: Message = { id: generateId(), role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);
    setAutoScroll(true); // Always scroll on new message send

    // Setup AbortController
    abortControllerRef.current = new AbortController();
    const signal = abortControllerRef.current.signal;

    try {
      const response = await fetch(
        `${
          import.meta.env.VITE_API_BASE_URL
        }/chat/sessions/${sessionId}/message`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token")}`,
          },
          body: JSON.stringify({ content: text }),
          signal, // Attach signal
        },
      );

      if (!response.body) throw new Error("No response body");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      const assistantMsgId = generateId();

      setMessages((prev) => [
        ...prev,
        { id: assistantMsgId, role: "assistant", content: "" },
      ]);

      let fullContent = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        if (!isMounted.current) break;

        const chunk = decoder.decode(value, { stream: true });
        fullContent += chunk;

        setMessages((prev) => {
          // If we switched sessions, don't update state for the old session
          if (activeSessionIdRef.current !== sessionId) return prev;

          const newHistory = [...prev];
          const lastIndex = newHistory.length - 1;
          if (
            newHistory[lastIndex] &&
            newHistory[lastIndex].id === assistantMsgId
          ) {
            newHistory[lastIndex] = {
              ...newHistory[lastIndex],
              content: fullContent,
            };
          }
          return newHistory;
        });
      }

      if (isMounted.current && activeSessionIdRef.current === sessionId) {
        api.getSessions().then((data) => {
          if (isMounted.current) setSessions(data);
        });
      }
    } catch (err: unknown) {
      if (err instanceof Error && err.name === "AbortError") {
        console.log("Stream aborted");
      } else {
        setMessages((prev) => [
          ...prev,
          {
            id: generateId(),
            role: "assistant",
            content: "⚠️ Connection Error.",
          },
        ]);
      }
    } finally {
      if (isMounted.current && activeSessionIdRef.current === sessionId)
        setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  const onFormSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    setIsLoading(true);
    const textToSend = input;
    setInput("");

    try {
      let currentId = activeSessionId;
      if (!currentId) {
        const newSession = await api.createSession(
          textToSend.substring(0, 30) + "...",
        );
        if (isMounted.current) {
          setSessions((prev) => [newSession, ...prev]);
          setActiveSessionId(newSession.session_id);
          currentId = newSession.session_id;
        }
      }
      if (currentId) await executeSendMessage(currentId, textToSend);
    } catch (error) {
      console.error(error);
      if (isMounted.current) setIsLoading(false);
    }
  };

  return (
    <>
      <div className="flex h-[calc(100vh-80px)] bg-white dark:bg-[#1a1a2e] overflow-hidden rounded-xl border border-slate-200 dark:border-[#33334d] shadow-sm mt-4">
        {/* SIDEBAR */}
        <div className="w-72 bg-slate-50 dark:bg-[#1a1a2e]/80 border-r border-slate-200 dark:border-[#33334d] flex flex-col">
          <div className="p-4 border-b border-slate-200 dark:border-[#33334d]">
            <button
              onClick={() => handleNewChat()}
              disabled={isLoading}
              className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 text-white py-2.5 rounded-lg text-sm font-medium transition-colors shadow-sm disabled:opacity-50"
            >
              <Plus className="h-4 w-4" /> New Strategy Chat
            </button>
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {sessions.map((s) => (
              <div
                key={s.session_id}
                className={cn(
                  "group relative flex items-center justify-between rounded-lg px-2 py-2 transition-all duration-200 cursor-pointer",
                  activeSessionId === s.session_id
                    ? "bg-white dark:bg-[#2a2a45] shadow-sm border border-slate-200 dark:border-[#33334d]"
                    : "hover:bg-slate-100 dark:hover:bg-[#2a2a45]/70",
                )}
                onClick={() => selectSession(s.session_id)}
              >
                {editingSessionId === s.session_id ? (
                  <div
                    className="flex items-center w-full gap-1"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <input
                      autoFocus
                      className="flex-1 min-w-0 bg-white dark:bg-[#1a1a2e] border border-indigo-300 dark:border-indigo-700 rounded px-2 py-1 text-xs focus:outline-none"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") saveTitle(e);
                        if (e.key === "Escape") {
                          e.stopPropagation();
                          setEditingSessionId(null);
                        }
                      }}
                    />
                    <button
                      onClick={saveTitle}
                      className="p-1 text-emerald-500 hover:bg-emerald-100 rounded"
                    >
                      <Check className="h-3 w-3" />
                    </button>
                    <button
                      onClick={cancelEditing}
                      className="p-1 text-slate-400 hover:bg-slate-200 rounded"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </div>
                ) : (
                  <>
                    <div
                      className={cn(
                        "flex items-center gap-3 flex-1 min-w-0 text-left px-2",
                        activeSessionId === s.session_id
                          ? "text-indigo-600 dark:text-indigo-400 font-medium"
                          : "text-slate-600 dark:text-slate-400",
                      )}
                    >
                      <MessageSquare className="h-4 w-4 shrink-0 opacity-70" />
                      <span className="truncate text-sm font-medium">
                        {s.title}
                      </span>
                    </div>
                    <div className="hidden group-hover:flex items-center gap-1 pl-2">
                      <button
                        onClick={(e) => startEditing(e, s)}
                        className="p-1.5 hover:bg-slate-200 rounded text-slate-400"
                      >
                        <Pencil className="h-3 w-3" />
                      </button>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          triggerDelete(s.session_id);
                        }}
                        className="p-1.5 hover:bg-rose-100 rounded text-slate-400 hover:text-rose-500"
                      >
                        <Trash2 className="h-3 w-3" />
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* CHAT AREA */}
        <div className="flex-1 flex flex-col relative bg-white dark:bg-[#1a1a2e]">
          <div
            ref={scrollContainerRef}
            onScroll={handleScroll}
            className="flex-1 overflow-y-auto p-6 space-y-8 scroll-smooth"
          >
            {messages.length === 0 && !isLoading && (
              <div className="flex flex-col items-center justify-center h-full text-center opacity-60 space-y-4">
                <Bot className="h-12 w-12 text-indigo-600" />
                <h3 className="text-lg font-semibold text-slate-800 dark:text-white">
                  Oakfield Strategy Engine
                </h3>
              </div>
            )}

            {messages.length === 0 && isLoading && (
              <div className="flex flex-col items-center justify-center h-full space-y-4 animate-in fade-in duration-500">
                <Loader2 className="h-8 w-8 animate-spin text-indigo-600 opacity-50" />
                <p className="text-sm text-slate-400 font-medium">
                  Loading conversation...
                </p>
              </div>
            )}

            {messages.map((m) => (
              <div
                key={m.id}
                className={cn(
                  "flex gap-4 animate-in fade-in slide-in-from-bottom-2",
                  m.role === "user" ? "flex-row-reverse" : "",
                )}
              >
                <div
                  className={cn(
                    "w-9 h-9 rounded-full flex items-center justify-center shrink-0 border shadow-sm",
                    m.role === "user"
                      ? "bg-slate-100 dark:bg-slate-800"
                      : "bg-indigo-600 text-white",
                  )}
                >
                  {m.role === "user" ? (
                    <User className="h-5 w-5" />
                  ) : (
                    <Bot className="h-5 w-5" />
                  )}
                </div>
                <div
                  className={cn(
                    "max-w-[85%] rounded-2xl p-5 text-sm leading-relaxed shadow-sm w-full",
                    m.role === "user"
                      ? "bg-indigo-600 text-white rounded-tr-sm"
                      : "bg-white dark:bg-[#22223a] border border-slate-100 dark:border-[#33334d] rounded-tl-sm",
                  )}
                >
                  {m.role === "assistant" ? (
                    (() => {
                      const jsonData = safeParseJSON(m.content);
                      if (jsonData && jsonData.blocks) {
                        return (
                          <BlockRenderer
                            blocks={jsonData.blocks}
                            onAction={handleBlockAction}
                          />
                        );
                      }
                      const trimmed = m.content.trim();
                      if (
                        trimmed.startsWith("{") ||
                        trimmed.startsWith("```json")
                      ) {
                        return (
                          <div className="flex items-center gap-3 py-4 px-2 text-slate-500 animate-pulse">
                            <Loader2 className="h-4 w-4 animate-spin text-indigo-500" />
                            <span className="text-xs font-medium uppercase tracking-wide">
                              Generating Visualization...
                            </span>
                          </div>
                        );
                      }
                      return (
                        <div className="whitespace-pre-wrap">{m.content}</div>
                      );
                    })()
                  ) : (
                    <div className="whitespace-pre-wrap font-medium">
                      {m.content}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isLoading &&
              messages.length > 0 &&
              messages[messages.length - 1].role === "user" && (
                <div className="flex gap-4 animate-in fade-in slide-in-from-bottom-2">
                  <div className="w-9 h-9 rounded-full flex items-center justify-center shrink-0 border shadow-sm bg-indigo-600 text-white">
                    <Bot className="h-5 w-5" />
                  </div>
                  <div className="max-w-[85%] rounded-2xl p-5 text-sm leading-relaxed shadow-sm w-full bg-white dark:bg-[#22223a] border border-slate-100 dark:border-[#33334d] rounded-tl-sm">
                    <div className="flex items-center gap-3">
                      <Loader2 className="h-4 w-4 animate-spin text-indigo-600" />
                      <span className="text-slate-500 font-medium">
                        Strategist is thinking...
                      </span>
                    </div>
                  </div>
                </div>
              )}
            <div ref={messagesEndRef} />
          </div>

          {/* Floating Scroll Button */}
          {showScrollButton && (
            <button
              onClick={scrollToBottom}
              className="absolute bottom-24 right-8 bg-white dark:bg-[#2a2a45] p-2 rounded-full shadow-lg border border-slate-200 dark:border-[#33334d] hover:bg-slate-50 dark:hover:bg-[#33335a] transition-all animate-in fade-in zoom-in"
            >
              <ArrowDown className="h-5 w-5 text-indigo-600" />
            </button>
          )}

          <div className="p-4 border-t border-slate-200 dark:border-[#33334d] bg-white dark:bg-[#1a1a2e]">
            <form
              onSubmit={onFormSubmit}
              className="relative max-w-4xl mx-auto"
            >
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask a strategic question..."
                className="w-full bg-slate-50 dark:bg-[#22223a]/50 border border-slate-200 dark:border-[#33334d] rounded-xl py-3.5 pl-5 pr-14 text-sm focus:ring-2 focus:ring-indigo-500/50 outline-none transition-all shadow-sm disabled:opacity-60"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="absolute right-2 top-2 p-1.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-all shadow-sm"
              >
                <Send className="h-4 w-4" />
              </button>
            </form>
          </div>
        </div>
      </div>

      <CustomPopup
        isOpen={!!sessionToDelete}
        onClose={() => setSessionToDelete(null)}
        title="Delete Conversation"
        description="Are you sure you want to delete this chat session? This action cannot be undone."
        variant="destructive"
        footer={
          <>
            <button
              onClick={() => setSessionToDelete(null)}
              className="px-4 py-2 text-sm font-medium text-slate-700 hover:bg-slate-100 rounded-lg"
            >
              Cancel
            </button>
            <button
              onClick={confirmDelete}
              className="px-4 py-2 text-sm font-medium text-white bg-rose-600 hover:bg-rose-700 rounded-lg"
            >
              Delete
            </button>
          </>
        }
      />
    </>
  );
}
