import React, { useState, useEffect } from "react";
import { v4 as uuidv4 } from "uuid";
import { askAI } from "../../api/ai";
import ChatMessage from "../../components/ChatMessage/ChatMessage";
import {
  smartGreeting,
  simulateTyping,
  scrollToBottom
} from "../../utils/chatHelpers";
import useSoundEffects from "../../hooks/useSoundEffects";
import {speakText} from "../../hooks/speakText";
import UseVoiceInput from "../../components/UseVoiceInput/UseVoiceInput"

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const { playTypeSound } = useSoundEffects()
  const { listening, startListening } = UseVoiceInput((text) => setInput(text));
  const [speechEnabled, setSpeechEnabled] = useState(true);
  const [selectedLanguage, setSelectedLanguage] = useState("en-US");


  const [sessionId] = useState(() =>
    localStorage.getItem("session") || uuidv4()
  );

  /** Load session + chat history */
useEffect(() => {
  localStorage.setItem("session", sessionId);

  const saved = localStorage.getItem("chat_" + sessionId);
  if (saved) {
    setMessages(JSON.parse(saved));
  } else {
    // Add empty assistant message first
    setMessages([{ role: "assistant", text: "" }]);

    const greetingText = smartGreeting();

    // Animate typing for initial greeting
    simulateTyping(setMessages, greetingText, 25, playTypeSound).then(() => {
      if (speechEnabled) {
        speakText(greetingText, selectedLanguage);
      }
    });
  }
}, []);

  /** Store chat history */
  useEffect(() => {
    localStorage.setItem("chat_" + sessionId, JSON.stringify(messages));
    scrollToBottom();
  }, [messages]);

  /** Send message */
  async function send() {
    if (!input || loading) return;

    const userMsg = { role: "user", text: input };
    setMessages((m) => [...m, userMsg]);

    setInput("");
    setLoading(true);

    try {
      const { data } = await askAI({
        question: userMsg.text,
        session_id: sessionId,
      });

      const assistantMsg = {
        role: "assistant",
        text: "",
        confidence: data.confidence,
        sources: data.sources || [],
      };

      // Add empty assistant message first
      setMessages((m) => [...m, assistantMsg]);
      // Animate typing (streaming simulation)
      await simulateTyping(setMessages, data.answer, 25, playTypeSound);
      if (speechEnabled) {
        speakText(data.answer, selectedLanguage);
      }
      setLoading(false);
    } catch (err) {
      setMessages((m) => [
        ...m,
        { role: "assistant", text: "❗ Error contacting AI." },
      ]);
      setLoading(false);
    }
  }

  return (
    <div className="max-w-3xl mx-auto p-4 space-y-4">

      {/* CHAT MESSAGES */}
      <div className="space-y-2">
        {messages.map((msg, i) => (
          <div key={i}>
            <ChatMessage message={msg} />

            {msg.role === "assistant" && msg.confidence !== undefined && (
              <p className="text-gray-500 text-sm">
                Confidence: {msg.confidence.toFixed(2)}%
              </p>
            )}

            {msg.role === "assistant" && msg.sources?.length > 0 && (
              <ul className="text-gray-400 text-sm list-disc ml-5">
                {msg.sources.map((s, idx) => (
                  <li key={idx}>
                    {s.text} ({s.score.toFixed(2)})
                  </li>
                ))}
              </ul>
            )}
          </div>
        ))}

        {loading && (
          <p className="text-gray-400 animate-pulse">AI is thinking...</p>
        )}
      </div>

      {/* INPUT BAR */}
      <div className="flex gap-2 pt-3 border-t">
        <input
          className="flex-1 p-2 border rounded"
          placeholder="Ask about Integrated Science..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
        />
        <select
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            className="px-2 py-1 border rounded"
          >
            <option value="en-US">English</option>
            <option value="es-ES">Spanish</option>
            <option value="fr-FR">French</option>
            <option value="de-DE">German</option>
            <option value="ja-JP">Japanese</option>
            <option value="zh-CN">Chinese</option>
          </select>
        <button
          type="button"
          onClick={() => setSpeechEnabled(prev => !prev)}
          className="px-3 py-2 bg-gray-300 text-black rounded"
        >
          {speechEnabled ? "🗣️ Speech On" : "🔇 Speech Off"}
        </button>

        <button
          type="button"
          onClick={startListening}
          className="px-3 py-2 bg-green-500 text-white rounded"
        >
          {listening ? "🎙 Listening..." : "🎤 Speak"}
        </button>

        <button
          onClick={send}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded"
        >
          {loading ? "..." : "Send"}
        </button>
      </div>
    </div>
  );
}
