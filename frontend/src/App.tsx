import { useState } from "react";
import { WorkspaceManager } from "./components/WorkspaceManager";
import { SearchPanel } from "./components/SearchPanel";
import { ChatWindow } from "./components/ChatWindow";
import { DiagramViewer } from "./components/DiagramViewer";
import { SettingsDrawer } from "./components/SettingsDrawer";
import { Terminal, Layers, Settings, MessageSquare } from "lucide-react";

export default function App() {
  const [projectId, setProjectId] = useState<string | null>(null);
  const [projectPath, setProjectPath] = useState<string>("");
  const [stats, setStats] = useState<any>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [activeTab, setActiveTab] = useState<
    "explain" | "diagrams" | "settings"
  >("explain");

  return (
    <div className="grid grid-cols-[320px_1fr] h-screen w-screen bg-bgMain text-gray-100 overflow-hidden font-sans">
      {/* Sidebar Control Room */}
      <aside className="bg-bgSidebar border-r border-white/10 p-5 flex flex-col gap-4 overflow-y-auto h-screen box-border">
        <div className="flex items-center gap-2 mb-2">
          <Terminal size={24} className="text-accentPurple" />
          <div>
            <h1 className="text-lg font-black bg-gradient-to-r from-accentPurple to-accentCyan bg-clip-text text-transparent font-outfit uppercase tracking-tight">
              ASTA
            </h1>
            <span className="text-[9px] text-gray-500 font-mono tracking-widest block">
              PERSONAL ENG INTEL
            </span>
          </div>
        </div>

        {/* Workspace crawler configuration */}
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

        {/* Workspace keyword lookup prefix panel */}
        <SearchPanel projectId={projectId} />
      </aside>

      {/* Main Dialog Screen */}
      <main className="flex flex-col h-screen overflow-hidden">
        {/* Navigation Tabs bar */}
        <nav className="flex border-b border-white/10 bg-black/20 px-5 py-3 gap-3 items-center">
          {[
            {
              id: "explain",
              label: "Technical Interview Mentor",
              icon: <MessageSquare size={16} />,
            },
            {
              id: "diagrams",
              label: "Diagram Canvas",
              icon: <Layers size={16} />,
            },
            {
              id: "settings",
              label: "System Settings",
              icon: <Settings size={16} />,
            },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              disabled={!projectId && tab.id !== "settings"}
              className={`flex items-center gap-2 px-4 py-2 rounded-md border font-semibold font-outfit text-xs transition-all cursor-pointer ${
                activeTab === tab.id
                  ? "border-accentPurple/40 bg-accentPurple/10 text-accentPurple"
                  : "border-transparent text-gray-400 hover:text-white"
              }`}
              style={{
                opacity: !projectId && tab.id !== "settings" ? 0.4 : 1,
              }}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </nav>

        {/* Active tab content container */}
        <section className="flex-1 overflow-hidden bg-black/5">
          {activeTab === "explain" && <ChatWindow projectId={projectId} />}
          {activeTab === "diagrams" && <DiagramViewer projectId={projectId} />}
          {activeTab === "settings" && <SettingsDrawer projectId={projectId} />}
        </section>
      </main>
    </div>
  );
}
