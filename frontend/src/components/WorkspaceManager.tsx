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
  stats, setStats, isScanning, setIsScanning,
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
    <div
      className="rounded-card flex flex-col gap-3"
      style={{
        background: 'var(--bg-card)',
        border: '1px solid rgba(255,255,255,0.05)',
        padding: '16px',
      }}
    >
      {/* Header */}
      <div className="flex items-center gap-2">
        <Folder size={15} style={{ color: 'var(--sage)' }} />
        <span
          className="font-heading font-semibold"
          style={{ fontSize: 12, color: 'var(--txt-second)' }}
        >
          Workspace Control
        </span>
      </div>

      {!projectId ? (
        /* ── Registration Form ── */
        <form onSubmit={handleRegister} className="flex flex-col gap-2">
          <input
            type="text"
            placeholder="Absolute folder path..."
            value={inputPath}
            onChange={(e) => setInputPath(e.target.value)}
            className="asta-input"
          />
          <button type="submit" className="asta-btn w-full">
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
        <div className="flex flex-col gap-3">

          {/* Active Path */}
          <div
            className="rounded-input px-3 py-2"
            style={{
              background: 'var(--bg-panel)',
              border: '1px solid var(--border)',
            }}
          >
            <div className="flex items-center gap-1.5 mb-1">
              <CheckCircle2 size={10} style={{ color: 'var(--success)' }} />
              <span style={{ fontSize: 9, color: 'var(--txt-disabled)', fontFamily: 'JetBrains Mono, monospace', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                Active Dir
              </span>
            </div>
            <code
              className="break-all block"
              style={{ fontSize: 10, color: 'var(--accent-hover)', fontFamily: 'JetBrains Mono, monospace', lineHeight: 1.5 }}
            >
              {projectPath}
            </code>
          </div>

          {/* Rescan */}
          <button
            onClick={() => handleScan(projectId, projectPath)}
            disabled={isScanning}
            className="asta-btn w-full flex items-center justify-center gap-2"
          >
            <RefreshCw size={13} className={isScanning ? 'animate-spin' : ''} />
            {isScanning ? 'Indexing...' : 'Rescan Codebase'}
          </button>

          {/* Stats Grid */}
          {stats && (
            <div className="grid grid-cols-2 gap-2">
              {[
                { label: 'Files Indexed', value: stats.total_files  || 0, accent: 'var(--sage)' },
                { label: 'Est. Tokens',   value: stats.total_tokens || 0, accent: 'var(--accent-hover)' },
              ].map(({ label, value, accent }) => (
                <div
                  key={label}
                  className="rounded-chip px-2.5 py-2"
                  style={{ background: 'var(--bg-panel)', border: '1px solid var(--border)' }}
                >
                  <span style={{ fontSize: 9, color: 'var(--txt-disabled)', display: 'block', marginBottom: 2, textTransform: 'uppercase', letterSpacing: '0.06em', fontFamily: 'JetBrains Mono, monospace' }}>
                    {label}
                  </span>
                  <span className="font-heading font-bold" style={{ fontSize: 15, color: accent }}>
                    {value.toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
