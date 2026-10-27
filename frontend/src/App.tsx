import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Sidebar';
import { Navbar } from './components/Navbar';
import { ToastProvider } from './components/Toast';

import { DashboardPage } from './pages/DashboardPage';
import { IncidentsPage } from './pages/IncidentsPage';
import { IncidentDetailPage } from './pages/IncidentDetailPage';
import { CopilotPage } from './pages/CopilotPage';
import { ThreatIntelPage } from './pages/ThreatIntelPage';
import { UploadPage } from './pages/UploadPage';
import { ReportsPage } from './pages/ReportsPage';
import { MitrePage } from './pages/MitrePage';
import { AuditPage } from './pages/AuditPage';
import { SettingsPage } from './pages/SettingsPage';

export function App() {
  const [currentPath, setCurrentPath] = useState<string>('/');

  const handleNavigate = (path: string) => {
    setCurrentPath(path);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const renderContent = () => {
    if (currentPath === '/') {
      return <DashboardPage onNavigate={handleNavigate} />;
    }
    if (currentPath === '/incidents') {
      return <IncidentsPage onNavigate={handleNavigate} />;
    }
    if (currentPath.startsWith('/incidents/')) {
      const incidentId = currentPath.replace('/incidents/', '');
      return <IncidentDetailPage incidentId={incidentId} onNavigate={handleNavigate} />;
    }
    if (currentPath === '/copilot') {
      return <CopilotPage onNavigate={handleNavigate} />;
    }
    if (currentPath === '/threat-intel') {
      return <ThreatIntelPage />;
    }
    if (currentPath === '/upload') {
      return <UploadPage onNavigate={handleNavigate} />;
    }
    if (currentPath === '/reports') {
      return <ReportsPage onNavigate={handleNavigate} />;
    }
    if (currentPath === '/mitre') {
      return <MitrePage />;
    }
    if (currentPath === '/audit') {
      return <AuditPage />;
    }
    if (currentPath === '/settings') {
      return <SettingsPage />;
    }
    return <DashboardPage onNavigate={handleNavigate} />;
  };

  return (
    <ToastProvider>
      <div className="min-h-screen bg-cream text-charcoal flex font-sans selection:bg-caramel-light selection:text-espresso-950">
        {/* Deep Espresso Sidebar */}
        <Sidebar currentPath={currentPath} onNavigate={handleNavigate} />

        {/* Primary Workspace Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Top Navbar */}
          <Navbar currentPath={currentPath} onNavigate={handleNavigate} />

          {/* Main Body */}
          <main className="flex-1 p-6 md:p-8 overflow-y-auto">
            {renderContent()}
          </main>
        </div>
      </div>
    </ToastProvider>
  );
}

export default App;
