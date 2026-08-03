import { useState } from "react";
import { WorkspaceManager } from "./components/WorkspaceManager";
import { SearchPanel } from "./components/SearchPanel";
import { ChatWindow } from "./components/ChatWindow";
import { DiagramViewer } from "./components/DiagramViewer";
import { SettingsDrawer } from "./components/SettingsDrawer";
import { Layers, Settings, MessageSquare } from "lucide-react";

const TABS = [
  { id: "explain",  label: "Interview Mentor", icon: <MessageSquare size={14} /> },
  { id: "diagrams", label: "Diagram Canvas",   icon: <Layers size={14} /> },
  { id: "settings", label: "Settings",         icon: <Settings size={14} /> },
] as const;

type TabId = (typeof TABS)[number]["id"];

export default function App() {
  const [projectId,   setProjectId]   = useState<string | null>(null);
  const [projectPath, setProjectPath] = useState<string>("");
  const [stats,       setStats]       = useState<any>(null);
  const [isScanning,  setIsScanning]  = useState(false);
  const [activeTab,   setActiveTab]   = useState<TabId>("explain");

  return (
    <div className="flex h-screen w-screen overflow-hidden" style={{ background: 'var(--bg-app)', color: 'var(--txt-primary)' }}>

      {/* ── Sidebar ───────────────────────────────────────────── */}
      <aside
        className="flex flex-col h-screen overflow-y-auto flex-shrink-0"
        style={{
          width: 280,
          background: 'var(--bg-sidebar)',
          borderRight: '1px solid var(--border)',
        }}
      >
        {/* Logo Lockup */}
        <div
          className="flex items-center gap-3 px-5 py-5 select-none"
          style={{ borderBottom: '1px solid var(--border)' }}
        >
          {/* Console badge */}
          <div
            className="flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center"
            style={{
              background: 'linear-gradient(135deg, #4D7C73 0%, #98B6A7 100%)',
              boxShadow: '0 2px 8px rgba(77,124,115,0.3)',
            }}
          >
            <span
              className="font-mono font-black leading-none select-none"
              style={{ fontSize: 11, color: '#131816' }}
            >
              &gt;_
            </span>
          </div>

          <div className="min-w-0">
            <div
              className="font-heading font-extrabold uppercase tracking-widest leading-none"
              style={{
                fontSize: 13,
                background: 'linear-gradient(90deg, #98B6A7 0%, #4D7C73 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              ASTA
            </div>
            <div
              className="font-mono uppercase tracking-widest mt-0.5"
              style={{ fontSize: 8, color: 'var(--txt-disabled)' }}
            >
              Personal Eng Intel
            </div>
          </div>
        </div>

        {/* Sidebar Body */}
        <div className="flex flex-col gap-4 flex-1 px-4 py-4 overflow-y-auto min-h-0">
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
          <SearchPanel projectId={projectId} />
        </div>

        {/* Sidebar Footer */}
        <div
          className="px-4 py-3 flex items-center gap-2"
          style={{ borderTop: '1px solid var(--border)' }}
        >
          <div
            className="w-1.5 h-1.5 rounded-full animate-pulse-soft"
            style={{ background: 'var(--success)' }}
          />
          <span style={{ fontSize: 10, color: 'var(--txt-disabled)', fontFamily: 'JetBrains Mono, monospace' }}>
            ASTA v1.0 · Local Model
          </span>
        </div>
      </aside>

      {/* ── Main Area ─────────────────────────────────────────── */}
      <main className="flex flex-col flex-1 h-screen overflow-hidden" style={{ background: 'var(--bg-panel)' }}>

        {/* Tab Nav */}
        <nav
          className="flex items-center gap-1 px-5 py-3 flex-shrink-0"
          style={{ borderBottom: '1px solid var(--border)', background: 'var(--bg-sidebar)' }}
        >
          {TABS.map((tab) => {
            const isActive   = activeTab === tab.id;
            const isDisabled = !projectId && tab.id !== "settings";
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                disabled={isDisabled}
                className="flex items-center gap-2 px-3.5 py-2 rounded-lg font-heading font-semibold transition-all"
                style={{
                  fontSize: 12,
                  cursor: isDisabled ? 'not-allowed' : 'pointer',
                  opacity: isDisabled ? 0.38 : 1,
                  color:      isActive ? 'var(--sage)'    : 'var(--txt-muted)',
                  background: isActive ? 'rgba(77,124,115,0.12)' : 'transparent',
                  border:     isActive ? '1px solid rgba(77,124,115,0.22)' : '1px solid transparent',
                  transition: 'all 220ms ease',
                }}
                onMouseEnter={(e) => {
                  if (!isDisabled && !isActive) {
                    (e.currentTarget as HTMLButtonElement).style.color = 'var(--txt-second)';
                    (e.currentTarget as HTMLButtonElement).style.background = 'var(--bg-hover)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isDisabled && !isActive) {
                    (e.currentTarget as HTMLButtonElement).style.color = 'var(--txt-muted)';
                    (e.currentTarget as HTMLButtonElement).style.background = 'transparent';
                  }
                }}
              >
                <span style={{ color: isActive ? 'var(--accent)' : 'inherit' }}>{tab.icon}</span>
                {tab.label}
              </button>
            );
          })}
        </nav>

        {/* Active Content */}
        <section className="flex-1 overflow-hidden">
          {activeTab === "explain"  && <ChatWindow  projectId={projectId} />}
          {activeTab === "diagrams" && <DiagramViewer projectId={projectId} />}
          {activeTab === "settings" && <SettingsDrawer projectId={projectId} />}
        </section>
      </main>
    </div>
  );
}
