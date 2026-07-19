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
    <div className="p-4 rounded-xl border border-white/10 bg-bgCard backdrop-blur-md flex flex-col overflow-hidden flex-1 hover:border-white/15 transition-all">
      <h3 className="flex items-center gap-2 text-sm text-gray-200 mb-3 font-semibold font-outfit">
        <Compass size={18} className="text-accentCyan" />
        Code Finder
      </h3>

      <div className="relative mb-2">
        <input
          type="text"
          placeholder="Search symbols or files..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSearch(query)}
          className="w-full bg-black/20 border border-white/10 rounded-md py-2 pr-7 pl-2 text-xs text-white outline-none focus:border-accentCyan/50 transition-all"
        />
        <Search
          size={14}
          onClick={() => handleSearch(query)}
          className="absolute right-2.5 top-2.5 cursor-pointer text-gray-500 hover:text-white transition-all"
        />

        {suggestions.length > 0 && (
          <div className="absolute top-9 left-0 right-0 bg-bgSidebar border border-white/10 rounded-md z-10 max-h-[150px] overflow-y-auto shadow-2xl">
            {suggestions.map((sug, idx) => (
              <div
                key={idx}
                onClick={() => handleSearch(sug)}
                className="p-2 text-xs cursor-pointer border-b border-white/5 hover:bg-white/5 text-gray-300 transition-all"
              >
                {sug}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Filter Types */}
      <div className="flex gap-1 mb-3 overflow-x-auto pb-1">
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
            className={`px-2 py-1 text-[10px] rounded border transition-all cursor-pointer ${
              filterType === f.key
                ? 'border-accentPurple bg-accentPurple/20 text-accentPurple'
                : 'border-white/10 bg-white/2 text-gray-400 hover:text-white'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Results viewport */}
      <div className="flex-1 overflow-y-auto flex flex-col gap-2">
        {results.length === 0 ? (
          <div className="text-center text-gray-500 text-xs py-5 font-outfit">
            Enter a search parameter above
          </div>
        ) : (
          results.map((res, idx) => (
            <div
              key={idx}
              className="p-2.5 rounded-lg bg-white/5 border border-white/5 flex items-start gap-2 hover:border-white/10 transition-all"
            >
              {res.type === 'file' ? (
                <FileText size={16} className="text-accentCyan mt-0.5" />
              ) : (
                <Tag size={16} className="text-accentPurple mt-0.5" />
              )}
              <div className="flex-1 min-w-0">
                <span className="text-xs font-medium text-gray-100 block truncate">
                  {res.title}
                </span>
                <span className="text-[9px] text-gray-500 font-mono uppercase">
                  {res.type} • {res.source}
                </span>
                {res.snippet && (
                  <code className="block text-[9px] bg-black/30 p-1.5 rounded mt-1 overflow-x-auto text-gray-400 font-mono">
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
