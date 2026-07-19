import React, { useState } from 'react';
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
    <div className="p-4 mb-4 rounded-xl border border-white/10 bg-bgCard backdrop-blur-md hover:border-white/15 transition-all">
      <h3 className="flex items-center gap-2 text-sm text-gray-200 mb-3 font-semibold font-outfit">
        <Folder size={18} className="text-accentPurple" />
        Workspace Control
      </h3>

      {!projectId ? (
        <form onSubmit={handleRegister} className="flex flex-col gap-2">
          <input
            type="text"
            placeholder="Absolute workspace folder path..."
            value={inputPath}
            onChange={(e) => setInputPath(e.target.value)}
            className="w-full bg-black/20 border border-white/10 rounded-md p-2 text-xs text-white outline-none focus:border-accentPurple/50 transition-all"
          />
          <button type="submit" className="glow-btn py-2 text-xs w-full">
            Register & Scan
          </button>
          {error && <span className="text-red-400 text-[10px]">{error}</span>}
        </form>
      ) : (
        <div className="flex flex-col gap-3">
          <div className="text-xs bg-white/5 p-2 rounded-md border border-white/5">
            <span className="text-gray-400 block mb-1 text-[10px]">ACTIVE DIR</span>
            <code className="text-accentCyan break-all font-mono">{projectPath}</code>
          </div>

          <button
            onClick={() => handleScan(projectId, projectPath)}
            disabled={isScanning}
            className="glow-btn py-2 text-xs w-full flex items-center justify-center gap-2"
            style={{ opacity: isScanning ? 0.7 : 1 }}
          >
            <RefreshCw size={14} className={isScanning ? 'animate-spin' : ''} />
            {isScanning ? 'Indexing Crawler...' : 'Rescan Codebase'}
          </button>

          {stats && (
            <div className="grid grid-cols-2 gap-2">
              <div className="bg-white/2 p-2 rounded-md border border-white/5">
                <span className="text-gray-500 text-[9px] block">FILES INDEXED</span>
                <span className="text-base font-bold text-accentPurple">{stats.total_files || 0}</span>
              </div>
              <div className="bg-white/2 p-2 rounded-md border border-white/5">
                <span className="text-gray-500 text-[9px] block">EST. TOKENS</span>
                <span className="text-base font-bold text-accentCyan">{stats.total_tokens || 0}</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
