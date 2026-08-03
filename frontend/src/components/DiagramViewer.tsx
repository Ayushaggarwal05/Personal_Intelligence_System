import React, { useState, useEffect, useRef } from 'react';
import { Layers, Activity, GitFork, Cpu } from 'lucide-react';
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'loose',
  themeVariables: {
    background: '#121216',
    primaryColor: '#a855f7',
    primaryTextColor: '#fff',
    lineColor: '#06b6d4',
  }
});

interface DiagramViewerProps {
  projectId: string | null;
}

export const DiagramViewer: React.FC<DiagramViewerProps> = ({ projectId }) => {
  const [diagType, setDiagType] = useState<'er' | 'api-flow' | 'sequence'>('sequence');
  const [mermaidCode, setMermaidCode] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!projectId) return;

    const fetchDiagram = async () => {
      setIsLoading(true);
      try {
        const res = await fetch(`http://localhost:8000/api/diagrams/${diagType}/${projectId}`);
        if (res.ok) {
          const data = await res.json();
          setMermaidCode(data.mermaid_code || '');
        }
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDiagram();
  }, [projectId, diagType]);

  useEffect(() => {
    if (!mermaidCode || !containerRef.current) return;

    containerRef.current.innerHTML = `<div class="mermaid">${mermaidCode}</div>`;
    try {
      mermaid.run({
        nodes: containerRef.current.querySelectorAll('.mermaid')
      });
    } catch (err) {
      console.error("Mermaid compile error:", err);
    }
  }, [mermaidCode]);

  return (
    <div className="flex-1 flex flex-col h-full p-6 overflow-y-auto bg-transparent animate-fade-in">
      {/* Selectors */}
      <div className="flex gap-2 mb-5 overflow-x-auto pb-1 select-none">
        {[
          { key: 'sequence', label: 'Controller Sequence', icon: <Activity size={14} /> },
          { key: 'er', label: 'Database Schema ER', icon: <Layers size={14} /> },
          { key: 'api-flow', label: 'FastAPI Routes Flow', icon: <GitFork size={14} /> },
        ].map((btn) => (
          <button
            key={btn.key}
            onClick={() => setDiagType(btn.key as any)}
            disabled={!projectId}
            className={`px-3 py-2 text-xs rounded-lg border flex items-center gap-1.5 transition-all cursor-pointer ${
              diagType === btn.key
                ? 'glow-btn text-white'
                : 'border-white/5 bg-black/15 text-txtMuted hover:text-txtPrimary'
            }`}
            style={{ opacity: !projectId ? 0.5 : 1 }}
          >
            {btn.icon}
            {btn.label}
          </button>
        ))}
      </div>

      {/* Rendering viewport */}
      <div className="flex-1 flex items-center justify-center min-h-[300px] bg-bgCard p-5 overflow-auto border border-white/5 rounded-2xl shadow-xl">
        {!projectId ? (
          <span className="text-txtMuted text-xs font-mono">Register a workspace path to render flow diagrams</span>
        ) : isLoading ? (
          <Cpu size={32} className="animate-spin text-accent" />
        ) : (
          <div ref={containerRef} className="w-full h-full flex justify-center" />
        )}
      </div>
    </div>
  );
};
