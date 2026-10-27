import React, { useState, useRef } from 'react';
import {
  FileUp,
  FileText,
  Play,
  Sparkles,
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Cpu,
  Layers,
  Terminal,
} from 'lucide-react';
import { api } from '../services/api';
import { SeverityBadge } from '../components/SeverityBadge';
import { useToast } from '../components/Toast';

interface UploadPageProps {
  onNavigate: (path: string) => void;
}

const PRESET_SCENARIOS = [
  {
    id: 'ssh-brute-force',
    title: 'SSH Velocity Brute Force',
    description: 'High-speed automated authentication failure sequence against root & admin.',
    filename: 'auth_ssh_attack.log',
    content: `Aug 29 19:45:10 server sshd[12450]: Failed password for admin from 192.168.1.15 port 49152 ssh2
Aug 29 19:45:14 server sshd[12452]: Failed password for admin from 192.168.1.15 port 49154 ssh2
Aug 29 19:45:18 server sshd[12455]: Failed password for root from 192.168.1.15 port 49156 ssh2
Aug 29 19:45:22 server sshd[12458]: Failed password for root from 192.168.1.15 port 49158 ssh2
Aug 29 19:45:26 server sshd[12460]: Failed password for root from 192.168.1.15 port 49160 ssh2`,
  },
  {
    id: 'password-spray',
    title: 'Horizontal Password Spraying',
    description: 'Single origin attempting credentials across 5 distinct corporate accounts.',
    filename: 'ad_identity_spray.log',
    content: `2026-08-29T14:10:05Z,auth_failure,203.0.113.88,10.0.0.1,jsmith,kerberos,88,failed,Single credential attempt
2026-08-29T14:10:15Z,auth_failure,203.0.113.88,10.0.0.1,bwayne,kerberos,88,failed,Single credential attempt
2026-08-29T14:10:25Z,auth_failure,203.0.113.88,10.0.0.1,ckent,kerberos,88,failed,Single credential attempt
2026-08-29T14:10:35Z,auth_failure,203.0.113.88,10.0.0.1,dprince,kerberos,88,failed,Single credential attempt
2026-08-29T14:10:45Z,auth_failure,203.0.113.88,10.0.0.1,bbanner,kerberos,88,failed,Single credential attempt`,
  },
  {
    id: 'sudo-privesc',
    title: 'Sudo Privilege Escalation',
    description: 'Service user executing unauthorized sudo commands on /etc/shadow.',
    filename: 'auditd_privesc.log',
    content: `type=SYSCALL arch=c000003e syscall=59 success=yes pid=4120 uid=1001 auid=1001 comm="cat" exe="/bin/cat"
Aug 29 16:30:12 app-prod-02 sudo[4119]: user_test : TTY=pts/1 ; PWD=/home/user_test ; USER=root ; COMMAND=/bin/cat /etc/shadow
Aug 29 16:30:15 app-prod-02 sudo[4125]: user_test : TTY=pts/1 ; PWD=/home/user_test ; USER=root ; COMMAND=/usr/bin/chmod 777 /etc/passwd`,
  },
  {
    id: 'web-sqli',
    title: 'Web SQL Injection & Traversal',
    description: 'Inbound HTTP requests with SQL Union and path traversal payloads.',
    filename: 'nginx_access_sqli.log',
    content: `198.51.100.44 - - [29/Aug/2026:18:20:10 +0000] "GET /vulnerabilities/sqli/?id=1%27%20UNION%20SELECT%20null,username,password%20FROM%20users-- HTTP/1.1" 500 1420 "Mozilla/5.0"
198.51.100.44 - - [29/Aug/2026:18:20:14 +0000] "GET /download.php?file=../../../../etc/passwd HTTP/1.1" 403 280 "Mozilla/5.0"
198.51.100.44 - - [29/Aug/2026:18:20:18 +0000] "GET /admin/db_backup.sql HTTP/1.1" 404 150 "Mozilla/5.0"`,
  },
];

