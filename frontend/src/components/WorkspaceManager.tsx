import React, { useState } from "react";
import { Folder, RefreshCw, CheckCircle2 } from "lucide-react";

interface WorkspaceManagerProps {
  projectId: string | null;
  setProjectId: (id: string | null) => void;
  projectPath: string;
  setProjectPath: (path: string) => void;
  stats: any;
  setStats: (stats: any) => void;
  isScanning: boolean;
  setIsScanning: (scanning: boolean) => void;
  isCollapsed?: boolean;
}

export const WorkspaceManager: React.FC<WorkspaceManagerProps> = ({
  projectId,
  setProjectId,
  projectPath,
  setProjectPath,
  stats: _stats,
  setStats,
  isScanning,
  setIsScanning,
  isCollapsed,
}) => {
  const [inputPath, setInputPath] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!inputPath.trim()) return;
    setIsScanning(true);
    try {
      const res = await fetch("http://localhost:8000/api/workspace/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: inputPath }),
      });
      const data = await res.json();
      if (res.ok) {
        setProjectId(data.id);
        setProjectPath(data.path);
        handleScan(data.id, data.path);
      } else {
        setError(data.detail || "Failed to register workspace.");
        setIsScanning(false);
      }
    } catch {
      setError("Backend service is offline.");
      setIsScanning(false);
    }
  };

  const handleScan = async (pId: string, path: string) => {
    setIsScanning(true);
    setError(null);
    try {
      const res = await fetch("http://localhost:8000/api/projects/scan", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path }),
      });
      if (res.ok) fetchStats(pId);
      else setError("Scanning workspace failed.");
    } catch {
      setError("Failed to scan workspace.");
    } finally {
      setIsScanning(false);
    }
  };

  const fetchStats = async (pId: string) => {
    try {
      const res = await fetch(
        `http://localhost:8000/api/workspace/statistics/${pId}`,
      );
      if (res.ok) setStats(await res.json());
    } catch {
      /* noop */
    }
  };

  if (isCollapsed) {
    return (
      <div
        className="flex flex-col items-center justify-center p-2 rounded-xl bg-white/5 border border-white/5 cursor-pointer hover:bg-white/10 transition-all"
        title={projectId ? `Active: ${projectPath}` : "Workspace Registration"}
        onClick={() => {
          if (projectId) handleScan(projectId, projectPath);
        }}
      >
        <Folder
          size={16}
          className={projectId ? "text-[var(--accent)]" : "text-txtMuted"}
        />
      </div>
    );
  }

  return (
    <div className="asta-sidebar-card flex flex-col gap-4">
      <hr />
      {/* Header */}
      <div className="flex items-center justify-between text-txtPrimary">
        <div className="flex items-center gap-2">
          <Folder size={16} style={{ color: "var(--sage)" }} />
          <span
            className="font-heading font-semibold"
            style={{
              fontSize: 13,
              color: "var(--txt-primary)",
              letterSpacing: "0.01em",
            }}
          >
            Workspace
          </span>
        </div>
        {projectId && (
          <span className="text-[9px] font-mono px-2 py-0.5 rounded-full bg-[var(--accent)]/10 text-[var(--accent)] border border-[var(--accent)]/20 uppercase tracking-widest font-semibold">
            Active
          </span>
        )}
      </div>

      {!projectId ? (
        /* ── Registration Form ── */
        <form onSubmit={handleRegister} className="flex flex-col gap-4">
          <span
            style={{
              fontSize: 11.5,
              color: "var(--txt-muted)",
              lineHeight: "1.4",
            }}
          >
            Connect your project folder to begin.
          </span>
          <input
            type="text"
            placeholder="Absolute folder path..."
            value={inputPath}
            onChange={(e) => setInputPath(e.target.value)}
            className="asta-input-premium"
          />
          <button type="submit" className="asta-btn-premium w-full">
            Register &amp; Scan
          </button>
          {error && (
            <span
              style={{
                fontSize: 10,
                color: "var(--error)",
                fontFamily: "JetBrains Mono, monospace",
              }}
            >
              {error}
            </span>
          )}
        </form>
      ) : (
        /* ── Registered State ── */
        <div className="flex flex-col gap-3">
          {/* Active Path Card */}
          <div
            className="rounded-2xl px-3.5 py-2.5 backdrop-blur-md"
            style={{
              background: "rgba(0, 0, 0, 0.25)",
              border: "1px solid var(--border)",
            }}
          >
            <div className="flex items-center justify-between mb-1">
              <div className="flex items-center gap-1.5">
                <CheckCircle2 size={12} style={{ color: "var(--success)" }} />
                <span
                  style={{
                    fontSize: 9.5,
                    color: "var(--txt-muted)",
                    fontFamily: "JetBrains Mono, monospace",
                    textTransform: "uppercase",
                    letterSpacing: "0.08em",
                  }}
                >
                  Indexed Path
                </span>
              </div>
              <button
                onClick={() => setProjectId(null)}
                className="text-[9px] font-mono text-txtMuted hover:text-txtPrimary transition-colors underline cursor-pointer"
                title="Disconnect & Change Project Path"
              >
                Change Path
              </button>
            </div>
            <code
              className="break-all block truncate"
              style={{
                fontSize: 10.5,
                color: "var(--sage)",
                fontFamily: "JetBrains Mono, monospace",
                lineHeight: 1.4,
              }}
              title={projectPath}
            >
              {projectPath}
            </code>
          </div>

          {/* Quick Action Re-index */}
          <button
            onClick={() => handleScan(projectId, projectPath)}
            disabled={isScanning}
            className="asta-btn-premium w-full flex items-center justify-center gap-2"
          >
            <RefreshCw size={13} className={isScanning ? "animate-spin" : ""} />
            {isScanning ? "Indexing Codebase..." : "Re-Index Workspace"}
          </button>
          {error && (
            <span
              style={{
                fontSize: 10,
                color: "var(--error)",
                fontFamily: "JetBrains Mono, monospace",
              }}
            >
              {error}
            </span>
          )}
        </div>
      )}
    </div>
  );
};
