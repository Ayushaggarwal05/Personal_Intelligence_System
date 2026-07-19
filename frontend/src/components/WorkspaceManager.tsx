import { useState } from 'react';
import { Folder, RefreshCw } from 'lucide-react';

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
  projectId,
  setProjectId,
  projectPath,
  setProjectPath,
  stats,
  setStats,
  isScanning,
  setIsScanning,
}) => {
  const [inputPath, setInputPath] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!inputPath) return;

    try {
      const res = await fetch('http://localhost:8000/api/workspace/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: inputPath }),
      });
      const data = await res.json();
      if (res.ok) {
        setProjectId(data.id);
        setProjectPath(data.path);
        // Start initial scan automatically
        handleScan(data.id, data.path);
      } else {
        setError(data.detail || 'Failed to register workspace.');
      }
    } catch (err) {
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
      if (res.ok) {
        // Fetch stats
        fetchStats(pId);
      } else {
        setError('Scanning workspace failed.');
      }
    } catch (err) {
      setError('Failed to scan workspace.');
    } finally {
      setIsScanning(false);
    }
  };

  const fetchStats = async (pId: string) => {
    try {
      const res = await fetch(`http://localhost:8000/api/workspace/statistics/${pId}`);
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="workspace-manager glass-panel" style={{ padding: '16px', marginBottom: '16px' }}>
      <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '15px', color: 'var(--text-primary)', marginBottom: '12px' }}>
        <Folder size={18} className="text-purple" style={{ color: 'var(--accent-purple)' }} />
        Workspace Control
      </h3>

      {!projectId ? (
        <form onSubmit={handleRegister} style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <input
            type="text"
            placeholder="Absolute workspace folder path..."
            value={inputPath}
            onChange={(e) => setInputPath(e.target.value)}
            style={{
              background: 'rgba(0,0,0,0.2)',
              border: '1px solid var(--border-color)',
              borderRadius: '6px',
              padding: '8px',
              color: '#fff',
              fontSize: '13px',
              outline: 'none',
            }}
          />
          <button type="submit" className="glow-btn" style={{ padding: '8px' }}>
            Register & Scan
          </button>
          {error && <span style={{ color: '#ef4444', fontSize: '11px' }}>{error}</span>}
        </form>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div style={{ fontSize: '12px', background: 'rgba(255,255,255,0.03)', padding: '8px', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
            <span style={{ color: 'var(--text-secondary)', display: 'block', marginBottom: '4px' }}>ACTIVE DIR</span>
            <code style={{ color: 'var(--accent-cyan)', wordBreak: 'break-all' }}>{projectPath}</code>
          </div>

          <button
            onClick={() => handleScan(projectId, projectPath)}
            disabled={isScanning}
            className="glow-btn"
            style={{
              padding: '8px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              opacity: isScanning ? 0.7 : 1,
            }}
          >
            <RefreshCw size={14} className={isScanning ? 'animate-spin' : ''} style={{ animation: isScanning ? 'spin 1s linear infinite' : 'none' }} />
            {isScanning ? 'Indexing Crawler...' : 'Rescan Codebase'}
          </button>

          {stats && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '8px', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
                <span style={{ color: 'var(--text-muted)', fontSize: '10px', display: 'block' }}>FILES INDEXED</span>
                <span style={{ fontSize: '16px', fontWeight: 'bold', color: 'var(--accent-purple)' }}>{stats.total_files || 0}</span>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.02)', padding: '8px', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
                <span style={{ color: 'var(--text-muted)', fontSize: '10px', display: 'block' }}>EST. TOKENS</span>
                <span style={{ fontSize: '16px', fontWeight: 'bold', color: 'var(--accent-cyan)' }}>{stats.total_tokens || 0}</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
