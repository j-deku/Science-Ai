import { useState, useRef } from "react";

export default function useStreamingChat() {
  const [messages, setMessages] = useState([]);
  const controllerRef = useRef(null);

  async function streamAI(endpoint, payload) {
    controllerRef.current = new AbortController();
    const decoder = new TextDecoder();

    const userMessage = { role: "user", text: payload.question };
    setMessages((m) => [...m, userMessage]);

    const assistantMsg = { role: "assistant", text: "", streaming: true };
    setMessages((m) => [...m, assistantMsg]);

    const res = await fetch(endpoint, {
      method: "POST",
      body: JSON.stringify(payload),
      headers: { "Content-Type": "application/json" },
      signal: controllerRef.current.signal
    });

    if (!res.body) return;

    const reader = res.body.getReader();
    let fullText = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      fullText += chunk;

      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        last.text = fullText;
        return updated;
      });
    }

    setMessages((prev) => {
      const final = [...prev];
      final[final.length - 1].streaming = false;
      return final;
    });

    return fullText;
  }

  function stopStream() {
    controllerRef.current?.abort();
  }

  return { messages, setMessages, streamAI, stopStream };
}
