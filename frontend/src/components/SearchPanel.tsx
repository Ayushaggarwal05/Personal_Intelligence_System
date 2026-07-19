import React, { useState, useEffect } from 'react';
import { Search, Compass, Tag, FileText } from 'lucide-react';

interface SearchPanelProps {
  projectId: string | null;
}

export const SearchPanel: React.FC<SearchPanelProps> = ({ projectId }) => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [results, setResults] = useState<any[]>([]);
  const [filterType, setFilterType] = useState<string | null>(null);

  useEffect(() => {
    if (!projectId || !query) {
      setSuggestions([]);
      return;
    }

    const fetchSuggestions = async () => {
      try {
        const res = await fetch(
          `http://localhost:8000/api/search/suggestions?project_id=${projectId}&prefix=${encodeURIComponent(query)}`
        );
        if (res.ok) {
          const data = await res.json();
          setSuggestions(data.suggestions || []);
        }
      } catch (err) {
        console.error(err);
      }
    };

    const delayDebounceFn = setTimeout(() => {
      fetchSuggestions();
    }, 200);

    return () => clearTimeout(delayDebounceFn);
  }, [query, projectId]);

  const handleSearch = async (searchQuery: string) => {
    if (!projectId || !searchQuery) return;
    setQuery(searchQuery);
    setSuggestions([]);

    let url = `http://localhost:8000/api/search?project_id=${projectId}&query=${encodeURIComponent(searchQuery)}`;
    if (filterType) {
      url += `&type=${filterType}`;
    }

    try {
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setResults(data.results || []);
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="search-panel glass-panel" style={{ padding: '16px', flex: '1', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
      <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '15px', color: 'var(--text-primary)', marginBottom: '12px' }}>
        <Compass size={18} style={{ color: 'var(--accent-cyan)' }} />
        Code Finder
      </h3>

      <div style={{ position: 'relative', marginBottom: '8px' }}>
        <input
          type="text"
          placeholder="Search symbols or files..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch(query)}
          style={{
            width: '100%',
            background: 'rgba(0,0,0,0.2)',
            border: '1px solid var(--border-color)',
            borderRadius: '6px',
            padding: '8px 28px 8px 8px',
            color: '#fff',
            fontSize: '13px',
            outline: 'none',
            boxSizing: 'border-box',
          }}
        />
        <Search
          size={14}
          onClick={() => handleSearch(query)}
          style={{ position: 'absolute', right: '10px', top: '10px', cursor: 'pointer', color: 'var(--text-muted)' }}
        />

        {suggestions.length > 0 && (
          <div style={{
            position: 'absolute',
            top: '36px',
            left: 0,
            right: 0,
            background: 'var(--bg-sidebar)',
            border: '1px solid var(--border-color)',
            borderRadius: '6px',
            zIndex: 10,
            maxHeight: '150px',
            overflowY: 'auto',
            boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
          }}>
            {suggestions.map((sug, idx) => (
              <div
                key={idx}
                onClick={() => handleSearch(sug)}
                style={{ padding: '8px', fontSize: '12px', cursor: 'pointer', borderBottom: '1px solid rgba(255,255,255,0.02)' }}
                className="hover-bg-sug"
              >
                {sug}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Filter Types */}
      <div style={{ display: 'flex', gap: '4px', marginBottom: '12px', overflowX: 'auto', paddingBottom: '4px' }}>
        {[
          { key: null, label: 'All' },
          { key: 'file', label: 'Files' },
          { key: 'class', label: 'Classes' },
          { key: 'function', label: 'Funcs' },
          { key: 'route', label: 'Routes' },
        ].map((f) => (
          <button
            key={f.key}
            onClick={() => setFilterType(f.key)}
            style={{
              padding: '4px 8px',
              fontSize: '11px',
              borderRadius: '4px',
              border: '1px solid var(--border-color)',
              background: filterType === f.key ? 'rgba(147, 51, 234, 0.2)' : 'rgba(255,255,255,0.02)',
              color: filterType === f.key ? 'var(--accent-purple)' : 'var(--text-secondary)',
              cursor: 'pointer',
            }}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Results viewport */}
      <div style={{ flex: '1', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {results.length === 0 ? (
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '12px', padding: '20px 0' }}>
            Enter a search parameter above
          </div>
        ) : (
          results.map((res, idx) => (
            <div
              key={idx}
              style={{
                padding: '8px',
                borderRadius: '6px',
                background: 'rgba(255,255,255,0.01)',
                border: '1px solid var(--border-color)',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '8px',
              }}
            >
              {res.type === 'file' ? (
                <FileText size={16} style={{ color: 'var(--accent-cyan)', marginTop: '2px' }} />
              ) : (
                <Tag size={16} style={{ color: 'var(--accent-purple)', marginTop: '2px' }} />
              )}
              <div style={{ flex: '1', minWidth: '0' }}>
                <span style={{ fontSize: '12px', fontWeight: '500', color: 'var(--text-primary)', display: 'block', textOverflow: 'ellipsis', overflow: 'hidden', whiteSpace: 'nowrap' }}>
                  {res.title}
                </span>
                <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>
                  {res.type.toUpperCase()} • {res.source.toUpperCase()}
                </span>
                {res.snippet && (
                  <code style={{ display: 'block', fontSize: '10px', background: 'rgba(0,0,0,0.3)', padding: '4px', borderRadius: '4px', marginTop: '4px', overflowX: 'auto', color: 'var(--text-secondary)' }}>
                    {res.snippet}
                  </code>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
