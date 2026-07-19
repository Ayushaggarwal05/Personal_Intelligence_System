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
    <div className="flex-1 flex flex-col h-full p-6 overflow-y-auto bg-black/10 animate-fade-in">
      <div className="flex items-center gap-2 mb-6">
        <Layers size={24} className="text-accentCyan" />
        <div>
          <h2 className="text-lg font-bold text-gray-100 font-outfit">Architectural Diagram Canvas</h2>
          <p className="text-xs text-gray-400">Mermaid.js vector graphs parsed from database definitions</p>
        </div>
      </div>

      {/* Selectors */}
      <div className="flex gap-2 mb-5 overflow-x-auto pb-1">
        {[
          { key: 'sequence', label: 'Controller Sequence', icon: <Activity size={14} /> },
          { key: 'er', label: 'Database Schema ER', icon: <Layers size={14} /> },
          { key: 'api-flow', label: 'FastAPI Routes Flow', icon: <GitFork size={14} /> },
        ].map((btn) => (
          <button
            key={btn.key}
            onClick={() => setDiagType(btn.key as any)}
            disabled={!projectId}
            className={`px-3 py-2 text-xs rounded border flex items-center gap-1.5 transition-all cursor-pointer ${
              diagType === btn.key
                ? 'glow-btn text-white'
                : 'border-white/10 bg-white/2 text-gray-400 hover:text-white'
            }`}
            style={{ opacity: !projectId ? 0.5 : 1 }}
          >
            {btn.icon}
            {btn.label}
          </button>
        ))}
      </div>

      {/* Rendering viewport */}
      <div className="glass-panel flex-1 flex items-center justify-center min-h-[300px] bg-bgSidebar p-5 overflow-auto border border-white/10 rounded-xl">
        {!projectId ? (
          <span className="text-gray-500 text-xs font-outfit">Register a workspace path to render flow diagrams</span>
        ) : isLoading ? (
          <Cpu size={32} className="animate-spin text-accentCyan" />
        ) : (
          <div ref={containerRef} className="w-full h-full flex justify-center" />
        )}
      </div>
    </div>
  );
};
