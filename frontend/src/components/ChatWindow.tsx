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

  // Auto-scroll to bottom of chats
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Establish WebSocket tunnel to receive background system signals
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/api/ws');
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === 'token_stream') {
          // Future real-time token append hooks
        }
      } catch (err) {
        // Fallback text packet
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
      const res = await fetch('http://localhost:8000/api/chat/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: projectId,
          query: userMsg
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setMessages((prev) => [...prev, { role: 'assistant', content: data.response }]);
      } else {
        setMessages((prev) => [...prev, { role: 'assistant', content: "Sorry, I encountered an issue querying the model. Please check Ollama provider status." }]);
      }
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'assistant', content: "Failed to connect to the backend server. Is the Uvicorn application online?" }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ flex: '1', display: 'flex', flexDirection: 'column', height: '100%', background: 'rgba(0,0,0,0.1)', overflow: 'hidden' }}>
      {/* Header */}
      <div style={{ padding: '16px', borderBottom: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Bot size={20} style={{ color: 'var(--accent-purple)' }} />
        <div>
          <h2 style={{ fontSize: '15px', color: 'var(--text-primary)' }}>Architecture & Memory Explainer</h2>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Discussing frameworks and design structures</span>
        </div>
      </div>

      {/* Messages viewport */}
      <div style={{ flex: '1', overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {messages.map((msg, idx) => (
          <div
            key={idx}
            style={{
              display: 'flex',
              gap: '12px',
              maxWidth: '80%',
              alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
              flexDirection: msg.role === 'user' ? 'row-reverse' : 'row'
            }}
          >
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              background: msg.role === 'user' ? 'rgba(6, 182, 212, 0.2)' : 'rgba(168, 85, 247, 0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: '1px solid',
              borderColor: msg.role === 'user' ? 'var(--accent-cyan)' : 'var(--accent-purple)',
              flexShrink: 0
            }}>
              {msg.role === 'user' ? <User size={16} style={{ color: 'var(--accent-cyan)' }} /> : <Bot size={16} style={{ color: 'var(--accent-purple)' }} />}
            </div>

            <div style={{
              background: msg.role === 'user' ? 'rgba(255,255,255,0.03)' : 'rgba(255,255,255,0.01)',
              border: '1px solid var(--border-color)',
              padding: '12px 16px',
              borderRadius: '12px',
              fontSize: '13px',
              color: 'var(--text-primary)',
              lineHeight: '1.6',
              whiteSpace: 'pre-wrap'
            }}>
              {msg.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div style={{ display: 'flex', gap: '12px', alignSelf: 'flex-start' }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              background: 'rgba(255,255,255,0.02)',
              border: '1px solid var(--border-color)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Cpu size={16} className="animate-spin" style={{ color: 'var(--text-muted)', animation: 'spin 1.5s linear infinite' }} />
            </div>
            <div style={{ padding: '12px 16px', color: 'var(--text-muted)', fontSize: '13px' }}>
              PEIS is reasoning...
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input pane */}
      <form onSubmit={handleSend} style={{ padding: '16px', borderTop: '1px solid var(--border-color)', display: 'flex', gap: '8px' }}>
        <input
          type="text"
          placeholder={projectId ? "Ask about design patterns, modules, or files..." : "Register a workspace path to begin..."}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={!projectId || isLoading}
          style={{
            flex: '1',
            background: 'rgba(0,0,0,0.2)',
            border: '1px solid var(--border-color)',
            borderRadius: '6px',
            padding: '10px 14px',
            color: '#fff',
            fontSize: '13px',
            outline: 'none'
          }}
        />
        <button
          type="submit"
          disabled={!projectId || isLoading || !input.trim()}
          className="glow-btn"
          style={{
            padding: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            opacity: (!projectId || isLoading || !input.trim()) ? 0.5 : 1,
            cursor: (!projectId || isLoading || !input.trim()) ? 'not-allowed' : 'pointer'
          }}
        >
          <Send size={16} />
        </button>
      </form>
    </div>
  );
};
