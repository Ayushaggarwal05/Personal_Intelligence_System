import React, { useState } from 'react';
import { Folder, RefreshCw, CheckCircle2 } from 'lucide-react';

interface WorkspaceManagerProps {
  projectId: string | null;
  setProjectId: (id: string | null) => void;
  projectPath: string;
  setProjectPath: (path: string) => void;
  stats: any;
  setStats: (stats: any) => void;
  isScanning: boolean;
  setIsScanning: (scanning: boolean) => void;
}

export const WorkspaceManager: React.FC<WorkspaceManagerProps> = ({
  projectId, setProjectId, projectPath, setProjectPath,
  stats: _stats, setStats, isScanning, setIsScanning,
}) => {
  const [inputPath, setInputPath] = useState('');
  const [error,     setError]     = useState<string | null>(null);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!inputPath.trim()) return;
    try {
      const res  = await fetch('http://localhost:8000/api/workspace/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: inputPath }),
      });
      const data = await res.json();
      if (res.ok) {
        setProjectId(data.id);
        setProjectPath(data.path);
        handleScan(data.id, data.path);
      } else {
        setError(data.detail || 'Failed to register workspace.');
      }
    } catch {
      setError('Backend service is offline.');
    }
  };

  const handleScan = async (pId: string, path: string) => {
    setIsScanning(true);
    setError(null);
    try {
      const res = await fetch('http://localhost:8000/api/projects/scan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path }),
      });
      if (res.ok) fetchStats(pId);
      else setError('Scanning workspace failed.');
    } catch {
      setError('Failed to scan workspace.');
    } finally {
      setIsScanning(false);
    }
  };

  const fetchStats = async (pId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/workspace/statistics/${pId}`);
      if (res.ok) setStats(await res.json());
    } catch { /* noop */ }
  };

  return (
    <div className="asta-sidebar-card flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center gap-2 text-txtPrimary">
        <Folder size={16} style={{ color: 'var(--sage)' }} />
        <span
          className="font-heading font-semibold"
          style={{ fontSize: 13, color: 'var(--txt-primary)', letterSpacing: '0.01em' }}
        >
          Workspace
        </span>
      </div>

      {!projectId ? (
        /* ── Registration Form ── */
        <form onSubmit={handleRegister} className="flex flex-col gap-4">
          <span style={{ fontSize: 11.5, color: 'var(--txt-muted)', lineHeight: '1.4' }}>
            Connect your project folder to begin.
          </span>
          <input
            type="text"
            placeholder="Absolute folder path..."
            value={inputPath}
            onChange={(e) => setInputPath(e.target.value)}
            className="asta-input-premium"
          />
          <button
            type="submit"
            className="asta-btn-premium w-full"
          >
            Register &amp; Scan
          </button>
          {error && (
            <span style={{ fontSize: 10, color: 'var(--error)', fontFamily: 'JetBrains Mono, monospace' }}>
              {error}
            </span>
          )}
        </form>
      ) : (
        /* ── Registered State ── */
        <div className="flex flex-col gap-4">
          {/* Active Path */}
          <div
            className="rounded-2xl px-4 py-3"
            style={{
              background: 'rgba(0, 0, 0, 0.2)',
              border: '1px solid var(--border)',
            }}
          >
            <div className="flex items-center gap-1.5 mb-1.5">
              <CheckCircle2 size={12} style={{ color: 'var(--success)' }} />
              <span style={{ fontSize: 10, color: 'var(--txt-muted)', fontFamily: 'JetBrains Mono, monospace', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                Active Dir
              </span>
            </div>
            <code
              className="break-all block"
              style={{ fontSize: 11, color: 'var(--sage)', fontFamily: 'JetBrains Mono, monospace', lineHeight: 1.4 }}
            >
              {projectPath}
            </code>
          </div>

          {/* Rescan */}
          <button
            onClick={() => handleScan(projectId, projectPath)}
            disabled={isScanning}
            className="asta-btn-premium w-full flex items-center justify-center gap-2"
          >
            <RefreshCw size={14} className={isScanning ? 'animate-spin' : ''} />
            {isScanning ? 'Indexing...' : 'Rescan Codebase'}
          </button>
          {error && (
            <span style={{ fontSize: 10, color: 'var(--error)', fontFamily: 'JetBrains Mono, monospace' }}>
              {error}
            </span>
          )}
        </div>
      )}
    </div>
  );
};
