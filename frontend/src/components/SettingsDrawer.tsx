import React, { useState, useEffect } from 'react';
import { Settings, Cpu, BrainCircuit, ShieldAlert } from 'lucide-react';

interface SettingsDrawerProps {
  projectId: string | null;
}

export const SettingsDrawer: React.FC<SettingsDrawerProps> = ({ projectId }) => {
  const [provider, setProvider] = useState('local');
  const [weakTopics, setWeakTopics] = useState<string[]>([]);
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const res = await fetch('http://localhost:8000/api/settings');
        if (res.ok) {
          const data = await res.json();
          setProvider(data.active_llm_provider || 'local');
        }
      } catch (err) {
        console.error(err);
      }
    };

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

  const handleProviderChange = async (newProv: string) => {
    setProvider(newProv);
    setMessage(null);
    try {
      const res = await fetch('http://localhost:8000/api/settings/provider', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ provider: newProv }),
      });
      if (res.ok) {
        setMessage(`LLM Provider switched to: ${newProv}`);
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-4 rounded-xl border border-white/10 bg-bgCard backdrop-blur-md flex flex-col gap-4 max-w-sm m-6 hover:border-white/15 transition-all">
      <h3 className="flex items-center gap-2 text-sm text-gray-200 font-semibold font-outfit">
        <Settings size={18} className="text-accentPurple" />
        System Configurations
      </h3>

      {/* Model Provider Toggle */}
      <div>
        <span className="text-[10px] text-gray-400 block mb-2 font-mono uppercase">
          ACTIVE LLM REASONING ENGINE
        </span>
        <div className="grid grid-cols-2 gap-1.5">
          {[
            { id: 'local', label: 'Local Ollama', icon: <Cpu size={12} /> },
            { id: 'gemini', label: 'Gemini Cloud', icon: <BrainCircuit size={12} /> },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => handleProviderChange(item.id)}
              className={`px-2 py-1.5 text-[11px] rounded border flex items-center justify-center gap-1.5 transition-all cursor-pointer ${
                provider === item.id
                  ? 'glow-btn text-white'
                  : 'border-white/10 bg-white/2 text-gray-400 hover:text-white'
              }`}
            >
              {item.icon}
              {item.label}
            </button>
          ))}
        </div>
        {message && <span className="text-accentCyan text-[10px] mt-1.5 block font-mono">{message}</span>}
      </div>

      {/* Weak Areas List */}
      <div className="mt-2">
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
