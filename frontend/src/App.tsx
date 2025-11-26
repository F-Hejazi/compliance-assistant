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
    <div className="flex flex-col h-screen bg-gradient-to-br from-amber-50 via-rose-50 to-orange-50 font-sans text-gray-800 relative overflow-hidden">
      {/* Soft animated background orbs - lighter and more subtle */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 -left-4 w-96 h-96 bg-orange-200 rounded-full mix-blend-multiply filter blur-3xl opacity-40 animate-blob"></div>
        <div className="absolute top-0 -right-4 w-96 h-96 bg-rose-200 rounded-full mix-blend-multiply filter blur-3xl opacity-40 animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-20 w-96 h-96 bg-amber-200 rounded-full mix-blend-multiply filter blur-3xl opacity-40 animate-blob animation-delay-4000"></div>
      </div>

      {/* Top bar with soft glassmorphism */}
      <header className="relative backdrop-blur-xl bg-white/70 border-b border-stone-200/60 shadow-sm">
        <div className="flex items-center justify-between px-8 py-6 max-w-7xl mx-auto">
          <div className="flex items-center space-x-4">
            {/* Book with Light logo placeholder */}
            <div className="relative w-12 h-12">
              <svg viewBox="0 0 64 64" className="w-full h-full drop-shadow-md">
                {/* Book pages */}
                <path d="M 20 16 L 20 48 L 32 45 L 44 48 L 44 16 L 32 19 Z" fill="#78716c" opacity="0.7" />
                <line x1="32" y1="19" x2="32" y2="45" stroke="#57534e" strokeWidth="1.5" />
                
                {/* Light rays emanating */}
                <line x1="32" y1="19" x2="22" y2="10" stroke="#f59e0b" strokeWidth="2" opacity="0.7" />
                <line x1="32" y1="19" x2="32" y2="8" stroke="#f59e0b" strokeWidth="2.5" opacity="0.9" />
                <line x1="32" y1="19" x2="42" y2="10" stroke="#f59e0b" strokeWidth="2" opacity="0.7" />
                <line x1="32" y1="19" x2="18" y2="16" stroke="#f59e0b" strokeWidth="1.5" opacity="0.5" />
                <line x1="32" y1="19" x2="46" y2="16" stroke="#f59e0b" strokeWidth="1.5" opacity="0.5" />
                
                {/* Central glow */}
                <circle cx="32" cy="19" r="3" fill="#f59e0b" opacity="0.9" />
                <circle cx="32" cy="19" r="6" fill="#f59e0b" opacity="0.4" />
                <circle cx="32" cy="19" r="9" fill="#fbbf24" opacity="0.2" />
                
                <defs>
                  <linearGradient id="bookGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#78716c" />
                    <stop offset="100%" stopColor="#57534e" />
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <div>
              <h1 className="text-3xl font-serif font-bold bg-gradient-to-r from-stone-700 via-stone-600 to-amber-700 bg-clip-text text-transparent tracking-wide">
                Clausewise
              </h1>
              <p className="text-xs text-stone-600/80 font-light tracking-wider uppercase">Compliance Intelligence</p>
            </div>
          </div>
          {sessionId && (
            <div className="hidden sm:flex items-center space-x-2 px-4 py-2 rounded-full bg-white/60 backdrop-blur-sm border border-emerald-200/50 shadow-sm">
              <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-stone-700 font-medium">Active Session</span>
            </div>
          )}
        </div>
      </header>

      {/* Chat messages */}
      <div className="flex-1 overflow-y-auto px-4 sm:px-8 py-8 relative">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.length === 0 && !loading && (
            <div className="flex flex-col items-center justify-center h-full min-h-[400px] space-y-6 animate-fade-in">
              <div className="w-24 h-24 bg-gradient-to-br from-amber-100/60 to-rose-100/60 rounded-3xl flex items-center justify-center backdrop-blur-sm border border-stone-200/40 shadow-xl">
                <svg className="w-12 h-12 text-stone-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div className="text-center space-y-2">
                <h2 className="text-2xl font-serif font-semibold text-stone-800">Welcome to Clausewise</h2>
                <p className="text-stone-600/90 max-w-md leading-relaxed">Your trusted partner in navigating the complexities of compliance. Ask me about regulations, policies, or contract clauses.</p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-8 w-full max-w-2xl">
                {[
                  { icon: "📋", text: "Review policy document", color: "from-amber-50/90 to-orange-50/90 border-amber-200/50 hover:border-amber-300/70 hover:shadow-md" },
                  { icon: "⚖️", text: "Check regulatory compliance", color: "from-orange-50/90 to-rose-50/90 border-orange-200/50 hover:border-orange-300/70 hover:shadow-md" },
                  { icon: "🔍", text: "Analyze contract clause", color: "from-rose-50/90 to-pink-50/90 border-rose-200/50 hover:border-rose-300/70 hover:shadow-md" },
                  { icon: "💡", text: "Explain requirements", color: "from-pink-50/90 to-amber-50/90 border-pink-200/50 hover:border-pink-300/70 hover:shadow-md" }
                ].map((suggestion, idx) => (
                  <button
                    key={idx}
                    onClick={() => setInput(suggestion.text)}
                    className={`bg-gradient-to-br ${suggestion.color} backdrop-blur-sm border p-4 rounded-2xl hover:scale-105 transition-all duration-200 text-left group`}
                  >
                    <div className="flex items-center space-x-3">
                      <span className="text-2xl group-hover:scale-110 transition-transform duration-200">{suggestion.icon}</span>
                      <span className="text-sm text-stone-700 font-medium">{suggestion.text}</span>
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
                className={`px-6 py-4 rounded-2xl max-w-2xl shadow-md ${
                  m.role === "user"
                    ? "bg-gradient-to-br from-stone-600 to-stone-700 text-white ml-auto"
                    : "bg-white/90 backdrop-blur-md text-stone-800 border border-stone-200/60"
                }`}
              >
                <p className="text-[15px] leading-relaxed whitespace-pre-wrap">{m.content}</p>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start animate-slide-up">
              <div className="px-6 py-4 rounded-2xl bg-white/90 backdrop-blur-md border border-stone-200/60 shadow-md">
                <div className="flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-amber-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-orange-500 rounded-full animate-bounce" style={{ animationDelay: "0.1s" }}></div>
                    <div className="w-2 h-2 bg-rose-500 rounded-full animate-bounce" style={{ animationDelay: "0.2s" }}></div>
                  </div>
                  <span className="text-stone-700 text-sm font-medium">Analyzing...</span>
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="flex justify-center animate-slide-up">
              <div className="px-6 py-4 rounded-2xl bg-rose-100/80 backdrop-blur-md border border-rose-300/50 text-rose-800 shadow-md">
                {error}
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Floating bottom input with warm glassmorphism */}
      <div className="relative p-4 sm:p-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex space-x-3 backdrop-blur-xl bg-white/80 border border-stone-200/60 rounded-2xl p-3 shadow-xl">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyPress}
              rows={2}
              placeholder="Ask about compliance, regulations, or policies..."
              className="flex-1 bg-transparent text-stone-800 placeholder-stone-500/60 p-3 rounded-xl focus:outline-none resize-none"
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="bg-gradient-to-br from-stone-600 to-stone-700 text-white font-semibold px-6 rounded-xl transition-all duration-200 transform hover:scale-105 hover:shadow-lg disabled:opacity-50 disabled:hover:scale-100 flex items-center justify-center min-w-[60px]"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <style jsx>{`
        @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&display=swap');

        .font-serif {
          font-family: 'Cormorant Garamond', serif;
        }

        @keyframes blob {
          0%, 100% {
            transform: translate(0px, 0px) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
        }

        @keyframes slide-up {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes fade-in {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        .animate-blob {
          animation: blob 7s infinite;
        }

        .animation-delay-2000 {
          animation-delay: 2s;
        }

        .animation-delay-4000 {
          animation-delay: 4s;
        }

        .animate-slide-up {
          animation: slide-up 0.5s ease-out;
        }

        .animate-fade-in {
          animation: fade-in 0.8s ease-out;
        }
      `}</style>
    </div>
  );
}