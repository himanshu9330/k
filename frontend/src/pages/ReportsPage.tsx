import React, { useEffect, useState } from 'react';
import {
  FileText,
  Printer,
  Download,
  ShieldAlert,
  Layers,
  Sparkles,
  Building2,
  Calendar,
  Lock,
  RefreshCw,
} from 'lucide-react';
import { api } from '../services/api';
import { Incident } from '../types';
import { useToast } from '../components/Toast';

interface ReportsPageProps {
  onNavigate: (path: string) => void;
}

export const ReportsPage: React.FC<ReportsPageProps> = ({ onNavigate }) => {
  const { showToast } = useToast();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncCode, setSelectedIncCode] = useState<string>('');
  const [reportType, setReportType] = useState<string>('EXECUTIVE_BRIEFING');
  const [reportData, setReportData] = useState<any | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    const loadIncidents = async () => {
      try {
        const data = await api.getIncidents({ page_size: 50 });
        setIncidents(data);
        if (data.length > 0) {
          setSelectedIncCode(data[0].incident_id);
          fetchReport(data[0].incident_id);
        }
      } catch (err) {
        console.error('Failed to load incidents for report generator:', err);
      }
    };
    loadIncidents();
  }, []);

  const fetchReport = async (code: string) => {
    setIsGenerating(true);
    try {
      const data = await api.getIncidentBriefing(code);
      setReportData(data);
    } catch (err: any) {
      showToast('error', 'Report Generation Failed', err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleIncidentSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const code = e.target.value;
    setSelectedIncCode(code);
    fetchReport(code);
  };

  const handlePrint = () => {
    window.print();
  };

  const handleDownloadJSON = () => {
    if (!reportData) return;
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${reportData.report_id || 'incident_report'}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('success', 'Report Exported', 'JSON briefing downloaded.');
  };

  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-16">
      {/* Top Generator Controls (Hidden in Print) */}
      <div className="cream-card p-6 no-print">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-[26px] font-black text-espresso-900 tracking-tight">
              CISO Executive Briefing & Incident Reports
            </h1>
            <p className="text-[14px] text-charcoal-muted mt-0.5">
              Generate structured, audit-compliant reports for executive leadership and compliance auditors.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handlePrint}
              disabled={!reportData || isGenerating}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-espresso-900 hover:bg-espresso-800 text-cream-100 font-bold text-[14px] shadow-sm disabled:opacity-50 transition-all"
            >
              <Printer className="w-4 h-4 text-caramel" />
              <span>Print / Save PDF</span>
            </button>
            <button
              onClick={handleDownloadJSON}
              disabled={!reportData || isGenerating}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-cream-200 hover:bg-cream-300 text-espresso-900 font-bold text-[14px] border border-cream-300 disabled:opacity-50 transition-all"
            >
              <Download className="w-4 h-4 text-caramel" />
              <span>JSON Export</span>
            </button>
          </div>
        </div>

        {/* Selection Dropdown */}
        <div className="mt-5 pt-4 border-t border-cream-200 flex flex-col sm:flex-row items-start sm:items-center gap-4">
          <label className="text-[13.5px] font-extrabold text-espresso-900 uppercase tracking-wider shrink-0">
            Select Incident:
          </label>
          <select
            value={selectedIncCode}
            onChange={handleIncidentSelect}
            className="flex-1 px-4 py-2.5 rounded-xl border border-cream-300 bg-cream-100 text-espresso-900 font-bold text-[14.5px] focus:outline-none focus:border-caramel"
          >
            {incidents.map((inc) => (
              <option key={inc.id} value={inc.incident_id}>
                {inc.incident_id} — {inc.title} ({inc.severity} / {inc.risk_score} pts)
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Formal Document Render Container */}
      {isGenerating ? (
        <div className="cream-card p-16 text-center space-y-3">
          <div className="w-10 h-10 rounded-full border-4 border-espresso-800 border-t-caramel animate-spin mx-auto" />
          <h3 className="font-extrabold text-[18px] text-espresso-900">
            Generating Formal Security Briefing...
          </h3>
        </div>
      ) : reportData ? (
        <div className="cream-card p-10 bg-white border border-cream-300 shadow-elevated space-y-8 print:p-0 print:border-none print:shadow-none">
          {/* Document Letterhead */}
          <div className="border-b-2 border-espresso-900 pb-6 flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2 text-espresso-900 font-black text-[22px] tracking-tight">
                <span>SENTINELAI-X</span>
                <span className="text-caramel">|</span>
                <span className="text-[16px] font-bold text-charcoal-muted uppercase">SOC Executive Briefing</span>
              </div>
              <p className="text-[13px] text-charcoal-muted mt-1 font-mono">
                AUTONOMOUS THREAT INVESTIGATION PLATFORM
              </p>
            </div>

            <div className="text-right">
              <span className="px-3 py-1 rounded bg-espresso-900 text-cream-100 font-mono text-[12px] font-bold tracking-wider uppercase">
                {reportData.classification || 'RESTRICTED / SOC INTERNAL'}
              </span>
              <p className="text-[12.5px] font-mono text-charcoal-muted mt-1">
                Ref: {reportData.report_id}
              </p>
            </div>
          </div>

          {/* Report Title */}
          <div>
            <h2 className="text-[26px] font-black text-espresso-900 leading-tight">
              {reportData.title}
            </h2>
            <div className="mt-2 flex flex-wrap items-center gap-4 text-[13.5px] text-charcoal-muted">
              <span>Date: <strong>{new Date(reportData.generated_at).toUTCString()}</strong></span>
              <span>Classification: <strong>{reportData.incident_metadata?.severity} Severity</strong></span>
              <span>Risk Score: <strong>{reportData.incident_metadata?.risk_score}/100 ({reportData.incident_metadata?.risk_level})</strong></span>
              <span>Status: <strong>{reportData.incident_metadata?.status}</strong></span>
            </div>
          </div>

          {/* 1. Executive Summary */}
          <div className="space-y-2">
            <h3 className="text-[16px] font-extrabold text-espresso-900 uppercase tracking-wider border-b border-cream-200 pb-1">
              1. Executive Summary
            </h3>
            <p className="text-[15.5px] text-charcoal leading-relaxed">
              {reportData.executive_summary}
            </p>
          </div>

          {/* 2. Adversary Profile & Telemetry */}
          <div className="space-y-3">
            <h3 className="text-[16px] font-extrabold text-espresso-900 uppercase tracking-wider border-b border-cream-200 pb-1">
              2. Adversary Profile & Telemetry
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-[14px]">
              <div className="p-3 bg-cream-100 rounded-lg border border-cream-200">
                <span className="text-[12px] text-charcoal-muted block font-semibold uppercase">Origin IP</span>
                <strong className="font-mono text-espresso-900">{reportData.incident_metadata?.source_ip || 'Unresolved'}</strong>
              </div>
              <div className="p-3 bg-cream-100 rounded-lg border border-cream-200">
                <span className="text-[12px] text-charcoal-muted block font-semibold uppercase">Target Service</span>
                <strong className="text-espresso-900">{reportData.incident_metadata?.target_service?.toUpperCase() || 'General'}</strong>
              </div>
              <div className="p-3 bg-cream-100 rounded-lg border border-cream-200">
                <span className="text-[12px] text-charcoal-muted block font-semibold uppercase">Failed Volume</span>
                <strong className="text-soc-danger">{reportData.incident_metadata?.failed_attempts} attempts</strong>
              </div>
              <div className="p-3 bg-cream-100 rounded-lg border border-cream-200">
                <span className="text-[12px] text-charcoal-muted block font-semibold uppercase">Lifecycle Stage</span>
                <strong className="text-espresso-900">{reportData.incident_metadata?.status}</strong>
              </div>
            </div>
          </div>

          {/* 3. MITRE ATT&CK Defensive Mapping */}
          {reportData.mitre_attack && (
            <div className="space-y-2">
              <h3 className="text-[16px] font-extrabold text-espresso-900 uppercase tracking-wider border-b border-cream-200 pb-1">
                3. MITRE ATT&CK Threat Mapping
              </h3>
              <div className="p-4 bg-cream-100 rounded-lg border border-cream-200 space-y-1.5 text-[14.5px]">
                <p>
                  <strong>Technique: </strong>
                  <span className="font-mono font-bold text-caramel">{reportData.mitre_attack.technique_id}</span> — {reportData.mitre_attack.name} ({reportData.mitre_attack.tactic})
                </p>
                <p>
                  <strong>Mitigation Strategy: </strong>
                  {reportData.mitre_attack.mitigation}
                </p>
              </div>
            </div>
          )}

          {/* 4. Response Actions Status */}
          {reportData.recommended_response_actions && reportData.recommended_response_actions.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-[16px] font-extrabold text-espresso-900 uppercase tracking-wider border-b border-cream-200 pb-1">
                4. Containment & Playbook Actions
              </h3>
              <div className="space-y-2">
                {reportData.recommended_response_actions.map((act: any, idx: number) => (
                  <div key={idx} className="p-3 bg-cream-100 rounded-lg border border-cream-200 flex items-center justify-between text-[14px]">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded bg-espresso-900 text-cream-100 font-mono text-[11.5px] font-bold">
                        {act.priority || 'P1'}
                      </span>
                      <span className="font-bold text-espresso-900">{act.action}</span>
                    </div>
                    <span className="px-2.5 py-0.5 rounded text-[12px] font-bold uppercase bg-cream-200 text-espresso-900">
                      {act.status || 'PROPOSED'}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 5. Analyst Notes & Findings */}
          {reportData.analyst_notes && (
            <div className="space-y-2">
              <h3 className="text-[16px] font-extrabold text-espresso-900 uppercase tracking-wider border-b border-cream-200 pb-1">
                5. Analyst Remarks & Investigation Notes
              </h3>
              <div className="p-4 bg-cream-100 rounded-lg border border-cream-200 font-mono text-[13.5px] text-charcoal whitespace-pre-wrap leading-relaxed">
                {reportData.analyst_notes}
              </div>
            </div>
          )}

          {/* Signoff Footer */}
          <div className="mt-12 pt-6 border-t border-cream-300 flex items-center justify-between text-[13px] text-charcoal-muted">
            <div>
              <span>Generated By: <strong>SentinelAI-X Autonomous SOC</strong></span>
            </div>
            <div>
              <span>Security Analyst Sign-off: <strong>Sarah Connor, Lead Analyst</strong></span>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
};
