import React, { useState, useEffect } from 'react';
import { ShieldAlert, Key, Check } from 'lucide-react';

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
  const [skipActivation, setSkipActivation] = useState(() => {
    return localStorage.getItem("asta_skip_activation") === "true";
  });

  const handleToggleActivation = (e: React.ChangeEvent<HTMLInputElement>) => {
    const checked = e.target.checked;
    setSkipActivation(checked);
    localStorage.setItem("asta_skip_activation", checked ? "true" : "false");
  };

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
    <div className="w-full h-full flex items-center justify-center p-6 select-none animate-fade-in">
      <div className="p-6 rounded-2xl border border-white/5 bg-bgCard backdrop-blur-md flex flex-col gap-5 max-w-sm w-full shadow-xl hover:border-white/10 transition-all">
        {/* API Key Configuration Form */}
        <form onSubmit={handleSaveKeys} className="flex flex-col gap-3.5">
          <div>
            <span className="text-[10px] text-txtSecond font-heading font-semibold block">
              Diagram Generator AI Key
            </span>
            <span className="text-[9px] text-txtMuted font-mono block mb-2">
              Only 1 key is required for Mermaid diagram generation
            </span>

            <label className="text-[9px] text-txtMuted block mb-1.5 font-mono uppercase tracking-wider">
              GOOGLE GEMINI API KEY
            </label>
            <div className="relative">
              <input
                type="password"
                placeholder={hasGeminiKey ? "••••••••••••••••••••" : "Configure Gemini key..."}
                value={geminiInput}
                onChange={(e) => setGeminiInput(e.target.value)}
                className="w-full bg-black/25 border border-white/5 rounded-lg py-2 px-3 text-xs text-txtPrimary outline-none focus:border-accent/40 transition-all font-mono"
              />
              {hasGeminiKey && (
                <span className="absolute right-3 top-2.5 flex items-center gap-1 text-[9px] text-success font-mono">
                  <Check size={10} /> Active
                </span>
              )}
            </div>
          </div>

          {/* Visual OR Divider */}
          <div className="flex items-center gap-2 my-0.5 select-none">
            <div className="h-[1px] flex-1 bg-white/10" />
            <span className="text-[8.5px] font-mono font-bold uppercase tracking-widest text-txtMuted px-2.5 py-0.5 bg-black/40 border border-white/10 rounded-full">
              OR
            </span>
            <div className="h-[1px] flex-1 bg-white/10" />
          </div>

          <div>
            <label className="text-[9px] text-txtMuted block mb-1.5 font-mono uppercase tracking-wider">
              GROQ API KEY
            </label>
            <div className="relative">
              <input
                type="password"
                placeholder={hasGroqKey ? "••••••••••••••••••••" : "Configure Groq key..."}
                value={groqInput}
                onChange={(e) => setGroqInput(e.target.value)}
                className="w-full bg-black/25 border border-white/5 rounded-lg py-2 px-3 text-xs text-txtPrimary outline-none focus:border-accent/40 transition-all font-mono"
              />
              {hasGroqKey && (
                <span className="absolute right-3 top-2.5 flex items-center gap-1 text-[9px] text-success font-mono">
                  <Check size={10} /> Active
                </span>
              )}
            </div>
          </div>

          <button
            type="submit"
            className="glow-btn py-2 px-3 text-xs w-full flex items-center justify-center gap-1.5 cursor-pointer font-heading font-semibold mt-1"
          >
            <Key size={12} />
            Save AI Keys
          </button>

          {message && (
            <span className="text-sage text-[10px] block font-mono text-center mt-1">
              {message}
            </span>
          )}
        </form>

        {/* Startup Boot Sequence Toggle */}
        <div className="border-t border-white/5 pt-4 flex items-center justify-between">
          <div className="flex flex-col">
            <span className="text-[10px] text-txtPrimary font-heading font-semibold">
              Skip Startup Boot Sequence
            </span>
            <span className="text-[9px] text-txtMuted font-mono uppercase tracking-wider mt-0.5">
              Launch directly to workspace
            </span>
          </div>
          <input
            type="checkbox"
            checked={skipActivation}
            onChange={handleToggleActivation}
            className="w-4 h-4 rounded bg-black/45 border border-white/10 accent-accent cursor-pointer"
          />
        </div>

        {/* Weak Areas List */}
        <div className="border-t border-white/5 pt-4">
          <span className="text-[9px] text-txtMuted block mb-2.5 font-mono uppercase tracking-wider">
            TECHNICAL WEAK TOPICS HISTORY
          </span>
          {weakTopics.length === 0 ? (
            <div className="bg-black/10 border border-white/5 rounded-lg p-3 text-xs text-txtMuted flex items-center gap-2">
              <ShieldAlert size={13} className="text-txtDisabled" />
              No weak topic areas detected yet
            </div>
          ) : (
            <div className="flex flex-wrap gap-1.5">
              {weakTopics.map((topic, idx) => (
                <span
                  key={idx}
                  className="bg-red-500/10 border border-red-500/20 text-red-400 px-2.5 py-1 rounded-full text-[10px] font-medium"
                >
                  {topic}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
