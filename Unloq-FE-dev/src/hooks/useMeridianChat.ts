import { useState, useCallback } from "react";
import { apiClient as api } from "../lib/api";
import type { ChatMessage } from "../types";

export function useOakfieldChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) return;

      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: "user",
        content: content.trim(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      try {
        const assistantMessageId = `assistant-${Date.now()}`;
        setMessages((prev) => [
          ...prev,
          { id: assistantMessageId, role: "assistant", content: "" },
        ]);

        await api.post(
          "/oakfield/strategist/chat",
          {
            content: content,
          },
          {
            onDownloadProgress: (progressEvent: { event?: { target?: { responseText: string } } }) => {
              const chunk = progressEvent.event?.target?.responseText || "";
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === assistantMessageId
                    ? { ...msg, content: chunk }
                    : msg
                )
              );
            },
          } as Record<string, unknown>
        );
      } catch (err) {
        console.error("Chat error:", err);
        setError(err as Error);
      } finally {
        setIsLoading(false);
      }
    },
    [messages]
  );

  const loadHistory = useCallback(async () => {
    try {
      const response = await api.get("/oakfield/chat/history");
      if (Array.isArray(response.data)) {
        setMessages(response.data);
      }
    } catch (err) {
      console.error("Failed to load chat history:", err);
    }
  }, []);

  return {
    messages,
    sendMessage,
    isLoading,
    error,
    loadHistory,
    setMessages,
  };
}