export const UploadPage: React.FC<UploadPageProps> = ({ onNavigate }) => {
  const { showToast } = useToast();
  const [activeTab, setActiveTab] = useState<'preset' | 'upload' | 'paste'>('preset');
  const [selectedScenario, setSelectedScenario] = useState(PRESET_SCENARIOS[0]);
  const [pasteContent, setPasteContent] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleRunPreset = async (scenario: typeof PRESET_SCENARIOS[0]) => {
    setSelectedScenario(scenario);
    setIsProcessing(true);
    setAnalysisResult(null);

    try {
      const blob = new Blob([scenario.content], { type: 'text/plain' });
      const file = new File([blob], scenario.filename, { type: 'text/plain' });
      const result = await api.uploadLog(file);
      setAnalysisResult(result);
      showToast('success', 'Analysis Complete', `Incident ${result.incident_id} created successfully.`);
    } catch (err: any) {
      showToast('error', 'Ingestion Failed', err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCustomUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    let fileToUpload: File | null = selectedFile;

    if (activeTab === 'paste') {
      if (!pasteContent.trim()) {
        showToast('warning', 'Empty Log', 'Please paste security log text.');
        return;
      }
      const blob = new Blob([pasteContent], { type: 'text/plain' });
      fileToUpload = new File([blob], 'manual_pasted_log.log', { type: 'text/plain' });
    }

    if (!fileToUpload) {
      showToast('warning', 'No File Selected', 'Please select a log file.');
      return;
    }

    setIsProcessing(true);
    setAnalysisResult(null);
    try {
      const result = await api.uploadLog(fileToUpload);
      setAnalysisResult(result);
      showToast('success', 'Analysis Complete', `Incident ${result.incident_id} created successfully.`);
    } catch (err: any) {
      showToast('error', 'Ingestion Failed', err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-16">
      {/* Header */}
      <div>
        <h1 className="text-[28px] md:text-[32px] font-black text-espresso-900 tracking-tight">
          Security Log Ingestion & Threat Analyzer
        </h1>
        <p className="text-[15px] text-charcoal-muted mt-1">
          Ingest raw syslog, auth logs, JSON, or CSV event streams for autonomous Gemini reasoning and instant incident generation.
        </p>
      </div>

      {/* Mode Selection Tabs */}
      <div className="flex items-center gap-2 border-b border-cream-300">
        <button
          onClick={() => setActiveTab('preset')}
          className={`px-5 py-3 font-extrabold text-[15px] border-b-2 transition-all ${
            activeTab === 'preset'
              ? 'border-caramel text-espresso-900'
              : 'border-transparent text-charcoal-muted hover:text-espresso-900'
          }`}
        >
          ⚡ 1-Click Threat Scenarios
        </button>
        <button
          onClick={() => setActiveTab('upload')}
          className={`px-5 py-3 font-extrabold text-[15px] border-b-2 transition-all ${
            activeTab === 'upload'
              ? 'border-caramel text-espresso-900'
              : 'border-transparent text-charcoal-muted hover:text-espresso-900'
          }`}
        >
          📁 Upload Log File
        </button>
        <button
          onClick={() => setActiveTab('paste')}
          className={`px-5 py-3 font-extrabold text-[15px] border-b-2 transition-all ${
            activeTab === 'paste'
              ? 'border-caramel text-espresso-900'
              : 'border-transparent text-charcoal-muted hover:text-espresso-900'
          }`}
        >
          📝 Paste Raw Log Text
        </button>
      </div>

      {/* Preset Scenarios Tab */}
      {activeTab === 'preset' && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {PRESET_SCENARIOS.map((sc) => (
            <div
              key={sc.id}
              className={`cream-card p-5 flex flex-col justify-between transition-all hover:shadow-elevated ${
                selectedScenario.id === sc.id ? 'border-caramel bg-cream-50 ring-2 ring-caramel/20' : ''
              }`}
            >
              <div>
                <h3 className="text-[17px] font-extrabold text-espresso-900">
                  {sc.title}
                </h3>
                <p className="text-[13px] text-charcoal-muted mt-1.5 leading-relaxed">
                  {sc.description}
                </p>
                <div className="mt-3 py-1 px-2.5 rounded bg-cream-200 text-espresso-900 font-mono text-[12px] font-bold inline-block">
                  {sc.filename}
                </div>
              </div>

              <button
                onClick={() => handleRunPreset(sc)}
                disabled={isProcessing}
                className="mt-5 w-full py-2.5 rounded-xl bg-espresso-900 hover:bg-espresso-800 text-cream-100 font-bold text-[14px] shadow-sm flex items-center justify-center gap-2 transition-all disabled:opacity-50"
              >
                <Play className="w-4 h-4 text-caramel fill-caramel" />
                <span>Simulate & Ingest</span>
              </button>
            </div>
          ))}
        </div>
      )}

      {/* File Upload Tab */}
      {activeTab === 'upload' && (
        <form onSubmit={handleCustomUpload} className="cream-card p-8 text-center space-y-4">
          <input
            ref={fileInputRef}
            type="file"
            accept=".log,.txt,.json,.csv"
            onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
            className="hidden"
          />

          <div
            onClick={() => fileInputRef.current?.click()}
            className="p-10 border-2 border-dashed border-cream-300 hover:border-caramel rounded-2xl cursor-pointer bg-cream-100 transition-colors flex flex-col items-center justify-center gap-3"
          >
            <div className="w-14 h-14 rounded-2xl bg-espresso-900 text-caramel flex items-center justify-center">
              <FileUp className="w-7 h-7" />
            </div>
            <div>
              <p className="font-extrabold text-[16px] text-espresso-900">
                {selectedFile ? selectedFile.name : 'Click or Drag & Drop Security Log File'}
              </p>
              <p className="text-[13px] text-charcoal-muted mt-0.5">
                Supported formats: Syslog (.log), JSON (.json), CSV (.csv), Plain Text (.txt)
              </p>
            </div>
          </div>

          <button
            type="submit"
            disabled={!selectedFile || isProcessing}
            className="px-8 py-3 rounded-xl bg-espresso-900 hover:bg-espresso-800 text-cream-100 font-extrabold text-[15px] shadow-sm disabled:opacity-50 transition-all"
          >
            {isProcessing ? 'Processing Telemetry...' : 'Upload & Analyze Log Stream'}
          </button>
        </form>
      )}

      {/* Paste Text Tab */}
      {activeTab === 'paste' && (
        <form onSubmit={handleCustomUpload} className="cream-card p-6 space-y-4">
          <textarea
            rows={8}
            placeholder="Paste raw syslog, auth log, or firewall records here..."
            value={pasteContent}
            onChange={(e) => setPasteContent(e.target.value)}
            className="w-full p-4 rounded-xl border border-cream-300 bg-cream-100 text-espresso-900 font-mono text-[13.5px] focus:outline-none focus:border-caramel resize-none leading-relaxed"
          />

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={!pasteContent.trim() || isProcessing}
              className="px-8 py-3 rounded-xl bg-espresso-900 hover:bg-espresso-800 text-cream-100 font-extrabold text-[15px] shadow-sm disabled:opacity-50 transition-all"
            >
              {isProcessing ? 'Analyzing Payload...' : 'Analyze Pasted Stream'}
            </button>
          </div>
        </form>
      )}

      {/* Processing Indicator */}
      {isProcessing && (
        <div className="cream-card p-8 text-center space-y-3">
          <div className="w-10 h-10 rounded-full border-4 border-espresso-800 border-t-caramel animate-spin mx-auto" />
          <h3 className="font-extrabold text-[18px] text-espresso-900">
            Orchestrating Autonomous SOC Pipeline
          </h3>
          <p className="text-[14px] text-charcoal-muted max-w-md mx-auto">
            1. Parsing logs → 2. Normalizing events → 3. Rule Detection → 4. Gemini AI Reasoning → 5. Risk Scoring → 6. MITRE Mapping.
          </p>
        </div>
      )}

      {/* Live Pipeline Analysis Results */}
      {analysisResult && (
        <div className="cream-card p-6 border-l-6 border-l-soc-success space-y-6 animate-in fade-in zoom-in-95">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-cream-200 pb-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <CheckCircle2 className="w-5 h-5 text-soc-success" />
                <span className="font-extrabold text-[14px] text-soc-success uppercase tracking-wider">
                  Incident Ingested & Persisted
                </span>
              </div>
              <h2 className="text-[24px] font-black text-espresso-900">
                {analysisResult.ai_analysis?.incident_type || 'Security Incident'} ({analysisResult.incident_id})
              </h2>
            </div>

            <button
              onClick={() => onNavigate(`/incidents/${analysisResult.incident_id}`)}
              className="px-6 py-3 rounded-xl bg-caramel hover:bg-caramel-hover text-white font-black text-[15px] shadow-sm flex items-center justify-center gap-2 transition-all hover:scale-[1.02]"
            >
              <span>Deep-Dive Incident #{analysisResult.incident_id}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>

          {/* Quick Metrics Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-cream-100 p-4 rounded-xl border border-cream-200">
              <span className="text-[12px] font-bold text-charcoal-muted uppercase tracking-wider block">
                Deterministic Risk
              </span>
              <span className="text-[26px] font-black text-espresso-900">
                {analysisResult.risk_score} <span className="text-[13px] font-normal text-charcoal-muted">/100</span>
              </span>
              <span className="block text-[12px] font-bold text-caramel uppercase">
                {analysisResult.risk_level} Priority
              </span>
            </div>

            <div className="bg-cream-100 p-4 rounded-xl border border-cream-200">
              <span className="text-[12px] font-bold text-charcoal-muted uppercase tracking-wider block">
                Normalized Events
              </span>
              <span className="text-[26px] font-black text-espresso-900">
                {analysisResult.event_count}
              </span>
              <span className="block text-[12px] font-mono text-charcoal-muted">
                Format: {analysisResult.log_format}
              </span>
            </div>

            <div className="bg-cream-100 p-4 rounded-xl border border-cream-200">
              <span className="text-[12px] font-bold text-charcoal-muted uppercase tracking-wider block">
                MITRE Technique
              </span>
              <span className="text-[22px] font-black font-mono text-espresso-900">
                {analysisResult.mitre_technique?.technique_id || 'T1110'}
              </span>
              <span className="block text-[12px] font-semibold text-charcoal-muted truncate">
                {analysisResult.mitre_technique?.name || 'Brute Force'}
              </span>
            </div>

            <div className="bg-cream-100 p-4 rounded-xl border border-cream-200">
              <span className="text-[12px] font-bold text-charcoal-muted uppercase tracking-wider block">
                AI Engine State
              </span>
              <span className="text-[22px] font-black text-soc-success">
                {analysisResult.ai_status}
              </span>
              <span className="block text-[12px] text-charcoal-muted">
                Corroborated Analysis
              </span>
            </div>
          </div>

          {/* AI Explanation Snippet */}
          <div className="bg-cream-100 p-5 rounded-xl border border-cream-200 space-y-2">
            <h4 className="font-extrabold text-[15px] text-espresso-900 flex items-center gap-2">
              <Cpu className="w-4 h-4 text-caramel" />
              <span>AI Analytical Assessment</span>
            </h4>
            <p className="text-[14.5px] text-charcoal leading-relaxed whitespace-pre-wrap">
              {analysisResult.ai_analysis?.explanation || 'Threat patterns verified via multi-factor rule analysis.'}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
