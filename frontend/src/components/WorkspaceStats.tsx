import { Sparkles, FileText, Cpu, Calendar } from "lucide-react";

interface WorkspaceStatsProps {
  projectId: string | null;
  stats: {
    total_files?: number;
    total_tokens?: number;
  } | null;
}

export function WorkspaceStats({ projectId, stats }: WorkspaceStatsProps) {
  if (!projectId || !stats) return null;

  const totalFiles = stats.total_files || 0;
  const totalTokens = stats.total_tokens || 0;

  const formatTokens = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + "M";
    if (num >= 1000) return (num / 1000).toFixed(1) + "K";
    return num.toLocaleString();
  };

  return (
    <div className="asta-sidebar-card flex flex-col gap-4">
      {/* Header */}
      <div className="flex items-center gap-2 text-txtPrimary">
        <Sparkles size={16} style={{ color: "var(--accent-hover)" }} />
        <span className="font-heading font-semibold" style={{ fontSize: 13, letterSpacing: "0.01em" }}>
          Workspace Stats
        </span>
      </div>

      {/* Stats list with soft icons */}
      <div className="flex flex-col gap-3">
        {/* Files Indexed */}
        <div className="flex items-center justify-between text-xs py-0.5">
          <div className="flex items-center gap-2 text-[var(--txt-muted)]">
            <FileText size={14} className="opacity-80" />
            <span>Files Indexed</span>
          </div>
          <span className="font-mono font-semibold text-[var(--txt-primary)] bg-[rgba(255,255,255,0.02)] px-2 py-0.5 rounded border border-[var(--border)]">
            {totalFiles}
          </span>
        </div>

        {/* Est. Tokens */}
        <div className="flex items-center justify-between text-xs py-0.5">
          <div className="flex items-center gap-2 text-[var(--txt-muted)]">
            <Cpu size={14} className="opacity-80" />
            <span>Tokens Estimate</span>
          </div>
          <span className="font-mono font-semibold text-[var(--accent-hover)] bg-[rgba(255,255,255,0.02)] px-2 py-0.5 rounded border border-[var(--border)]">
            {formatTokens(totalTokens)}
          </span>
        </div>

        {/* Last Scan */}
        <div className="flex items-center justify-between text-xs py-0.5">
          <div className="flex items-center gap-2 text-[var(--txt-muted)]">
            <Calendar size={14} className="opacity-80" />
            <span>Last Scan</span>
          </div>
          <span className="font-sans font-semibold text-[var(--sage)]">
            Today
          </span>
        </div>
      </div>
    </div>
  );
}
