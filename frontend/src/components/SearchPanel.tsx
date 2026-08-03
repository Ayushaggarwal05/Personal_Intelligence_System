import React, { useState, useEffect } from 'react';
import { Search, BookOpen, Tag, FileText } from 'lucide-react';

interface SearchPanelProps {
  projectId: string | null;
}

const FILTERS = [
  { key: null,       label: 'All'     },
  { key: 'file',     label: 'Files'   },
  { key: 'class',    label: 'Classes' },
  { key: 'function', label: 'Funcs'   },
  { key: 'route',    label: 'Routes'  },
] as const;

export const SearchPanel: React.FC<SearchPanelProps> = ({ projectId }) => {
  const [query,      setQuery]      = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [results,    setResults]    = useState<any[]>([]);
  const [filterType, setFilterType] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId || !query) { setSuggestions([]); return; }
    const t = setTimeout(async () => {
      try {
        const res = await fetch(
          `http://localhost:8000/api/search/suggestions?project_id=${projectId}&prefix=${encodeURIComponent(query)}`
        );
        if (res.ok) setSuggestions((await res.json()).suggestions || []);
      } catch { /* noop */ }
    }, 200);
    return () => clearTimeout(t);
  }, [query, projectId]);

  const handleSearch = async (q: string) => {
    if (!projectId || !q) return;
    setQuery(q);
    setSuggestions([]);
    try {
      let url = `http://localhost:8000/api/search?project_id=${projectId}&query=${encodeURIComponent(q)}`;
      if (filterType) url += `&type=${filterType}`;
      const res = await fetch(url);
      if (res.ok) setResults((await res.json()).results || []);
    } catch { /* noop */ }
  };

  return (
    <div
      className="rounded-card flex flex-col overflow-hidden flex-1 min-h-0"
      style={{
        background: 'var(--bg-card)',
        border: '1px solid rgba(255,255,255,0.05)',
        padding: '16px',
        gap: '12px',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Header */}
      <div className="flex items-center gap-2 flex-shrink-0">
        <BookOpen size={15} style={{ color: 'var(--accent-hover)' }} />
        <span
          className="font-heading font-semibold"
          style={{ fontSize: 12, color: 'var(--txt-second)' }}
        >
          Code Finder
        </span>
      </div>

      {/* Search Input */}
      <div className="relative flex-shrink-0">
        <input
          type="text"
          placeholder="Search symbols or files..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch(query)}
          className="asta-input"
          style={{ paddingRight: 36 }}
        />
        <Search
          size={13}
          onClick={() => handleSearch(query)}
          className="absolute right-3 cursor-pointer transition-colors"
          style={{ top: '50%', transform: 'translateY(-50%)', color: 'var(--txt-disabled)' }}
          onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--sage)')}
          onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--txt-disabled)')}
        />

        {/* Autocomplete */}
        {suggestions.length > 0 && (
          <div
            className="absolute left-0 right-0 z-20 overflow-y-auto"
            style={{
              top: 42,
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              borderRadius: 10,
              boxShadow: '0 8px 24px rgba(0,0,0,0.35)',
              maxHeight: 160,
            }}
          >
            {suggestions.map((s, i) => (
              <div
                key={i}
                onClick={() => handleSearch(s)}
                className="px-3 py-2 cursor-pointer transition-colors"
                style={{
                  fontSize: 11,
                  color: 'var(--txt-second)',
                  fontFamily: 'JetBrains Mono, monospace',
                  borderBottom: i < suggestions.length - 1 ? '1px solid rgba(255,255,255,0.04)' : 'none',
                }}
                onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-hover)')}
                onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
              >
                {s}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Filter chips */}
      <div className="flex gap-1.5 flex-shrink-0 flex-wrap">
        {FILTERS.map((f) => {
          const active = filterType === f.key;
          return (
            <button
              key={String(f.key)}
              onClick={() => setFilterType(f.key as string | null)}
              className="px-2.5 py-1 rounded-chip font-heading font-semibold transition-all cursor-pointer"
              style={{
                fontSize: 10,
                color: active ? 'var(--sage)' : 'var(--txt-disabled)',
                background: active ? 'rgba(77,124,115,0.14)' : 'transparent',
                border: active ? '1px solid rgba(77,124,115,0.28)' : '1px solid var(--border)',
                transition: 'all 220ms ease',
              }}
            >
              {f.label}
            </button>
          );
        })}
      </div>

      {/* Results */}
      <div className="flex-1 overflow-y-auto flex flex-col gap-2 min-h-0">
        {results.length === 0 ? (
          <div
            className="text-center py-6 font-heading"
            style={{ fontSize: 11, color: 'var(--txt-disabled)' }}
          >
            Enter a search parameter above
          </div>
        ) : (
          results.map((res, i) => (
            <div
              key={i}
              className="flex items-start gap-2.5 rounded-input px-2.5 py-2 transition-colors"
              style={{
                background: 'var(--bg-panel)',
                border: '1px solid rgba(255,255,255,0.04)',
                transition: 'border-color 220ms ease',
              }}
              onMouseEnter={(e) => ((e.currentTarget as HTMLDivElement).style.borderColor = 'rgba(255,255,255,0.09)')}
              onMouseLeave={(e) => ((e.currentTarget as HTMLDivElement).style.borderColor = 'rgba(255,255,255,0.04)')}
            >
              {res.type === 'file'
                ? <FileText size={14} style={{ color: 'var(--accent-hover)', marginTop: 2 }} />
                : <Tag      size={14} style={{ color: 'var(--sage)', marginTop: 2 }} />
              }
              <div className="flex-1 min-w-0">
                <span
                  className="block truncate font-heading font-medium"
                  style={{ fontSize: 11, color: 'var(--txt-primary)' }}
                >
                  {res.title}
                </span>
                <span
                  className="block uppercase"
                  style={{ fontSize: 9, color: 'var(--txt-disabled)', fontFamily: 'JetBrains Mono, monospace', letterSpacing: '0.05em' }}
                >
                  {res.type} · {res.source}
                </span>
                {res.snippet && (
                  <pre
                    className="mt-1.5 overflow-x-auto rounded"
                    style={{
                      fontSize: 9,
                      background: 'var(--bg-app)',
                      border: '1px solid var(--border)',
                      padding: '6px 8px',
                      color: 'var(--txt-muted)',
                      fontFamily: 'JetBrains Mono, monospace',
                      lineHeight: 1.5,
                    }}
                  >
                    {res.snippet}
                  </pre>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
