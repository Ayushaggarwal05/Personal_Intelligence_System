import React, { useState, useEffect } from 'react';
import { Settings, ShieldAlert, Key, Check } from 'lucide-react';

interface SettingsDrawerProps {
  projectId: string | null;
}

export const SettingsDrawer: React.FC<SettingsDrawerProps> = ({ projectId }) => {
  const [hasGeminiKey, setHasGeminiKey] = useState(false);
  const [hasGroqKey, setHasGroqKey] = useState(false);
  const [geminiInput, setGeminiInput] = useState('');
  const [groqInput, setGroqInput] = useState('');
  const [weakTopics, setWeakTopics] = useState<string[]>([]);
  const [message, setMessage] = useState<string | null>(null);

  const fetchSettings = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/settings');
      if (res.ok) {
        const data = await res.json();
        setHasGeminiKey(data.has_gemini_key);
        setHasGroqKey(data.has_groq_key);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchSettings();
  }, []);

  useEffect(() => {
    if (!projectId) return;

    const fetchWeakTopics = async () => {
      try {
        const res = await fetch(`http://localhost:8000/api/memory/weak-areas/${projectId}`);
        if (res.ok) {
          const data = await res.json();
          setWeakTopics(data.weak_topics || []);
        }
      } catch (err) {
        console.error(err);
      }
    };

    fetchWeakTopics();
  }, [projectId]);

  const handleSaveKeys = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    try {
      const res = await fetch('http://localhost:8000/api/settings/keys', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          gemini_key: geminiInput ? geminiInput.trim() : undefined,
          groq_key: groqInput ? groqInput.trim() : undefined,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setHasGeminiKey(data.has_gemini_key);
        setHasGroqKey(data.has_groq_key);
        setGeminiInput('');
        setGroqInput('');
        setMessage('Credentials successfully saved to local config!');
      } else {
        setMessage('Failed to register credentials.');
      }
    } catch (err) {
      setMessage('Backend configuration service offline.');
    }
  };

  return (
    <div className="p-4 rounded-xl border border-white/10 bg-bgCard backdrop-blur-md flex flex-col gap-4 max-w-sm m-6 hover:border-white/15 transition-all">
      <h3 className="flex items-center gap-2 text-sm text-gray-200 font-semibold font-outfit">
        <Settings size={18} className="text-accentPurple" />
        System Configurations
      </h3>

      {/* API Key Configuration Form */}
      <form onSubmit={handleSaveKeys} className="flex flex-col gap-3">
        <div>
          <label className="text-[10px] text-gray-400 block mb-1 font-mono uppercase">
            GOOGLE GEMINI API KEY
          </label>
          <div className="relative">
            <input
              type="password"
              placeholder={hasGeminiKey ? "••••••••••••••••••••" : "Configure Gemini key..."}
              value={geminiInput}
              onChange={(e) => setGeminiInput(e.target.value)}
              className="w-full bg-black/20 border border-white/10 rounded-md py-1.5 px-2.5 text-xs text-white outline-none focus:border-accentPurple/50 transition-all font-mono"
            />
            {hasGeminiKey && (
              <span className="absolute right-2.5 top-2 flex items-center gap-1 text-[9px] text-emerald-400 font-mono">
                <Check size={10} /> Active
              </span>
            )}
          </div>
        </div>

        <div>
          <label className="text-[10px] text-gray-400 block mb-1 font-mono uppercase">
            GROQ API KEY
          </label>
          <div className="relative">
            <input
              type="password"
              placeholder={hasGroqKey ? "••••••••••••••••••••" : "Configure Groq key..."}
              value={groqInput}
              onChange={(e) => setGroqInput(e.target.value)}
              className="w-full bg-black/20 border border-white/10 rounded-md py-1.5 px-2.5 text-xs text-white outline-none focus:border-accentPurple/50 transition-all font-mono"
            />
            {hasGroqKey && (
              <span className="absolute right-2.5 top-2 flex items-center gap-1 text-[9px] text-emerald-400 font-mono">
                <Check size={10} /> Active
              </span>
            )}
          </div>
        </div>

        <button
          type="submit"
          className="glow-btn py-2 text-xs w-full flex items-center justify-center gap-1.5 cursor-pointer font-outfit"
        >
          <Key size={12} />
          Save AI Keys
        </button>

        {message && (
          <span className="text-accentCyan text-[10px] block font-mono text-center mt-1">
            {message}
          </span>
        )}
      </form>

      {/* Weak Areas List */}
      <div className="mt-2 border-t border-white/10 pt-4">
        <span className="text-[10px] text-gray-400 block mb-2 font-mono uppercase">
          TECHNICAL WEAK TOPICS HISTORY
        </span>
        {weakTopics.length === 0 ? (
          <div className="bg-white/1 border border-white/5 rounded-md p-2.5 text-xs text-gray-500 flex items-center gap-1.5">
            <ShieldAlert size={14} />
            No weak topic areas detected yet
          </div>
        ) : (
          <div className="flex flex-wrap gap-1.5">
            {weakTopics.map((topic, idx) => (
              <span
                key={idx}
                className="bg-red-500/10 border border-red-500/20 text-red-400 px-2 py-1 rounded-full text-[10px] font-medium"
              >
                {topic}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
