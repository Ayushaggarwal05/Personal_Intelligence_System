import React, { useState, useEffect, useRef } from 'react';
import { Send, Bot, User, Cpu } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface ChatWindowProps {
  projectId: string | null;
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ projectId }) => {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', content: "Hello! I am PEIS, your engineering memory coach. Please register a codebase workspace path, and we can discuss the implementation details, system architecture, and trade-offs of your project." }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/api/ws');
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === 'token_stream') {
          // Streaming hooks
        }
      } catch (err) {
        // Fallback
      }
    };

    return () => {
      ws.close();
    };
  }, []);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !projectId || isLoading) return;

    const userMsg = input.trim();
    setMessages((prev) => [...prev, { role: 'user', content: userMsg }]);
    setInput('');
    setIsLoading(true);

    try {
      // Append initial empty assistant message for real-time streaming accumulation
      setMessages((prev) => [...prev, { role: 'assistant', content: '' }]);

      const res = await fetch('http://localhost:8000/api/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          query: userMsg
        }),
      });

      if (res.ok && res.body) {
        const reader = res.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let done = false;
        let accumulatedText = '';

        while (!done) {
          const { value, done: readerDone } = await reader.read();
          done = readerDone;
          if (value) {
            const chunk = decoder.decode(value, { stream: true });
            accumulatedText += chunk;
            setMessages((prev) => {
              const updated = [...prev];
              updated[updated.length - 1] = { role: 'assistant', content: accumulatedText };
              return updated;
            });
          }
        }
      } else {
        setMessages((prev) => [
          ...prev.slice(0, -1),
          { role: 'assistant', content: "Sorry, I encountered an issue querying the model. Please check Ollama provider status." }
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev.slice(0, -1),
        { role: 'assistant', content: "Failed to connect to the backend server. Is the Uvicorn application online?" }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-black/10 overflow-hidden">
      {/* Header */}
      <div className="p-4 border-b border-white/10 flex items-center gap-2 bg-bgCard/30">
        <Bot size={20} className="text-accentPurple" />
        <div className="flex flex-col">
          <h2 className="text-sm font-semibold text-gray-100 font-outfit">Architecture & Memory Explainer</h2>
          <span className="text-[10px] text-gray-400">Discussing frameworks and design structures</span>
        </div>
      </div>

      {/* Messages viewport */}
      <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex gap-3 max-w-[80%] ${
              msg.role === 'user' ? 'self-end flex-row-reverse' : 'self-start flex-row'
            } animate-fade-in`}
          >
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 border ${
              msg.role === 'user' ? 'bg-accentCyan/10 border-accentCyan' : 'bg-accentPurple/10 border-accentPurple'
            }`}>
              {msg.role === 'user' ? <User size={16} className="text-accentCyan" /> : <Bot size={16} className="text-accentPurple" />}
            </div>

            <div className={`border border-white/10 p-3 rounded-2xl text-xs leading-relaxed font-sans ${
              msg.role === 'user' ? 'bg-white/5 text-gray-200' : 'bg-white/2 text-gray-100'
            } whitespace-pre-wrap`}>
              {msg.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3 self-start items-center">
            <div className="w-8 h-8 rounded-full bg-white/2 border border-white/10 flex items-center justify-center flex-shrink-0">
              <Cpu size={16} className="animate-spin text-gray-500" />
            </div>
            <div className="p-3 text-gray-400 text-xs font-outfit">
              PEIS is reasoning...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input pane */}
      <form onSubmit={handleSend} className="p-4 border-t border-white/10 flex gap-2 bg-bgCard/20">
        <input
          type="text"
          placeholder={projectId ? "Ask about design patterns, modules, or files..." : "Register a workspace path to begin..."}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={!projectId || isLoading}
          className="flex-1 bg-black/20 border border-white/10 rounded-md p-2.5 text-xs text-white outline-none focus:border-accentPurple/50 transition-all"
        />
        <button
          type="submit"
          disabled={!projectId || isLoading || !input.trim()}
          className="glow-btn p-2.5 flex items-center justify-center cursor-pointer"
          style={{ opacity: (!projectId || isLoading || !input.trim()) ? 0.5 : 1 }}
        >
          <Send size={16} />
        </button>
      </form>
    </div>
  );
};
