import React, { useEffect, useState } from 'react';
import {
  ShieldCheck,
  Cpu,
  User,
  PlusCircle,
  Activity,
  CheckCircle2,
  AlertCircle
} from 'lucide-react';
import { api } from '../services/api';

interface NavbarProps {
  currentPath: string;
  onNavigate: (path: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentPath, onNavigate }) => {
  const [backendStatus, setBackendStatus] = useState<'healthy' | 'offline' | 'checking'>('checking');
  const [modelName, setModelName] = useState<string>('gemini-2.5-flash');

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await api.healthCheck();
        setBackendStatus('healthy');
        if (res.model) setModelName(res.model);
      } catch {
        setBackendStatus('offline');
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const getPageTitle = () => {
    if (currentPath === '/') return 'Security Operations Center Dashboard';
    if (currentPath === '/incidents') return 'Incident Triage & Analysis Queue';
    if (currentPath.startsWith('/incidents/')) return 'Incident Deep-Dive & Forensics';
    if (currentPath === '/copilot') return 'AI Autonomous SOC Copilot';
    if (currentPath === '/threat-intel') return 'Threat Intelligence & IOC Enrichment';
    if (currentPath === '/upload') return 'Security Log Parser & Threat Analyzer';
    if (currentPath === '/reports') return 'Executive CISO Briefings & Reports';
    if (currentPath === '/mitre') return 'MITRE ATT&CK Enterprise Matrix';
    if (currentPath === '/audit') return 'Forensic Audit & Compliance Trail';
    if (currentPath === '/settings') return 'System Architecture & DevSecOps';
    return 'Security Operations Console';
  };

  return (
    <header className="h-20 bg-white/90 backdrop-blur-md border-b border-cream-300 px-8 flex items-center justify-between sticky top-0 z-10">
      {/* Page Title & Breadcrumb */}
      <div>
        <div className="flex items-center gap-2 text-[13px] font-semibold text-charcoal-muted uppercase tracking-wider">
          <span>SentinelAI-X</span>
          <span>/</span>
          <span className="text-caramel font-bold">Platform</span>
        </div>
        <h2 className="text-[22px] font-extrabold text-espresso-900 tracking-tight">
          {getPageTitle()}
        </h2>
      </div>

      {/* Right Controls & Indicators */}
      <div className="flex items-center gap-4">
        {/* Backend Heartbeat */}
        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cream-200 border border-cream-300 text-[13.5px] font-medium text-charcoal">
          {backendStatus === 'healthy' ? (
            <>
              <CheckCircle2 className="w-4 h-4 text-soc-success" />
              <span className="font-semibold text-espresso-900">API Online</span>
            </>
          ) : backendStatus === 'offline' ? (
            <>
              <AlertCircle className="w-4 h-4 text-soc-danger" />
              <span className="font-semibold text-soc-danger">API Offline</span>
            </>
          ) : (
            <>
              <Activity className="w-4 h-4 text-caramel animate-spin" />
              <span>Connecting...</span>
            </>
          )}
        </div>

        {/* Gemini Engine Indicator */}
        <div className="flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-caramel-light border border-caramel/30 text-[13.5px] text-espresso-900 font-semibold">
          <Cpu className="w-4 h-4 text-copper" />
          <span>Gemini AI</span>
          <span className="text-[11.5px] px-1.5 py-0.2 rounded bg-caramel text-white font-mono font-bold">
            Flash
          </span>
        </div>

        {/* Quick Ingest Button */}
        <button
          onClick={() => onNavigate('/upload')}
          className="flex items-center gap-2 px-4 py-2 rounded-xl bg-espresso-900 hover:bg-espresso-800 text-cream-100 font-bold text-[14.5px] shadow-sm transition-all hover:scale-[1.02] active:scale-[0.98]"
        >
          <PlusCircle className="w-4 h-4 text-caramel" />
          <span>Ingest Log</span>
        </button>

        {/* Analyst Profile Pill */}
        <div className="flex items-center gap-2.5 pl-3 border-l border-cream-300">
          <div className="w-9 h-9 rounded-full bg-espresso-800 text-caramel flex items-center justify-center font-bold text-[14px]">
            SC
          </div>
          <div className="text-left hidden lg:block">
            <p className="text-[14px] font-bold text-espresso-900 leading-tight">Sarah Connor</p>
            <p className="text-[12px] font-medium text-charcoal-muted">SOC Lead Analyst</p>
          </div>
        </div>
      </div>
    </header>
  );
};
