import { useState } from "react";
import { WorkspaceManager } from "./components/WorkspaceManager";
import { SearchPanel } from "./components/SearchPanel";
import { ChatWindow } from "./components/ChatWindow";
import { DiagramViewer } from "./components/DiagramViewer";
import { SettingsDrawer } from "./components/SettingsDrawer";
import { WorkspaceStats } from "./components/WorkspaceStats";
import { Layers, Settings, MessageSquare, Folder } from "lucide-react";

const TABS = [
  {
    id: "explain",
    label: "Interview Mentor",
    icon: <MessageSquare size={14} />,
  },
  { id: "diagrams", label: "Diagram Canvas", icon: <Layers size={14} /> },
  { id: "settings", label: "Settings", icon: <Settings size={14} /> },
] as const;

type TabId = (typeof TABS)[number]["id"];

export default function App() {
  const [projectId, setProjectId] = useState<string | null>(null);
  const [projectPath, setProjectPath] = useState<string>("");
  const [stats, setStats] = useState<any>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [activeTab, setActiveTab] = useState<TabId>("explain");

  return (
    <div
      className="flex h-screen w-screen overflow-hidden"
      style={{ background: "var(--bg-app)", color: "var(--txt-primary)" }}
    >
      {/* ── Sidebar ───────────────────────────────────────────── */}
      <aside
        className="flex flex-col h-screen overflow-hidden flex-shrink-0 sidebar-bg"
        style={{
          width: 250,
          borderRight: "1px solid var(--border)",
        }}
      >
        {/* Logo Lockup */}
        <div className="flex items-center gap-3 px-6 pt-7 pb-3 select-none">
          {/* Console badge */}
          <div
            className="flex-shrink-0 rounded-xl flex items-center justify-center"
            style={{
              width: 36,
              height: 36,
              background:
                "linear-gradient(135deg, var(--accent) 0%, var(--sage) 100%)",
              boxShadow: "0 6px 18px rgba(77,124,115,.12)",
            }}
          >
            <span
              className="font-mono font-black leading-none select-none"
              style={{
                fontSize: 12.5,
                color: "var(--bg-card)",
              }}
            >
              &gt;_&lt;
            </span>
          </div>

          <div className="min-w-0">
            <div
              className="font-heading font-bold tracking-tight leading-none"
              style={{
                fontSize: 16.5,
                color: "var(--txt-primary)",
              }}
            >
              ASTA
            </div>

            <div
              className="font-mono uppercase mt-1"
              style={{
                fontSize: 8.5,
                letterSpacing: "0.18em",
                color: "var(--txt-muted)",
              }}
            >
              PERSONAL ENG INTEL
            </div>
          </div>
        </div>

        {/* Sidebar Body */}
        <div className="flex flex-col gap-10 flex-1 px-5 pt-4 pb-8 overflow-y-auto min-h-0">
          <WorkspaceManager
            projectId={projectId}
            setProjectId={setProjectId}
            projectPath={projectPath}
            setProjectPath={setProjectPath}
            stats={stats}
            setStats={setStats}
            isScanning={isScanning}
            setIsScanning={setIsScanning}
          />
          <WorkspaceStats projectId={projectId} stats={stats} />
          <SearchPanel projectId={projectId} />
        </div>

        {/* Sidebar Footer */}
        <div className="px-6 py-4 flex items-center justify-between border-t border-[var(--border)] mt-auto bg-[rgba(0,0,0,0.1)]">
          <div className="flex items-center gap-2">
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--success)] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[var(--success)]"></span>
            </span>
            <span
              className="font-mono uppercase select-none text-txtPrimary"
              style={{
                fontSize: 9,
                letterSpacing: "0.08em",
                color: "var(--txt-muted)",
              }}
            >
              Local Model Connected
            </span>
          </div>
          <span
            className="font-mono uppercase select-none"
            style={{
              fontSize: 9,
              letterSpacing: "0.05em",
              color: "var(--txt-disabled)",
            }}
          >
            ASTA v1.0
          </span>
        </div>
      </aside>

      {/* ── Main Area ─────────────────────────────────────────── */}
      <main
        className="flex flex-col flex-1 h-screen overflow-hidden"
        style={{ background: "var(--bg-app)" }}
      >
        <header
          className="flex items-center justify-between px-6 py-4 flex-shrink-0 select-none"
          style={{
            background: "var(--bg-sidebar)",
            borderBottom: "1px solid var(--border)",
          }}
        >
          {/* Active Context Title */}
          <div className="min-w-0">
            {activeTab === "explain" && (
              <>
                <h2
                  className="font-heading font-bold tracking-tight text-txtPrimary animate-fade-in"
                  style={{ fontSize: 13 }}
                >
                  Architecture &amp; Memory Explainer
                </h2>
                <p
                  className="font-mono text-txtMuted mt-0.5 animate-fade-in"
                  style={{ fontSize: 9, letterSpacing: "0.02em" }}
                >
                  Design trade-offs · Implementation details · Interview prep
                </p>
              </>
            )}
            {activeTab === "diagrams" && (
              <>
                <h2
                  className="font-heading font-bold tracking-tight text-txtPrimary animate-fade-in"
                  style={{ fontSize: 13 }}
                >
                  Architectural Diagram Canvas
                </h2>
                <p
                  className="font-mono text-txtMuted mt-0.5 animate-fade-in"
                  style={{ fontSize: 9, letterSpacing: "0.02em" }}
                >
                  Mermaid.js vector graphs parsed from database definitions
                </p>
              </>
            )}
            {activeTab === "settings" && (
              <>
                <h2
                  className="font-heading font-bold tracking-tight text-txtPrimary animate-fade-in"
                  style={{ fontSize: 13 }}
                >
                  System Configurations
                </h2>
                <p
                  className="font-mono text-txtMuted mt-0.5 animate-fade-in"
                  style={{ fontSize: 9, letterSpacing: "0.02em" }}
                >
                  Configure AI models and workspace settings
                </p>
              </>
            )}
          </div>

          {/* Navigation Tab Segment Control */}
          <div className="flex items-center gap-1 bg-black/25 p-1 rounded-xl border border-white/5 flex-shrink-0">
            {TABS.map((tab) => {
              const isActive = activeTab === tab.id;
              const isDisabled = !projectId && tab.id !== "settings";
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  disabled={isDisabled}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg font-heading font-semibold transition-all"
                  style={{
                    fontSize: 11,
                    cursor: isDisabled ? "not-allowed" : "pointer",
                    opacity: isDisabled ? 0.38 : 1,
                    color: isActive ? "var(--txt-primary)" : "var(--txt-muted)",
                    background: isActive ? "var(--bg-hover)" : "transparent",
                    border: "none",
                    transition: "all 220ms ease",
                  }}
                  onMouseEnter={(e) => {
                    if (!isDisabled && !isActive) {
                      (e.currentTarget as HTMLButtonElement).style.color =
                        "var(--txt-second)";
                      (e.currentTarget as HTMLButtonElement).style.background =
                        "rgba(255,255,255,0.03)";
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (!isDisabled && !isActive) {
                      (e.currentTarget as HTMLButtonElement).style.color =
                        "var(--txt-muted)";
                      (e.currentTarget as HTMLButtonElement).style.background =
                        "transparent";
                    }
                  }}
                >
                  <span
                    style={{ color: isActive ? "var(--accent)" : "inherit" }}
                  >
                    {tab.icon}
                  </span>
                  {tab.label}
                </button>
              );
            })}
          </div>
        </header>

        {/* Active Content */}
        <section className="flex-1 overflow-hidden relative">
          {activeTab === "explain" && <ChatWindow projectId={projectId} />}
          {activeTab === "diagrams" && <DiagramViewer projectId={projectId} />}
          {activeTab === "settings" && <SettingsDrawer projectId={projectId} />}

          {isScanning && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/60 backdrop-blur-md z-50 animate-fade-in">
              <div className="asta-sidebar-card flex flex-col items-center gap-6 p-10 max-w-sm text-center border border-[var(--accent)]/30 shadow-[0_0_50px_rgba(77,124,115,0.15)] rounded-3xl">
                {/* Scanner animation node */}
                <div className="relative w-20 h-20 rounded-2xl border border-[var(--accent)] flex items-center justify-center overflow-hidden">
                  <div className="absolute inset-0 bg-gradient-to-b from-transparent via-[var(--accent)]/20 to-transparent animate-pulse" />
                  <Folder
                    size={32}
                    className="text-[var(--accent)] animate-bounce"
                  />
                </div>
                <div className="flex flex-col gap-2">
                  <h3 className="font-heading font-bold text-sm text-[var(--txt-primary)]">
                    Indexing Project Workspace
                  </h3>
                  <p className="text-xs text-[var(--txt-muted)] leading-relaxed">
                    ASTA is reading files, parsing code symbols, and building
                    your personal engineer intelligence database.
                  </p>
                </div>
                {/* Progress bar simulation */}
                <div className="w-full h-1 bg-[rgba(255,255,255,0.05)] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-[var(--accent)] animate-[shimmer_1.5s_infinite]"
                    style={{ width: "60%" }}
                  />
                </div>
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}
