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
    <div className="settings-drawer glass-panel" style={{ padding: '16px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '15px', color: 'var(--text-primary)' }}>
        <Settings size={18} style={{ color: 'var(--accent-purple)' }} />
        System Configurations
      </h3>

      {/* Model Provider Toggle */}
      <div>
        <span style={{ fontSize: '11px', color: 'var(--text-secondary)', display: 'block', marginBottom: '8px' }}>
          ACTIVE LLM REASONING ENGINE
        </span>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
          {[
            { id: 'local', label: 'Local Ollama', icon: <Cpu size={12} /> },
            { id: 'gemini', label: 'Gemini Cloud', icon: <BrainCircuit size={12} /> },
          ].map((item) => (
            <button
              key={item.id}
              onClick={() => handleProviderChange(item.id)}
              className="glow-btn"
              style={{
                padding: '6px',
                fontSize: '11px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '4px',
                background: provider === item.id ? 'var(--accent-gradient)' : 'rgba(255,255,255,0.02)',
                border: '1px solid var(--border-color)',
                color: provider === item.id ? '#fff' : 'var(--text-secondary)',
              }}
            >
              {item.icon}
              {item.label}
            </button>
          ))}
        </div>
        {message && <span style={{ color: 'var(--accent-cyan)', fontSize: '10px', marginTop: '6px', display: 'block' }}>{message}</span>}
      </div>

      {/* Weak Areas List */}
      <div>
        <span style={{ fontSize: '11px', color: 'var(--text-secondary)', display: 'block', marginBottom: '8px' }}>
          TECHNICAL WEAK TOPICS HISTORY
        </span>
        {weakTopics.length === 0 ? (
          <div style={{ background: 'rgba(255,255,255,0.01)', border: '1px solid var(--border-color)', borderRadius: '6px', padding: '10px', fontSize: '12px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <ShieldAlert size={14} />
            No weak topic areas detected yet
          </div>
        ) : (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {weakTopics.map((topic, idx) => (
              <span
                key={idx}
                style={{
                  background: 'rgba(239, 68, 68, 0.1)',
                  border: '1px solid rgba(239, 68, 68, 0.2)',
                  color: '#ef4444',
                  padding: '4px 8px',
                  borderRadius: '100px',
                  fontSize: '10px',
                  fontWeight: '500',
                }}
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
