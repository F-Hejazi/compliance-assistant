import { useState, useEffect, useRef } from "react";

type Message = {
  role: "user" | "assistant";
  content: string;
};

type BackendResponse = {
  mode: string;
  session_id: string;
  input: string;
  final_output: string;
  history: Message[];
};

export default function App() {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function sendMessage() {
    if (!input.trim()) return;
    setError(null);
    setLoading(true);

    try {
      const payload = sessionId
        ? { text: input, session_id: sessionId }
        : { text: input };

      const res = await fetch("http://localhost:8000/process", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        setError("The backend returned an error");
        setLoading(false);
        return;
      }

      const data: BackendResponse = await res.json();
      setSessionId(data.session_id);
      setMessages(data.history);
      setInput("");
    } catch {
      setError("Network error");
    } finally {
      setLoading(false);
    }
  }

  function handleKeyPress(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  return (
    <div className="flex flex-col h-screen font-inter text-gray-800 relative overflow-hidden" style={{ background: 'linear-gradient(135deg, #f8f9f5 0%, #f5f5f0 50%, #f0f2ed 100%)' }}>
      {/* Exact background from sage variation */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="blob blob1"></div>
        <div className="blob blob2"></div>
      </div>

      {/* Top bar */}
      <header className="relative backdrop-blur-xl bg-white/70 border-b border-stone-200/60 shadow-sm">
        <div className="flex items-center justify-between px-8 py-4 max-w-7xl mx-auto">
          <div className="flex items-center space-x-4">
            {/* Original book with light rays logo */}
            <div className="relative w-20 h-19">
              <svg viewBox="0 0 64 64" className="w-full h-full drop-shadow-md">
                <path d="M 20 16 L 20 48 L 32 45 L 44 48 L 44 16 L 32 19 Z" fill="#6b7d64" opacity="0.85" />
                <line x1="32" y1="19" x2="32" y2="45" stroke="#5a6b52" strokeWidth="1.5" />

                <line x1="32" y1="19" x2="22" y2="10" stroke="#6d7d64" strokeWidth="2" opacity="0.7" />
                <line x1="32" y1="19" x2="32" y2="8" stroke="#6d7d64" strokeWidth="2.5" opacity="0.9" />
                <line x1="32" y1="19" x2="42" y2="10" stroke="#6d7d64" strokeWidth="2" opacity="0.7" />
                <line x1="32" y1="19" x2="18" y2="16" stroke="#6d7d64" strokeWidth="1.5" opacity="0.5" />
                <line x1="32" y1="19" x2="46" y2="16" stroke="#6d7d64" strokeWidth="1.5" opacity="0.5" />

                <circle cx="32" cy="19" r="3" fill="#6d7d64" opacity="0.9" />
                <circle cx="32" cy="19" r="6" fill="#8b9d83" opacity="0.3" />
              </svg>
            </div>
            <div>
              <h1 className="text-4xl font-title font-bold py-1 tracking-wide" style={{ color: "#4d5e47" }}>
                Clausewise
              </h1>
              <p className="text-[0.83rem] text-stone-600/80 font-light tracking-widest uppercase mt-1">Compliance Intelligence</p>
            </div>
          </div>

          {/* Right side - helpful info icons */}
          <div className="flex items-center space-x-3">
            {sessionId && (
              <div className="flex items-center space-x-2 px-3 py-1.5 rounded-full bg-white/60 border border-stone-200/50">
                <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse"></div>
                <span className="text-xs text-stone-700 font-medium">Active Session</span>
              </div>
            )}
            <button className="p-2 hover:bg-stone-100/50 rounded-lg transition-colors duration-200 group" title="Help & Documentation">
              <svg className="w-6 h-6 text-stone-600 group-hover:text-stone-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </button>
            <button className="p-2 hover:bg-stone-100/50 rounded-lg transition-colors duration-200 group" title="Settings">
              <svg className="w-6 h-6 text-stone-600 group-hover:text-stone-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </button>
          </div>
        </div>
      </header>

      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto px-4 sm:px-8 py-15 relative">
        <div className="max-w-5xl mx-auto space-y-10">
          {messages.length === 0 && !loading && (
            <div className="flex flex-col items-center justify-center h-full min-h-[400px] space-y-8 animate-fade-in">
              <div className="text-center space-y-5">
                <h2 className="text-4xl font-title font-semibold" style={{ color: "#4d5e47" }}>Good evening,</h2>
                <p className="text-stone-600 max-w-[80vw] leading-relaxed px-4 py-2">Here to help you interpret compliance with precision and confidence.</p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5 w-full max-w-2xl px-4">
                {[
                  {
                    text: "Review policy documents",
                    icon: (
                      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#4d5e47" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                        <polyline points="14 2 14 8 20 8" />
                      </svg>
                    ),
                  },
                  {
                    text: "Check regulatory compliance",
                    icon: (
                      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#4d5e47" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                        <polyline points="9 12 11 14 15 10" />
                      </svg>
                    ),
                  },
                  {
                    text: "Analyze contract clauses",
                    icon: (
                      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#4d5e47" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="11" cy="11" r="8" />
                        <line x1="21" y1="21" x2="16.65" y2="16.65" />
                      </svg>
                    ),
                  },
                  {
                    text: "Explain requirements",
                    icon: (
                      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#4d5e47" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 6c-3.31 0-6 2.69-6 6 0 2.22 1.2 4.16 3 5.2V20a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2v-2.8c1.8-1.04 3-2.98 3-5.2 0-3.31-2.69-6-6-6z" />
                        <path d="M12 2v2" />
                        <path d="M19.07 4.93 17.66 6.34" />
                        <path d="M4.93 4.93 6.34 6.34" />
                      </svg>
                    ),
                  },
                ].map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInput(suggestion.text)}
                    className="bg-white border border-stone-200/60 p-4 rounded-xl hover:border-stone-300/80 hover:shadow-md transition-all duration-200 text-left group"
                  >
                    <div className="flex items-center space-x-3">
                      <span className="group-hover:scale-110 transition-transform duration-200">
                        {suggestion.icon}
                      </span>
                      <span className="text-sm text-stone-700 font-medium">
                        {suggestion.text}
                      </span>
                    </div>
                  </button>
                ))}
              </div>

            </div>
          )}

          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex ${m.role === "user" ? "justify-end" : "justify-start"} animate-slide-up`}
              style={{ animationDelay: `${idx * 0.1}s` }}
            >
              <div
                className={`px-5 py-3.5 rounded-2xl max-w-2xl shadow-sm ${m.role === "user"
                  ? "bg-stone-700 text-white ml-auto"
                  : "bg-white text-stone-800 border border-stone-200/50"
                  }`}
              >
                <p className="text-[15px] leading-relaxed whitespace-pre-wrap">{m.content}</p>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start animate-slide-up">
              <div className="px-5 py-3.5 rounded-2xl bg-white border border-stone-200/50 shadow-sm">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-stone-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-stone-500 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                    <div className="w-2 h-2 bg-stone-600 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                  </div>
                  <span className="text-stone-700 text-sm font-medium">Analyzing...</span>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="flex justify-center animate-slide-up">
              <div className="px-5 py-3.5 rounded-2xl bg-red-50 border border-red-200 text-red-800 shadow-sm">
                {error}
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Floating bottom input */}
      <div className="relative p-4 sm:p-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex space-x-3 bg-white border border-stone-200/60 rounded-2xl p-3 shadow-lg">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              rows={2}
              placeholder="Ask about compliance, regulations, or policies..."
              className="flex-1 bg-transparent text-stone-800 placeholder-stone-400 p-3 rounded-xl focus:outline-none resize-none"
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="text-white font-semibold px-6 rounded-xl transition-all duration-200 transform hover:scale-105 hover:bg-stone-800 hover:shadow-md disabled:opacity-50 disabled:hover:scale-100 flex items-center justify-center min-w-[60px]" style={{ background: "#4d5e47" }}
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
