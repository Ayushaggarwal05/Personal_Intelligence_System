import { useState } from "react";
import { WorkspaceManager } from "./components/WorkspaceManager";
import { SearchPanel } from "./components/SearchPanel";
import { ChatWindow } from "./components/ChatWindow";
import { DiagramViewer } from "./components/DiagramViewer";
import { SettingsDrawer } from "./components/SettingsDrawer";
import { WorkspaceStats } from "./components/WorkspaceStats";
import {
  Layers,
  Settings,
  MessageSquare,
  Folder,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { ActivationScreen } from "./components/ActivationScreen";

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
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [showActivation, setShowActivation] = useState(() => {
    return localStorage.getItem("asta_skip_activation") !== "true";
  });

  return (
    <div
      className="flex h-screen w-screen overflow-hidden p-3 gap-3"
      style={{ background: "#050908", color: "var(--txt-primary)" }}
    >
      {showActivation && (
        <ActivationScreen onComplete={() => setShowActivation(false)} />
      )}
      {/* ── Sidebar Floating Panel ───────────────────────────────────────────── */}
      <aside
        className="flex flex-col h-full overflow-hidden flex-shrink-0 rounded-3xl bg-[#0a120f] border border-[rgba(45,106,90,0.28)] shadow-2xl transition-all duration-300 ease-in-out relative z-30"
        style={{
          width: isSidebarCollapsed ? 64 : 260,
        }}
      >
        {/* Logo Lockup & Collapse Toggle */}
        <div
          className={`flex items-center ${isSidebarCollapsed ? "justify-center px-2 py-4" : "justify-between px-5 pt-6 pb-3"} select-none`}
        >
          <div className="flex items-center gap-3 min-w-0">
            {/* Console badge */}
            <div
              className="flex-shrink-0 rounded-xl flex items-center justify-center cursor-pointer transition-transform hover:scale-105"
              onClick={() => setIsSidebarCollapsed(!isSidebarCollapsed)}
              style={{
                width: 36,
                height: 36,
                background:
                  "linear-gradient(135deg, var(--accent) 0%, var(--sage) 100%)",
                boxShadow: "0 6px 18px rgba(45,106,90,0.25)",
              }}
              title={
                isSidebarCollapsed
                  ? "Expand Sidebar"
                  : "ASTA Engineering Intelligence"
              }
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

            {!isSidebarCollapsed && (
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
            )}
          </div>

          {/* Collapse Button */}
          {!isSidebarCollapsed && (
            <button
              onClick={() => setIsSidebarCollapsed(true)}
              className="p-1.5 rounded-lg text-txtMuted hover:text-txtPrimary hover:bg-white/5 transition-all cursor-pointer border border-transparent hover:border-white/10"
              title="Collapse Sidebar"
            >
              <ChevronLeft size={16} />
            </button>
          )}
        </div>

        {/* Collapsed Expand Quick Button */}
        {isSidebarCollapsed && (
          <div className="flex justify-center pb-2">
            <button
              onClick={() => setIsSidebarCollapsed(false)}
              className="p-1.5 rounded-lg text-txtMuted hover:text-txtPrimary hover:bg-white/5 transition-all cursor-pointer border border-white/5"
              title="Expand Sidebar"
            >
              <ChevronRight size={14} />
            </button>
          </div>
        )}

        {/* Sidebar Body */}
        <div
          className={`flex flex-col gap-6 flex-1 ${isSidebarCollapsed ? "px-2 py-4" : "px-4 pt-3 pb-6"} overflow-y-auto min-h-0 scrollbar-thin`}
        >
          <WorkspaceManager
            projectId={projectId}
            setProjectId={setProjectId}
            projectPath={projectPath}
            setProjectPath={setProjectPath}
            stats={stats}
            setStats={setStats}
            isScanning={isScanning}
            setIsScanning={setIsScanning}
            isCollapsed={isSidebarCollapsed}
          />
          <WorkspaceStats
            projectId={projectId}
            stats={stats}
            isCollapsed={isSidebarCollapsed}
          />
          <SearchPanel projectId={projectId} isCollapsed={isSidebarCollapsed} />
        </div>

        {/* Sidebar Footer */}
        <div
          className={`${isSidebarCollapsed ? "px-2 py-3 justify-center" : "px-4 py-3 justify-between"} flex items-center border-t border-[rgba(45,106,90,0.2)] mt-auto bg-[rgba(0,0,0,0.2)] select-none`}
        >
          <div
            className="flex items-center gap-2"
            title="Local Model Connected: Qwen 2.5 3B (8K Context)"
          >
            <span className="flex h-2 w-2 relative flex-shrink-0">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--success)] opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-[var(--success)]"></span>
            </span>
            {!isSidebarCollapsed && (
              <div className="flex flex-col">
                <span
                  className="font-mono uppercase text-txtPrimary font-semibold"
                  style={{
                    fontSize: 8.5,
                    letterSpacing: "0.06em",
                    color: "var(--txt-primary)",
                  }}
                >
                  Local Model Connected
                </span>
                <span
                  className="font-mono"
                  style={{
                    fontSize: 8,
                    color: "var(--txt-muted)",
                  }}
                >
                  Qwen 2.5 3B · 8K Context
                </span>
              </div>
            )}
          </div>
          {!isSidebarCollapsed && (
            <span className="font-mono uppercase text-[9px] text-[var(--txt-disabled)]">
              v1.0
            </span>
          )}
        </div>
      </aside>

      {/* ── Main Area Floating Panel ─────────────────────────────────────────── */}
      <main
        className="flex flex-col flex-1 h-full overflow-hidden rounded-3xl bg-[#0a120f] border border-[rgba(45,106,90,0.28)] shadow-2xl"
      >
        <header
          className="flex items-center justify-between px-6 py-4 flex-shrink-0 select-none"
        >
          {/* Active Context Title (Un-boxed Floating Text) */}
          <div className="min-w-0">
            {activeTab === "explain" && (
              <>
                <h2
                  className="font-heading font-bold tracking-tight text-txtPrimary animate-fade-in text-sm"
                >
                  Architecture &amp; Memory Explainer
                </h2>
                <p
                  className="font-mono text-txtMuted mt-0.5 animate-fade-in text-[9.5px]"
                >
                  Design trade-offs <span className="text-[var(--accent-hover)]">•</span> Implementation details <span className="text-[var(--accent-hover)]">•</span> Interview prep
                </p>
              </>
            )}
            {activeTab === "diagrams" && (
              <>
                <h2
                  className="font-heading font-bold tracking-tight text-txtPrimary animate-fade-in text-sm"
                >
                  Architectural Diagram Canvas
                </h2>
                <p
                  className="font-mono text-txtMuted mt-0.5 animate-fade-in text-[9.5px]"
                >
                  Mermaid.js vector graphs parsed from database definitions
                </p>
              </>
            )}
            {activeTab === "settings" && (
              <>
                <h2
                  className="font-heading font-bold tracking-tight text-txtPrimary animate-fade-in text-sm"
                >
                  System Configurations
                </h2>
                <p
                  className="font-mono text-txtMuted mt-0.5 animate-fade-in text-[9.5px]"
                >
                  Configure AI models and workspace settings
                </p>
              </>
            )}
          </div>

          {/* Glowing Navigation Tab Segment Control */}
          <div className="flex items-center gap-1.5 bg-black/40 p-1.5 rounded-2xl border border-white/5 flex-shrink-0 shadow-lg">
            {TABS.map((tab) => {
              const isActive = activeTab === tab.id;
              const isDisabled = !projectId && tab.id !== "settings";
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  disabled={isDisabled}
                  className={`flex items-center gap-2 px-4 py-2 rounded-2xl font-heading font-semibold text-xs transition-all cursor-pointer ${
                    isActive
                      ? "bg-[#14241e] text-white border border-[#2d6a5a] shadow-[0_0_18px_rgba(45,106,90,0.4)]"
                      : "text-txtMuted hover:text-white border border-transparent"
                  }`}
                  style={{
                    opacity: isDisabled ? 0.38 : 1,
                    cursor: isDisabled ? "not-allowed" : "pointer",
                  }}
                >
                  <span
                    style={{ color: isActive ? "var(--sage)" : "inherit" }}
                  >
                    {tab.icon}
                  </span>
                  {tab.label}
                </button>
              );
            })}
          </div>
        </header>

        {/* Active Content Viewport */}
        <section className="flex-1 overflow-hidden relative border-t border-[rgba(77,124,115,0.12)]">
          {activeTab === "explain" && <ChatWindow projectId={projectId} />}
          {activeTab === "diagrams" && (
            <DiagramViewer
              projectId={projectId}
              onOpenSettings={() => setActiveTab("settings")}
            />
          )}
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
