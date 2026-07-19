import { useState } from 'react';
import { WorkspaceManager } from './components/WorkspaceManager';
import { SearchPanel } from './components/SearchPanel';
import { ChatWindow } from './components/ChatWindow';
import { InterviewCoach } from './components/InterviewCoach';
import { DiagramViewer } from './components/DiagramViewer';
import { SettingsDrawer } from './components/SettingsDrawer';
import { Terminal, Award, Layers, Settings, MessageSquare } from 'lucide-react';

export default function App() {
  const [projectId, setProjectId] = useState<string | null>(null);
  const [projectPath, setProjectPath] = useState<string>('');
  const [stats, setStats] = useState<any>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [activeTab, setActiveTab] = useState<'explain' | 'interview' | 'diagrams' | 'settings'>('explain');

  return (
    <div className="app-container">
      {/* Sidebar Control Room */}
      <aside style={{
        background: 'var(--bg-sidebar)',
        borderRight: '1px solid var(--border-color)',
        padding: '20px',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        overflowY: 'auto',
        height: '100vh',
        boxSizing: 'border-box'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
          <Terminal size={24} style={{ color: 'var(--accent-purple)' }} />
          <div>
            <h1 style={{ fontSize: '18px', fontWeight: '800', background: 'var(--accent-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>PEIS</h1>
            <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>PERSONAL ENG INTEL</span>
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
      <main style={{ display: 'flex', flexDirection: 'column', height: '100vh', overflow: 'hidden' }}>
        {/* Navigation Tabs bar */}
        <nav style={{
          display: 'flex',
          borderBottom: '1px solid var(--border-color)',
          background: 'rgba(22, 22, 28, 0.4)',
          padding: '12px 20px',
          gap: '12px',
          alignItems: 'center'
        }}>
          {[
            { id: 'explain', label: 'Architecture Explainer', icon: <MessageSquare size={16} /> },
            { id: 'interview', label: 'Mock Interview Coach', icon: <Award size={16} /> },
            { id: 'diagrams', label: 'Diagram Canvas', icon: <Layers size={16} /> },
            { id: 'settings', label: 'System Settings', icon: <Settings size={16} /> }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              disabled={!projectId && tab.id !== 'settings'}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 16px',
                borderRadius: '6px',
                border: '1px solid',
                borderColor: activeTab === tab.id ? 'var(--border-color-active)' : 'transparent',
                background: activeTab === tab.id ? 'rgba(147, 51, 234, 0.1)' : 'transparent',
                color: activeTab === tab.id ? 'var(--accent-purple)' : 'var(--text-secondary)',
                fontFamily: 'Outfit, sans-serif',
                fontWeight: '600',
                fontSize: '13px',
                cursor: (!projectId && tab.id !== 'settings') ? 'not-allowed' : 'pointer',
                opacity: (!projectId && tab.id !== 'settings') ? 0.4 : 1,
                transition: 'all 0.2s ease-in-out'
              }}
            >
              {tab.icon}
              {tab.label}
            </button>
          ))}
        </nav>

        {/* Active tab content container */}
        <section style={{ flex: '1', overflow: 'hidden' }}>
          {activeTab === 'explain' && <ChatWindow projectId={projectId} />}
          {activeTab === 'interview' && <InterviewCoach projectId={projectId} />}
          {activeTab === 'diagrams' && <DiagramViewer projectId={projectId} />}
          {activeTab === 'settings' && <SettingsDrawer projectId={projectId} />}
        </section>
      </main>
    </div>
  );
}
