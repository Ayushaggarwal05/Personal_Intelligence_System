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
    <div className="asta-sidebar-card flex flex-col overflow-hidden flex-1 min-h-0 gap-4">
      {/* Header */}
      <div className="flex flex-col gap-2 flex-shrink-0">
        <div className="flex items-center gap-2 text-txtPrimary">
          <BookOpen size={16} style={{ color: 'var(--accent-hover)' }} />
          <span
            className="font-heading font-semibold"
            style={{ fontSize: 13, color: 'var(--txt-primary)', letterSpacing: '0.01em' }}
          >
            Code Finder
          </span>
        </div>
        <span style={{ fontSize: 11.5, color: 'var(--txt-muted)', lineHeight: '1.4' }}>
          Search files, classes, functions and routes instantly.
        </span>
      </div>

      {/* Search Input */}
      <div className="relative flex-shrink-0">
        <Search
          size={14}
          onClick={() => handleSearch(query)}
          className="absolute left-4 cursor-pointer transition-colors"
          style={{ top: '50%', transform: 'translateY(-50%)', color: 'var(--txt-disabled)', zIndex: 10 }}
          onMouseEnter={(e) => (e.currentTarget.style.color = 'var(--sage)')}
          onMouseLeave={(e) => (e.currentTarget.style.color = 'var(--txt-disabled)')}
        />
        <input
          type="text"
          placeholder="Search symbols or files..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch(query)}
          className="asta-input-premium"
          style={{ paddingLeft: 42 }}
        />

        {/* Autocomplete */}
        {suggestions.length > 0 && (
          <div
            className="absolute left-0 right-0 z-20 overflow-y-auto"
            style={{
              top: 54,
              background: 'var(--bg-card)',
              border: '1px solid var(--border)',
              borderRadius: 16,
              boxShadow: '0 10px 30px rgba(0,0,0,0.3)',
              maxHeight: 160,
            }}
          >
            {suggestions.map((s, i) => (
              <div
                key={i}
                onClick={() => handleSearch(s)}
                className="px-4 py-2.5 cursor-pointer transition-colors text-xs"
                style={{
                  color: 'var(--txt-second)',
                  fontFamily: 'JetBrains Mono, monospace',
                  borderBottom: i < suggestions.length - 1 ? '1px solid var(--border)' : 'none',
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
      <div className="flex gap-2 flex-shrink-0 flex-wrap">
        {FILTERS.map((f) => {
          const active = filterType === f.key;
          return (
            <button
              key={String(f.key)}
              onClick={() => setFilterType(f.key as string | null)}
              className={active ? 'asta-chip-active' : 'asta-chip-inactive'}
            >
              {f.label}
            </button>
          );
        })}
      </div>

      {/* Results */}
      <div className="flex-1 overflow-y-auto flex flex-col gap-2.5 min-h-0 scrollbar-thin">
        {results.length === 0 ? (
          <div className="flex flex-col items-center justify-center text-center py-8 px-2 select-none">
            <div
              className="w-12 h-12 rounded-2xl flex items-center justify-center mb-3.5"
              style={{
                background: 'rgba(255, 255, 255, 0.02)',
                border: '1px solid var(--border)',
              }}
            >
              <Search size={20} className="text-[var(--txt-disabled)] opacity-80" />
            </div>
            <h3
              className="font-heading font-semibold mb-1"
              style={{ fontSize: 13, color: 'var(--txt-second)' }}
            >
              Search your codebase
            </h3>
            <p
              className="text-[var(--txt-disabled)] leading-relaxed"
              style={{ fontSize: 10.5 }}
            >
              Find classes, files, functions, routes and symbols instantly.
            </p>
          </div>
        ) : (
          results.map((res, i) => (
            <div
              key={i}
              className="flex items-start gap-2.5 rounded-xl px-3 py-2.5 transition-all cursor-pointer"
              style={{
                background: 'rgba(0, 0, 0, 0.1)',
                border: '1px solid var(--border)',
                transition: 'all 220ms ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = 'var(--bg-hover)';
                e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = 'rgba(0,0,0,0.1)';
                e.currentTarget.style.borderColor = 'var(--border)';
              }}
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
