import React, { useState, useEffect, useRef } from "react";
import { Send, Bot, User } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ChatWindowProps {
  projectId: string | null;
}

/* ── Inline markdown parser ──────────────────────────────── */
const parseInline = (text: string): React.ReactNode[] => {
  const codeParts = text.split(/(`[^`]+`)/g);
  return codeParts.flatMap((part, i) => {
    if (part.startsWith("`") && part.endsWith("`")) {
      return (
        <code
          key={i}
          style={{
            background: 'rgba(77,124,115,0.15)',
            border: '1px solid rgba(77,124,115,0.2)',
            borderRadius: 4,
            padding: '1px 6px',
            fontSize: '0.85em',
            fontFamily: 'JetBrains Mono, monospace',
            color: 'var(--accent-hover)',
          }}
        >
          {part.slice(1, -1)}
        </code>
      );
    }
    const boldParts = part.split(/(\*\*[^*]+\*\*)/g);
    return boldParts.map((b, bi) =>
      b.startsWith("**") && b.endsWith("**")
        ? <strong key={`${i}-${bi}`} style={{ fontWeight: 600, color: 'var(--sage)' }}>{b.slice(2, -2)}</strong>
        : b
    );
  });
};

const parseMarkdown = (text: string): React.ReactNode =>
  text.split("\n").map((line, idx) => {
    // 1. Headings
    const hm = line.match(/^(#{1,6})\s+(.*)$/);
    if (hm) {
      const lvl = hm[1].length;
      const sz  = lvl === 1 ? 15 : lvl === 2 ? 14 : 13;
      return (
        <p
          key={idx}
          style={{
            margin: '18px 0 8px',
            fontFamily: 'Manrope, Inter, sans-serif',
            fontWeight: 700,
            fontSize: sz,
            color: 'var(--txt-primary)',
            letterSpacing: '-0.01em',
          }}
        >
          {parseInline(hm[2])}
        </p>
      );
    }

    // 2. Blockquotes / Callouts
    const bq = line.match(/^>\s+(.*)$/);
    if (bq) {
      return (
        <div
          key={idx}
          style={{
            borderLeft: '3px solid var(--accent)',
            paddingLeft: 14,
            margin: '12px 0',
            color: 'var(--txt-second)',
            fontStyle: 'italic',
            fontSize: 12,
            lineHeight: 1.8,
          }}
        >
          {parseInline(bq[1])}
        </div>
      );
    }

    // 3. Bullet lists
    const lm = line.match(/^[-*]\s+(.*)$/);
    if (lm) return (
      <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: 8, margin: '6px 0', paddingLeft: 4 }}>
        <span style={{ color: 'var(--accent)', fontSize: 10, marginTop: 4, flexShrink: 0 }}>▸</span>
        <span style={{ fontSize: 12, color: 'var(--txt-second)', lineHeight: 1.8 }}>{parseInline(lm[1])}</span>
      </div>
    );

    // 4. Whitespace spacer
    if (line.trim() === "") return <div key={idx} style={{ height: 8 }} />;

    // 5. Normal paragraphs
    return (
      <p
        key={idx}
        style={{
          margin: '0 0 10px',
          fontSize: 12.2,
          color: 'var(--txt-second)',
          lineHeight: 1.8,
          letterSpacing: '0.01em',
        }}
      >
        {parseInline(line)}
      </p>
    );
  });

/* ── Code block ─────────────────────────────────────────── */
const CodeBlock: React.FC<{ language: string; code: string }> = ({ language, code }) => {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 1800);
  };
  return (
    <div
      style={{
        margin: '12px 0',
        borderRadius: 12,
        overflow: 'hidden',
        border: '1px solid rgba(255,255,255,0.07)',
        boxShadow: '0 2px 12px rgba(0,0,0,0.3)',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '7px 14px',
          background: '#1C2420',
          borderBottom: '1px solid rgba(255,255,255,0.06)',
        }}
      >
        <span style={{ fontSize: 9, color: 'var(--txt-muted)', fontFamily: 'JetBrains Mono, monospace', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
          {language}
        </span>
        <button
          onClick={copy}
          style={{
            fontSize: 9,
            color: copied ? 'var(--success)' : 'var(--txt-disabled)',
            background: 'rgba(255,255,255,0.05)',
            border: '1px solid rgba(255,255,255,0.06)',
            borderRadius: 5,
            padding: '2px 8px',
            cursor: 'pointer',
            fontFamily: 'JetBrains Mono, monospace',
            transition: 'color 220ms ease',
          }}
        >
          {copied ? '✓ copied' : 'copy'}
        </button>
      </div>
      <pre
        style={{
          margin: 0,
          padding: '14px 16px',
          background: '#161D1A',
          fontSize: 11,
          lineHeight: 1.7,
          color: '#CAD2CE',
          fontFamily: 'JetBrains Mono, monospace',
          overflowX: 'auto',
        }}
      >
        <code>{code}</code>
      </pre>
    </div>
  );
};

/* ── Full content renderer ──────────────────────────────── */
const renderContent = (content: string) => {
  if (!content) return null;
  const parts = content.split(/(```[\s\S]*?```)/g);
  return parts.map((part, i) => {
    if (part.startsWith("```") && part.endsWith("```")) {
      const lines     = part.slice(3, -3).trim().split("\n");
      const firstLine = lines[0].trim();
      let lang = "code", codeLines = lines;
      if (firstLine && !firstLine.includes(" ") && firstLine.length < 20) {
        lang = firstLine; codeLines = lines.slice(1);
      }
      return <CodeBlock key={i} language={lang} code={codeLines.join("\n")} />;
    }
    return <div key={i}>{parseMarkdown(part)}</div>;
  });
};

/* ── Suggestion section parser ───────────────────────────── */
const splitSuggestions = (content: string): { main: string; questions: string[] } => {
  let main = content.replace("[EXPLAIN_DONE]", "");
  const questions: string[] = [];

  // 1. Try to extract JSON-like structures that contain "question": "..."
  const jsonRegex = /\{[\s\S]*?"question"\s*:\s*"((?:[^"\\]|\\.)*)"[\s\S]*?\}/g;
  let match;
  const matchesToStrip: string[] = [];

  while ((match = jsonRegex.exec(content)) !== null) {
    const fullMatch = match[0];
    const qText = match[1]
      .replace(/\\"/g, '"') // unescape double quotes
      .replace(/\\n/g, ' ') // clean up newlines
      .trim();
    if (qText) {
      questions.push(qText);
      matchesToStrip.push(fullMatch);
    }
  }

  if (questions.length > 0) {
    let cleaned = content;
    for (const block of matchesToStrip) {
      cleaned = cleaned.replace(block, "");
    }
    cleaned = cleaned.replace(/[\s,\[\]\{\}]*$/, "").trim();
    main = cleaned;
  }

  // 2. Fallback to standard "consider asking:" text matching
  const marker = "consider asking:";
  const markerIdx = main.toLowerCase().indexOf(marker);
  if (markerIdx !== -1) {
    const headerStart = main.slice(0, markerIdx).lastIndexOf("\nTo ");
    const splitAt = headerStart > 0 ? headerStart : markerIdx - 30;
    if (splitAt > 0) {
      const textMain = main.slice(0, splitAt).trim();
      const followUp = main.slice(splitAt);
      const textQuestions = followUp
        .split("\n")
        .map(l => l.trim().match(/^\d+\.\s+(.+)$/)?.[1])
        .filter(Boolean) as string[];
      
      if (textQuestions.length > 0) {
        return { main: textMain, questions: [...questions, ...textQuestions] };
      }
    }
  }

  // 3. Fallback to parsing trailing numbered question blocks (e.g. "1. Why... \n 2. How...") at the end of the text
  const lines = main.split("\n");
  const parsedQuestions: string[] = [];
  let startIndex = -1;

  for (let i = 0; i < lines.length; i++) {
    const l = lines[i].trim();
    const match = l.match(/^\d+\.\s+(.+)$/);
    if (match) {
      if (startIndex === -1) {
        if (l.startsWith("1.")) {
          startIndex = i;
          parsedQuestions.push(match[1].trim());
        }
      } else {
        parsedQuestions.push(match[1].trim());
      }
    } else {
      if (startIndex !== -1 && l !== "") {
        startIndex = -1;
        parsedQuestions.length = 0;
      }
    }
  }

  if (startIndex !== -1 && parsedQuestions.length > 0) {
    return {
      main: lines.slice(0, startIndex).join("\n").trim(),
      questions: [...questions, ...parsedQuestions]
    };
  }

  return { main, questions };
};

/* ── Typing indicator ───────────────────────────────────── */
const TypingIndicator = () => (
  <div className="flex items-center gap-1.5" style={{ padding: '4px 0' }}>
    {[0, 1, 2].map(i => <div key={i} className="typing-dot" />)}
  </div>
);

/* ════════════════════════════════════════════════════════════ */
export const ChatWindow: React.FC<ChatWindowProps> = ({ projectId }) => {
  const [messages, setMessages] = useState<Message[]>([{
    role: "assistant",
    content: "Hello! I'm ASTA, your engineering mentor. Register a codebase workspace to begin exploring architecture, trade-offs, and implementation details of your project.",
  }]);
  const [input,     setInput]     = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement | null>(null);
  const wsRef     = useRef<WebSocket | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/api/ws");
    wsRef.current = ws;
    ws.onmessage = () => {};
    return () => ws.close();
  }, []);

  /* ── Core streaming fetch ─────────────────────────────── */
  const streamQuery = async (query: string, history: Message[]) => {
    setIsLoading(true);
    setMessages(prev => [...prev, { role: "assistant", content: "" }]);
    try {
      const res = await fetch("http://localhost:8000/api/chat/stream", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project_id: projectId,
          query,
          history: history.map(m => ({ role: m.role, content: m.content })),
        }),
      });
      if (res.ok && res.body) {
        const reader  = res.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let accumulated = "";
        while (true) {
          const { value, done } = await reader.read();
          if (done) break;
          accumulated += decoder.decode(value, { stream: true });
          setMessages(prev => {
            const u = [...prev];
            u[u.length - 1] = { role: "assistant", content: accumulated };
            return u;
          });
        }
      } else {
        setMessages(prev => [
          ...prev.slice(0, -1),
          { role: "assistant", content: "Sorry — I encountered an issue querying the model. Please check your Ollama connection." },
        ]);
      }
    } catch {
      setMessages(prev => [
        ...prev.slice(0, -1),
        { role: "assistant", content: "Failed to connect to the backend server. Is Uvicorn running on port 8000?" },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    const q = input.trim();
    if (!q || !projectId || isLoading) return;
    const history = [...messages];
    setMessages(prev => [...prev, { role: "user", content: q }]);
    setInput("");
    await streamQuery(q, history);
  };

  const handleSuggestionClick = async (q: string) => {
    if (!projectId || isLoading) return;
    const history = [...messages];
    setMessages(prev => [...prev, { role: "user", content: q }]);
    await streamQuery(q, history);
  };

  return (
    <div
      className="flex flex-col h-full overflow-hidden"
      style={{ background: 'var(--bg-app)' }}
    >
      {/* Message Viewport */}
      <div
        className="flex-1 overflow-y-auto chat-bg"
        style={{ padding: '24px 20px', display: 'flex', flexDirection: 'column', gap: 16 }}
      >
        {messages.map((msg, idx) => {
          const { main, questions } = msg.role === "assistant"
            ? splitSuggestions(msg.content)
            : { main: msg.content, questions: [] };

          const isUser = msg.role === "user";

          // Skip rendering if assistant message is empty to avoid rendering an empty bubble
          if (!isUser && !main.trim()) return null;

          const isLast = idx === messages.length - 1;
          const hasFinishedExplanation = msg.content.includes("[EXPLAIN_DONE]");
          const isStreamingThis = !isUser && isLast && isLoading && hasFinishedExplanation;

          return (
            <div
              key={idx}
              className="animate-fade-in"
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 12,
                flexDirection: isUser ? 'row-reverse' : 'row',
                maxWidth: '88%',
                alignSelf: isUser ? 'flex-end' : 'flex-start',
              }}
            >
              {/* Avatar */}
              <div
                className="flex-shrink-0 rounded-full flex items-center justify-center"
                style={{
                  width: 30,
                  height: 30,
                  background: isUser
                    ? 'rgba(77,124,115,0.12)'
                    : 'rgba(152,182,167,0.10)',
                  border: isUser
                    ? '1px solid rgba(77,124,115,0.25)'
                    : '1px solid rgba(152,182,167,0.18)',
                }}
              >
                {isUser
                  ? <User size={14} style={{ color: 'var(--accent-hover)' }} />
                  : <Bot  size={14} style={{ color: 'var(--sage)' }} />
                }
              </div>

              {/* Bubble */}
              <div
                style={{
                  borderRadius: isUser ? '16px 16px 4px 16px' : undefined,
                  padding: isUser ? '12px 16px' : '4px 0',
                  background: isUser
                    ? 'rgba(77,124,115,0.11)'
                    : 'transparent',
                  border: isUser
                    ? '1px solid rgba(77,124,115,0.22)'
                    : 'none',
                  boxShadow: isUser ? '0 1px 4px rgba(0,0,0,0.1)' : 'none',
                  backdropFilter: isUser ? 'blur(6px)' : 'none',
                  minWidth: 0,
                  flex: 1,
                }}
              >
                {renderContent(main)}

                {/* Active thinking/generating indicator */}
                {isLast && isLoading && !hasFinishedExplanation && (
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8,
                      marginTop: 12,
                      padding: '6px 12px',
                      background: 'rgba(255, 255, 255, 0.02)',
                      border: '1px solid rgba(255, 255, 255, 0.04)',
                      borderRadius: 8,
                      width: 'fit-content',
                    }}
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent)] animate-pulse" />
                    <span
                      style={{
                        fontSize: 10.5,
                        color: 'var(--txt-muted)',
                        fontFamily: 'monospace',
                      }}
                    >
                      ASTA is thinking...
                    </span>
                  </div>
                )}

                {/* Streaming suggested questions indicator */}
                {isStreamingThis && (
                  <div
                    style={{
                      marginTop: 20,
                      padding: 16,
                      background: 'rgba(26, 33, 30, 0.45)',
                      border: '1px solid rgba(255, 255, 255, 0.04)',
                      borderRadius: 12,
                      display: 'flex',
                      alignItems: 'center',
                      gap: 8,
                    }}
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent)] animate-pulse" />
                    <span
                      style={{
                        fontSize: 11,
                        color: 'var(--txt-second)',
                        fontFamily: 'Inter, sans-serif',
                      }}
                    >
                      Formulating suggested follow-ups...
                    </span>
                  </div>
                )}

                {/* Suggested questions */}
                {questions.length > 0 && (
                  <div
                    style={{
                      marginTop: 20,
                      padding: 16,
                      background: 'rgba(26, 33, 30, 0.45)',
                      border: '1px solid rgba(255, 255, 255, 0.04)',
                      borderRadius: 12,
                    }}
                  >
                    <div
                      style={{
                        fontSize: 9,
                        color: 'var(--sage)',
                        fontFamily: 'JetBrains Mono, monospace',
                        textTransform: 'uppercase',
                        letterSpacing: '0.08em',
                        marginBottom: 10,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 6,
                      }}
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent)] animate-pulse" />
                      Suggested follow-ups
                    </div>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                      {questions.map((q, qi) => (
                        <button
                          key={qi}
                          onClick={() => handleSuggestionClick(q)}
                          className="text-left font-sans leading-relaxed cursor-pointer"
                          style={{
                            fontSize: 11.5,
                            color: 'var(--txt-second)',
                            background: 'rgba(255, 255, 255, 0.02)',
                            border: '1px solid rgba(255, 255, 255, 0.04)',
                            borderRadius: 8,
                            padding: '10px 14px',
                            transition: 'all 200ms ease',
                          }}
                          onMouseEnter={(e) => {
                            (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(77, 124, 115, 0.35)';
                            (e.currentTarget as HTMLButtonElement).style.color = 'var(--txt-primary)';
                            (e.currentTarget as HTMLButtonElement).style.background = 'rgba(77, 124, 115, 0.08)';
                            (e.currentTarget as HTMLButtonElement).style.transform = 'translateY(-1px)';
                          }}
                          onMouseLeave={(e) => {
                            (e.currentTarget as HTMLButtonElement).style.borderColor = 'rgba(255, 255, 255, 0.04)';
                            (e.currentTarget as HTMLButtonElement).style.color = 'var(--txt-second)';
                            (e.currentTarget as HTMLButtonElement).style.background = 'rgba(255, 255, 255, 0.02)';
                            (e.currentTarget as HTMLButtonElement).style.transform = 'none';
                          }}
                        >
                          {q}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {/* Typing indicator */}
        {isLoading && (messages.length === 0 || messages[messages.length - 1].role !== "assistant" || !messages[messages.length - 1].content) && (
          <div
            className="animate-fade-in"
            style={{ display: 'flex', alignItems: 'flex-start', gap: 12, maxWidth: '88%' }}
          >
            <div
              className="flex-shrink-0 rounded-full flex items-center justify-center"
              style={{
                width: 30,
                height: 30,
                background: 'rgba(152,182,167,0.10)',
                border: '1px solid rgba(152,182,167,0.18)',
              }}
            >
              <Bot size={14} style={{ color: 'var(--sage)' }} />
            </div>
            <div
              style={{
                borderRadius: '4px 18px 18px 18px',
                padding: '14px 18px',
                background: 'var(--bg-card)',
                border: '1px solid rgba(255,255,255,0.05)',
              }}
            >
              <TypingIndicator />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Floating Input Bar */}
      <div className="w-full px-6 flex-shrink-0 bg-transparent flex flex-col pt-2 select-none">
        <form
          onSubmit={handleSend}
          className="asta-chat-input-container"
        >
          <input
            type="text"
            placeholder={
              projectId
                ? "Ask about architecture, modules, design decisions..."
                : "Register a workspace to begin..."
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={!projectId || isLoading}
            style={{
              background: 'transparent',
              border: 'none',
              outline: 'none',
              width: '100%',
              color: 'var(--txt-primary)',
              fontSize: 12.5,
              fontFamily: 'Inter, sans-serif',
              paddingRight: 10,
            }}
          />
          <button
            type="submit"
            disabled={!projectId || isLoading || !input.trim()}
            className="flex items-center justify-center rounded-full flex-shrink-0"
            style={{
              width: 32,
              height: 32,
              background: (!projectId || isLoading || !input.trim()) ? 'transparent' : 'var(--accent)',
              color: (!projectId || isLoading || !input.trim()) ? 'var(--txt-disabled)' : '#F4F6F5',
              border: 'none',
              cursor: (!projectId || isLoading || !input.trim()) ? 'not-allowed' : 'pointer',
              transition: 'all 200ms ease',
            }}
          >
            <Send size={13} />
          </button>
        </form>
      </div>
    </div>
  );
};
