import { FormEvent, useRef, useState } from "react";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { useToast } from "../hooks/useToast";
import { agentRoute, chat } from "../services/api";

const starters = [
  "How should I dispose of a plastic bottle?",
  "What is wet waste?",
  "Can batteries be put in normal garbage?",
  "How can I reduce household waste?",
  "What is e-waste?",
];

interface Msg {
  role: "user" | "assistant";
  content: string;
  action?: string;
}

export function ChatAssistant() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [pendingAction, setPendingAction] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const { push } = useToast();

  async function send(text: string) {
    if (!text.trim()) return;
    const userMsg: Msg = { role: "user", content: text.trim() };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const route = await agentRoute(text);
      setPendingAction(route.label);
      const history = [...messages, userMsg].map((m) => ({
        role: m.role,
        content: m.content,
      }));
      const res = await chat(text, history);
      setMessages((m) => [
        ...m,
        { role: "assistant", content: res.reply, action: res.agent_action },
      ]);
    } catch (err) {
      push(err instanceof Error ? err.message : "Chat failed.", "error");
    } finally {
      setLoading(false);
      setPendingAction(null);
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 100);
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    send(input);
  }

  return (
    <div className="flex h-[calc(100vh-8rem)] max-w-3xl flex-col gap-4">
      <div>
        <h1 className="text-2xl font-bold">AI Chat Assistant</h1>
        <p className="text-slate-600 mt-1">EcoSort AI answers waste and recycling questions.</p>
      </div>
      {pendingAction && (
        <p className="text-sm font-medium text-eco-800">AI Action: {pendingAction}</p>
      )}
      <div className="flex-1 overflow-y-auto rounded-xl border bg-white p-4 space-y-3">
        {messages.length === 0 && (
          <p className="text-slate-500 text-sm">Ask a question or try a suggestion below.</p>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={`max-w-[90%] rounded-lg px-3 py-2 text-sm ${
              m.role === "user" ? "ml-auto bg-eco-600 text-white" : "bg-slate-100 text-slate-900"
            }`}
          >
            {m.action && m.role === "assistant" && (
              <p className="text-xs font-semibold text-eco-700 mb-1">AI Action: {m.action}</p>
            )}
            {m.content}
          </div>
        ))}
        {loading && <LoadingSpinner label="EcoSort AI is thinking…" />}
        <div ref={bottomRef} />
      </div>
      <div className="flex flex-wrap gap-2">
        {starters.map((s) => (
          <button
            key={s}
            type="button"
            className="rounded-full border px-3 py-1 text-xs hover:bg-eco-50"
            onClick={() => send(s)}
            disabled={loading}
          >
            {s}
          </button>
        ))}
      </div>
      <form onSubmit={onSubmit} className="flex gap-2">
        <input
          className="flex-1 rounded-lg border px-3 py-2"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your question…"
          aria-label="Chat message"
        />
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-eco-600 px-4 py-2 text-white hover:bg-eco-700 disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
}
