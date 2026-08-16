import React, { useState, useEffect, useRef } from 'react';
import { Layers, Activity, GitFork, Cpu, Key, AlertTriangle, ShieldAlert, ArrowRight } from 'lucide-react';
import mermaid from 'mermaid';

mermaid.initialize({
  startOnLoad: false,
  theme: 'dark',
  securityLevel: 'loose',
  flowchart: { useMaxWidth: true, htmlLabels: true },
  sequence: { useMaxWidth: true, showSequenceNumbers: true },
  er: { useMaxWidth: true },
  themeVariables: {
    background: '#121216',
    primaryColor: '#a855f7',
    primaryTextColor: '#fff',
    lineColor: '#06b6d4',
  }
});

interface DiagramViewerProps {
  projectId: string | null;
  onOpenSettings?: () => void;
}

export const DiagramViewer: React.FC<DiagramViewerProps> = ({ projectId, onOpenSettings }) => {
  const [diagType, setDiagType] = useState<'er' | 'api-flow' | 'sequence'>('sequence');
  const [mermaidCode, setMermaidCode] = useState<string>('');
  const [errorState, setErrorState] = useState<{ code: string; detail: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!projectId) return;

    const fetchDiagram = async () => {
      setIsLoading(true);
      setErrorState(null);
      setMermaidCode('');

      try {
        const res = await fetch(`http://localhost:8000/api/diagrams/${diagType}/${projectId}`);
        if (res.ok) {
          const data = await res.json();
          if (data.error) {
            setErrorState({ code: data.code || 'GENERATION_FAILED', detail: data.detail || 'Failed to generate diagram.' });
          } else {
            setMermaidCode(data.mermaid_code || '');
          }
        } else {
          setErrorState({ code: 'SERVER_ERROR', detail: 'Failed to communicate with backend service.' });
        }
      } catch (err: any) {
        setErrorState({ code: 'NETWORK_ERROR', detail: err?.message || 'Network error occurred.' });
      } finally {
        setIsLoading(false);
      }
    };

    fetchDiagram();
  }, [projectId, diagType]);

  useEffect(() => {
    if (!mermaidCode || !containerRef.current || errorState) return;

    containerRef.current.innerHTML = `<div class="mermaid w-full h-full flex items-center justify-center">${mermaidCode}</div>`;
    try {
      mermaid.run({
        nodes: containerRef.current.querySelectorAll('.mermaid')
      });
    } catch (err) {
      console.error("Mermaid compile error:", err);
    }
  }, [mermaidCode, errorState]);

  return (
    <div className="flex-1 flex flex-col h-full p-6 overflow-y-auto bg-transparent animate-fade-in">
      <style>{`
        .mermaid-viewport svg {
          max-width: 100% !important;
          width: 100% !important;
          height: auto !important;
          min-height: 400px !important;
          max-height: 75vh !important;
        }
      `}</style>
      {/* Selectors */}
      <div className="flex gap-2 mb-5 overflow-x-auto pb-1 select-none">
        {[
          { key: 'sequence', label: 'Controller Sequence', icon: <Activity size={14} /> },
          { key: 'er', label: 'Database Schema ER', icon: <Layers size={14} /> },
          { key: 'api-flow', label: 'Backend Routes Flow', icon: <GitFork size={14} /> },
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

      {/* Rendering Viewport */}
      <div className="flex-1 flex items-center justify-center min-h-[350px] bg-bgCard p-5 overflow-auto border border-white/5 rounded-2xl shadow-xl">
        {!projectId ? (
          <span className="text-txtMuted text-xs font-mono">Register a workspace path to render flow diagrams</span>
        ) : isLoading ? (
          <div className="flex flex-col items-center gap-3">
            <Cpu size={32} className="animate-spin text-accent" />
            <span className="text-xs text-txtMuted font-mono">Generating dynamic Mermaid diagram...</span>
          </div>
        ) : errorState ? (
          /* Error State Alert Banner - No Fake Diagrams */
          <div className="flex flex-col items-center justify-center max-w-md text-center p-6 bg-black/30 border border-white/10 rounded-2xl gap-4">
            <div className="w-12 h-12 rounded-full bg-accent/10 border border-accent/20 flex items-center justify-center text-accent">
              {errorState.code === 'RATE_LIMITED' ? (
                <AlertTriangle size={22} className="text-amber-400" />
              ) : errorState.code === 'INVALID_KEY' ? (
                <ShieldAlert size={22} className="text-rose-400" />
              ) : (
                <Key size={22} className="text-accent" />
              )}
            </div>

            <div className="flex flex-col gap-1.5">
              <h4 className="font-heading font-bold text-sm text-txtPrimary">
                {errorState.code === 'RATE_LIMITED'
                  ? 'API Rate Limit Exceeded'
                  : errorState.code === 'INVALID_KEY'
                  ? 'Invalid API Key'
                  : 'Diagram Generation API Key Required'}
              </h4>
              <p className="text-xs text-txtMuted leading-relaxed font-sans">
                {errorState.code === 'NO_API_KEY'
                  ? 'Dynamic architectural diagram generation requires an API Key. Please add a Gemini or Groq API key in Settings.'
                  : errorState.detail}
              </p>
            </div>

            {onOpenSettings && (
              <button
                onClick={onOpenSettings}
                className="glow-btn py-2 px-4 text-xs flex items-center gap-2 cursor-pointer font-heading font-semibold mt-1"
              >
                <Key size={13} />
                Configure API Key in Settings
                <ArrowRight size={13} />
              </button>
            )}
          </div>
        ) : (
          <div ref={containerRef} className="w-full h-full flex items-center justify-center overflow-auto text-center mermaid-viewport" />
        )}
      </div>
    </div>
  );
};
