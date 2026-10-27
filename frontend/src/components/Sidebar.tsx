import React from 'react';
import {
  LayoutDashboard,
  ShieldAlert,
  Bot,
  Globe2,
  FileUp,
  FileText,
  Layers,
  ScrollText,
  Settings,
  Flame,
} from 'lucide-react';

interface SidebarProps {
  currentPath: string;
  onNavigate: (path: string) => void;
  openIncidentsCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentPath,
  onNavigate,
  openIncidentsCount = 0,
}) => {
  const navItems = [
    {
      id: 'dashboard',
      label: 'SOC Dashboard',
      path: '/',
      icon: LayoutDashboard,
    },
    {
      id: 'incidents',
      label: 'Incidents & Triage',
      path: '/incidents',
      icon: ShieldAlert,
      badge: openIncidentsCount > 0 ? openIncidentsCount : undefined,
    },
    {
      id: 'copilot',
      label: 'AI Investigation Copilot',
      path: '/copilot',
      icon: Bot,
      highlight: true,
    },
    {
      id: 'threat-intel',
      label: 'Threat Intelligence',
      path: '/threat-intel',
      icon: Globe2,
    },
    {
      id: 'upload',
      label: 'Log Analyzer & Ingestion',
      path: '/upload',
      icon: FileUp,
    },
    {
      id: 'reports',
      label: 'Executive Reports',
      path: '/reports',
      icon: FileText,
    },
    {
      id: 'mitre',
      label: 'MITRE ATT&CK Matrix',
      path: '/mitre',
      icon: Layers,
    },
    {
      id: 'audit',
      label: 'Forensic Audit Logs',
      path: '/audit',
      icon: ScrollText,
    },
    {
      id: 'settings',
      label: 'System & Architecture',
      path: '/settings',
      icon: Settings,
    },
  ];

  return (
    <aside className="w-72 bg-espresso-900 border-r border-espresso-700 flex flex-col shrink-0 min-h-screen text-[#EFE6D8] z-20">
      {/* Brand Header */}
      <div className="p-6 border-b border-espresso-700/80 flex items-center gap-3.5">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-caramel to-copper flex items-center justify-center shadow-espresso text-white font-black text-xl">
          <Flame className="w-6 h-6 text-cream-100 fill-cream-100" />
        </div>
        <div>
          <h1 className="font-extrabold text-[20px] text-cream-100 tracking-tight leading-tight">
            SentinelAI<span className="text-caramel font-black">-X</span>
          </h1>
          <p className="text-[12.5px] font-medium text-cream-400/80 tracking-wide uppercase">
            Autonomous SOC Engine
          </p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-5 space-y-1.5 overflow-y-auto">
        <div className="px-3 pb-2 text-[11.5px] font-bold tracking-wider text-cream-500 uppercase">
          Operations & Intelligence
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPath === item.path || (item.path !== '/' && currentPath.startsWith(item.path));

          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.path)}
              className={`w-full flex items-center gap-3.5 px-3.5 py-3 rounded-xl font-semibold text-[15px] transition-all duration-150 text-left relative ${
                isActive
                  ? 'bg-espresso-800 text-cream-100 shadow-sm border border-caramel/40'
                  : 'text-cream-300 hover:bg-espresso-800/60 hover:text-cream-100'
              }`}
            >
              {/* Active Left Pill */}
              {isActive && (
                <div className="absolute left-0 top-2 bottom-2 w-1.5 bg-caramel rounded-r-full" />
              )}
              
              <Icon
                className={`w-5 h-5 shrink-0 ${
                  isActive ? 'text-caramel' : 'text-cream-400'
                } ${item.highlight ? 'animate-pulse text-caramel' : ''}`}
              />

              <span className="flex-1 truncate">{item.label}</span>

              {item.badge !== undefined && (
                <span className="px-2 py-0.5 text-[12px] font-bold rounded-full bg-soc-danger text-white shrink-0">
                  {item.badge}
                </span>
              )}

              {item.highlight && !isActive && (
                <span className="px-1.5 py-0.5 text-[11px] font-bold rounded bg-caramel/20 text-caramel border border-caramel/30 shrink-0 uppercase">
                  AI
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Footer System Status */}
      <div className="p-4 m-3 rounded-xl bg-espresso-800 border border-espresso-700">
        <div className="flex items-center justify-between text-[13px] font-semibold text-cream-300">
          <span className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-soc-success animate-ping" />
            <span className="text-cream-100">SOC Online</span>
          </span>
          <span className="text-cream-400 font-mono text-[12px]">v1.0.0</span>
        </div>
        <div className="mt-2 text-[12.5px] text-cream-400">
          Engine: <span className="font-semibold text-caramel">Gemini 3.6 + Rule</span>
        </div>
      </div>
    </aside>
  );
};
