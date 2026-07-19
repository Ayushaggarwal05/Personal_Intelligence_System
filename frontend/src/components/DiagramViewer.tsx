import React, { useState, useEffect, useRef } from 'react';
import { Layers, Activity, GitFork, Cpu } from 'lucide-react';
import mermaid from 'mermaid';

// Initialize Mermaid.js configuration
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

    // Reset container and compile Mermaid code markup
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
    <div style={{ flex: '1', display: 'flex', flexDirection: 'column', height: '100%', padding: '24px', overflowY: 'auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '24px' }}>
        <Layers size={24} style={{ color: 'var(--accent-cyan)' }} />
        <div>
          <h2 style={{ fontSize: '18px', fontWeight: 'bold' }}>Architectural Diagram Canvas</h2>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Mermaid.js vector graphs parsed from database definitions</p>
        </div>
      </div>

      {/* Selectors */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '20px' }}>
        {[
          { key: 'sequence', label: 'Controller sequence', icon: <Activity size={14} /> },
          { key: 'er', label: 'Database Schema ER', icon: <Layers size={14} /> },
          { key: 'api-flow', label: 'FastAPI Routes Flow', icon: <GitFork size={14} /> },
        ].map((btn) => (
          <button
            key={btn.key}
            onClick={() => setDiagType(btn.key as any)}
            disabled={!projectId}
            className="glow-btn"
            style={{
              padding: '8px 12px',
              fontSize: '12px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              background: diagType === btn.key ? 'var(--accent-gradient)' : 'rgba(255,255,255,0.02)',
              border: '1px solid var(--border-color)',
              color: diagType === btn.key ? '#fff' : 'var(--text-secondary)',
              opacity: !projectId ? 0.5 : 1,
            }}
          >
            {btn.icon}
            {btn.label}
          </button>
        ))}
      </div>

      {/* Rendering viewport */}
      <div className="glass-panel" style={{ flex: '1', display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '300px', background: '#121216', padding: '20px', overflow: 'auto' }}>
        {!projectId ? (
          <span style={{ color: 'var(--text-muted)', fontSize: '13px' }}>Register a workspace path to render flow diagrams</span>
        ) : isLoading ? (
          <Cpu size={32} className="animate-spin" style={{ color: 'var(--accent-cyan)', animation: 'spin 1.5s linear infinite' }} />
        ) : (
          <div ref={containerRef} style={{ width: '100%', height: '100%', display: 'flex', justifyContent: 'center' }} />
        )}
      </div>
    </div>
  );
};
