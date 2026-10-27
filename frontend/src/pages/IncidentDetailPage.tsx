import React, { useEffect, useState } from 'react';
import { IncidentDetail, ResponseAction } from '../types';
import { api } from '../services/api';
import { SeverityBadge } from '../components/SeverityBadge';
import { StatusBadge } from '../components/StatusBadge';
import { RiskScoreGauge } from '../components/RiskScoreGauge';
import { IncidentTimeline } from '../components/IncidentTimeline';
import { ThreatIndicatorCard } from '../components/ThreatIndicatorCard';
import { useToast } from '../components/Toast';
import {
  ArrowLeft,
  Bot,
  Terminal,
  CheckCircle2,
  FileText,
  ShieldCheck,
  Cpu,
  Layers,
  Save,
  Clock,
  Radio,
  ExternalLink,
  Copy,
} from 'lucide-react';

interface IncidentDetailPageProps {
  incidentId: string;
  onNavigate: (path: string) => void;
}

export const IncidentDetailPage: React.FC<IncidentDetailPageProps> = ({
  incidentId,
  onNavigate,
}) => {
  const { showToast } = useToast();
  const [incident, setIncident] = useState<IncidentDetail | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [analystNoteText, setAnalystNoteText] = useState('');
  const [isSavingNote, setIsSavingNote] = useState(false);
  const [statusUpdating, setStatusUpdating] = useState(false);

  const loadIncident = async () => {
    setIsLoading(true);
    try {
      const data = await api.getIncidentDetails(incidentId);
      setIncident(data);
    } catch (err: any) {
      showToast('error', 'Failed to load incident', err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadIncident();
  }, [incidentId]);

  const handleStatusChange = async (newStatus: string) => {
    setStatusUpdating(true);
    try {
      const updated = await api.updateIncidentStatus(incidentId, newStatus);
      showToast('success', 'Lifecycle Status Updated', `Status changed to ${newStatus}`);
      loadIncident();
    } catch (err: any) {
      showToast('error', 'Update Failed', err.message);
    } finally {
      setStatusUpdating(false);
    }
  };

  const handleActionApproval = async (actionId: number, status: 'APPROVED' | 'EXECUTED' | 'REJECTED') => {
    try {
      await api.updateActionStatus(incidentId, actionId, status);
      showToast('success', `Response Action ${status}`, 'Playbook response action updated.');
      loadIncident();
    } catch (err: any) {
      showToast('error', 'Action Update Failed', err.message);
    }
  };

  const handleAddNote = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!analystNoteText.trim()) return;

    setIsSavingNote(true);
    try {
      await api.addIncidentNote(incidentId, analystNoteText.trim());
      showToast('success', 'Analyst Note Saved', 'Milestone recorded in incident forensic log.');
      setAnalystNoteText('');
      loadIncident();
    } catch (err: any) {
      showToast('error', 'Failed to save note', err.message);
    } finally {
      setIsSavingNote(false);
    }
  };

  const copyToClipboard = (text: string, label: string) => {
    navigator.clipboard.writeText(text);
    showToast('info', 'Copied to Clipboard', label);
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <div className="w-12 h-12 rounded-full border-4 border-espresso-800 border-t-caramel animate-spin" />
        <p className="mt-4 font-bold text-[16px] text-espresso-900">
          Loading Deep-Dive Incident Forensics...
        </p>
      </div>
    );
  }

  if (!incident) {
    return (
      <div className="cream-card p-12 text-center space-y-4 max-w-xl mx-auto my-12">
        <h2 className="text-[22px] font-black text-espresso-900">Incident Not Found</h2>
        <p className="text-[15px] text-charcoal-muted">
          The requested incident ({incidentId}) could not be resolved in the database.
        </p>
        <button
          onClick={() => onNavigate('/incidents')}
          className="px-5 py-2.5 rounded-xl bg-espresso-900 text-cream-100 font-bold"
        >
          Return to Queue
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-16">
      {/* Top Breadcrumb & Quick Action Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <button
          onClick={() => onNavigate('/incidents')}
          className="flex items-center gap-2 text-charcoal-muted hover:text-espresso-900 font-bold text-[14.5px] transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Incident Queue</span>
        </button>

        <div className="flex flex-wrap items-center gap-3">
          {/* AI Copilot shortcut */}
          <button
            onClick={() => onNavigate('/copilot')}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-espresso-800 hover:bg-espresso-700 text-cream-100 font-bold text-[14px] border border-caramel/40 shadow-xs transition-colors"
          >
            <Bot className="w-4 h-4 text-caramel" />
            <span>Ask AI Copilot about this</span>
          </button>

          {/* Generate Report shortcut */}
          <button
            onClick={() => onNavigate('/reports')}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cream-200 hover:bg-cream-300 text-espresso-900 font-bold text-[14px] border border-cream-300 transition-colors"
          >
            <FileText className="w-4 h-4 text-caramel" />
            <span>Executive Briefing</span>
          </button>
        </div>
      </div>

      {/* Incident Hero Header Card */}
      <div className="cream-card p-6 border-l-6 border-l-caramel">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          <div className="space-y-2 flex-1">
            <div className="flex flex-wrap items-center gap-3">
              <span className="font-mono font-black text-[16px] text-espresso-900 bg-cream-200 px-3 py-1 rounded-lg border border-cream-300">
                {incident.incident_id}
              </span>
              <SeverityBadge severity={incident.severity} size="md" />
              <StatusBadge status={incident.status} size="md" />
              <span className="text-[13.5px] text-charcoal-muted font-medium">
                Detected {new Date(incident.created_at).toLocaleString()}
              </span>
            </div>

            <h1 className="text-[24px] md:text-[30px] font-black text-espresso-900 tracking-tight leading-snug">
              {incident.title}
            </h1>

            {incident.description && (
              <p className="text-[15.5px] text-charcoal leading-relaxed max-w-4xl">
                {incident.description}
              </p>
            )}
          </div>

          {/* Lifecycle Status Dropdown */}
          <div className="flex flex-col items-start lg:items-end gap-2 shrink-0">
            <label className="text-[12.5px] font-extrabold text-charcoal-muted uppercase tracking-wider">
              Incident Lifecycle Stage
            </label>
            <select
              value={incident.status}
              disabled={statusUpdating}
              onChange={(e) => handleStatusChange(e.target.value)}
              className="px-4 py-2.5 rounded-xl border border-cream-300 bg-white font-extrabold text-[15px] text-espresso-900 shadow-sm focus:outline-none focus:border-caramel"
            >
              <option value="OPEN">🔴 Open / Untriaged</option>
              <option value="INVESTIGATING">🔵 Under Investigation</option>
              <option value="CONTAINED">🟡 Contained / Isolated</option>
              <option value="RESOLVED">🟢 Remediated & Resolved</option>
              <option value="FALSE_POSITIVE">⚪ False Positive</option>
            </select>
          </div>
        </div>
      </div>

      {/* Main Grid: Left Investigation Cockpit (2 Cols) | Right Analytics (1 Col) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column (2 Cols) */}
        <div className="lg:col-span-2 space-y-8">
          {/* 1. Generative AI Investigation Analysis */}
          <div className="cream-card p-6 relative overflow-hidden">
            <div className="flex items-center justify-between border-b border-cream-200 pb-4 mb-4">
              <div className="flex items-center gap-2.5">
                <div className="w-9 h-9 rounded-xl bg-espresso-900 text-caramel flex items-center justify-center font-bold">
                  <Cpu className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-[18px] font-extrabold text-espresso-900">
                    Gemini AI Forensic Investigation
                  </h3>
                  <p className="text-[13px] text-charcoal-muted">
                    Automated analytical threat reasoning & pattern explanation
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <span className="px-2.5 py-1 rounded bg-cream-200 text-espresso-900 font-mono text-[12.5px] font-bold">
                  Confidence: {Math.round(incident.confidence * 100)}%
                </span>
              </div>
            </div>

            <div className="prose max-w-none text-[15.5px] text-charcoal leading-relaxed whitespace-pre-wrap">
              {incident.ai_explanation ||
                'Rule engine correlated high-velocity failed attempts matching automated adversarial signatures.'}
            </div>

            {incident.investigation_steps && incident.investigation_steps.length > 0 && (
              <div className="mt-5 pt-4 border-t border-cream-200">
                <h4 className="font-extrabold text-[14.5px] text-espresso-900 mb-2 uppercase tracking-wider">
                  Recommended Investigative Steps
                </h4>
                <ul className="space-y-2">
                  {incident.investigation_steps.map((step, idx) => (
                    <li key={idx} className="flex items-start gap-2.5 text-[14.5px] text-charcoal">
                      <span className="w-5 h-5 rounded-full bg-cream-200 text-espresso-900 font-bold text-[12px] flex items-center justify-center shrink-0 mt-0.5">
                        {idx + 1}
                      </span>
                      <span>{step}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* 2. Chronological Timeline */}
          <IncidentTimeline
            incidentId={incident.incident_id}
            events={incident.timeline_events || []}
            onEventAdded={loadIncident}
          />

          {/* 3. Indicators of Compromise (IOCs) */}
          <div className="cream-card p-6">
            <div className="border-b border-cream-200 pb-4 mb-4 flex items-center justify-between">
              <div>
                <h3 className="text-[18px] font-extrabold text-espresso-900">
                  Observed Indicators of Compromise (IOCs)
                </h3>
                <p className="text-[13.5px] text-charcoal-muted mt-0.5">
                  Actionable network and host indicators linked to this incident
                </p>
              </div>
              <button
                onClick={() => onNavigate('/threat-intel')}
                className="text-[13px] font-bold text-caramel hover:text-copper"
              >
                Open Threat Intel Hub →
              </button>
            </div>

            {incident.threat_indicators && incident.threat_indicators.length > 0 ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {incident.threat_indicators.map((ioc) => (
                  <ThreatIndicatorCard
                    key={ioc.id}
                    indicator={ioc}
                    onEnrich={(val) => onNavigate('/threat-intel')}
                  />
                ))}
              </div>
            ) : (
              <div className="p-6 text-center text-charcoal-muted text-[14px] bg-cream-100 rounded-xl border border-cream-200">
                Attacker IP: <strong className="font-mono text-espresso-900">{incident.source_ip || 'Unresolved'}</strong>
              </div>
            )}
          </div>

          {/* 4. Human-in-the-Loop Response Actions */}
          <div className="cream-card p-6">
            <div className="flex items-center justify-between border-b border-cream-200 pb-4 mb-5">
              <div>
                <h3 className="text-[18px] font-extrabold text-espresso-900 flex items-center gap-2">
                  <ShieldCheck className="w-5 h-5 text-soc-success" />
                  Response Playbook Recommendations
                </h3>
                <p className="text-[13.5px] text-charcoal-muted mt-0.5">
                  Human-in-the-Loop approval required for containment and remediation execution
                </p>
              </div>
            </div>

            <div className="space-y-4">
              {incident.response_actions?.map((act) => (
                <div
                  key={act.id}
                  className="bg-cream-100 p-5 rounded-xl border border-cream-200 space-y-3"
                >
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded bg-espresso-900 text-cream-100 font-mono font-bold text-[12px]">
                        {act.priority}
                      </span>
                      <h4 className="font-extrabold text-[16px] text-espresso-900">
                        {act.action}
                      </h4>
                    </div>

                    <span
                      className={`px-2.5 py-1 rounded-lg text-[12.5px] font-bold uppercase tracking-wider ${
                        act.status === 'APPROVED'
                          ? 'bg-emerald-100 text-emerald-800'
                          : act.status === 'EXECUTED'
                          ? 'bg-purple-100 text-purple-800'
                          : 'bg-amber-100 text-amber-800'
                      }`}
                    >
                      {act.status}
                    </span>
                  </div>

                  <p className="text-[14px] text-charcoal leading-relaxed">
                    {act.reason}
                  </p>

                  {/* CLI Command Preview */}
                  {act.command_preview && (
                    <div className="bg-espresso-950 text-cream-200 p-3.5 rounded-lg font-mono text-[13px] relative group overflow-x-auto">
                      <div className="flex items-center justify-between text-[11px] text-cream-400 mb-1.5 pb-1 border-b border-espresso-800">
                        <span>RECOMMENDED CONTAINMENT COMMAND</span>
                        <button
                          onClick={() => copyToClipboard(act.command_preview!, 'Command preview copied')}
                          className="hover:text-cream-100 flex items-center gap-1"
                        >
                          <Copy className="w-3.5 h-3.5" />
                          <span>Copy</span>
                        </button>
                      </div>
                      <pre className="whitespace-pre-wrap">{act.command_preview}</pre>
                    </div>
                  )}

                  {/* Analyst Approval Controls */}
                  <div className="flex items-center justify-end gap-2.5 pt-2 border-t border-cream-200">
                    {act.status === 'PROPOSED' && (
                      <>
                        <button
                          onClick={() => handleActionApproval(act.id, 'APPROVED')}
                          className="px-4 py-2 rounded-xl bg-soc-success hover:bg-emerald-700 text-white font-bold text-[13.5px] transition-colors"
                        >
                          Approve Action
                        </button>
                        <button
                          onClick={() => handleActionApproval(act.id, 'REJECTED')}
                          className="px-4 py-2 rounded-xl bg-cream-200 hover:bg-cream-300 text-charcoal-muted font-bold text-[13.5px] transition-colors"
                        >
                          Reject
                        </button>
                      </>
                    )}
                    {act.status === 'APPROVED' && (
                      <button
                        onClick={() => handleActionApproval(act.id, 'EXECUTED')}
                        className="px-4 py-2 rounded-xl bg-espresso-900 hover:bg-espresso-800 text-cream-100 font-bold text-[13.5px] transition-colors"
                      >
                        Mark as Executed
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* 5. Analyst Notes & Investigation Journal */}
          <div className="cream-card p-6">
            <h3 className="text-[18px] font-extrabold text-espresso-900 mb-1">
              Analyst Investigation Notes
            </h3>
            <p className="text-[13.5px] text-charcoal-muted mb-4">
              Immutable forensic triage journal for recording evidence, handoff notes, and executive summaries.
            </p>

            {incident.analyst_notes ? (
              <div className="bg-cream-100 p-4 rounded-xl border border-cream-200 text-[14.5px] text-charcoal whitespace-pre-wrap mb-4 font-mono leading-relaxed">
                {incident.analyst_notes}
              </div>
            ) : (
              <p className="text-[13.5px] text-charcoal-muted italic mb-4">
                No triage remarks logged yet.
              </p>
            )}

            <form onSubmit={handleAddNote} className="space-y-3">
              <textarea
                rows={3}
                placeholder="Append new forensic observation or mitigation update..."
                value={analystNoteText}
                onChange={(e) => setAnalystNoteText(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-cream-300 bg-cream-100 text-espresso-900 font-medium text-[14.5px] focus:outline-none focus:border-caramel resize-none"
              />
              <div className="flex justify-end">
                <button
                  type="submit"
                  disabled={isSavingNote || !analystNoteText.trim()}
                  className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-espresso-900 hover:bg-espresso-800 text-cream-100 font-bold text-[14px] shadow-sm disabled:opacity-50 transition-all"
                >
                  <Save className="w-4 h-4 text-caramel" />
                  <span>{isSavingNote ? 'Saving...' : 'Append Note to Record'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Right Column (1 Col): Risk Gauge, MITRE Matrix, Telemetry */}
        <div className="space-y-6">
          {/* Risk Gauge */}
          <RiskScoreGauge
            score={incident.risk_score}
            level={incident.risk_level}
            assessment={incident.risk_assessment}
          />

          {/* MITRE ATT&CK Mapping Card */}
          {incident.mitre_technique ? (
            <div className="cream-card p-6">
              <div className="flex items-center justify-between border-b border-cream-200 pb-3 mb-4">
                <h3 className="text-[17px] font-extrabold text-espresso-900 flex items-center gap-2">
                  <Layers className="w-5 h-5 text-caramel" />
                  MITRE ATT&CK Mapping
                </h3>
                <span className="font-mono text-[13px] font-bold bg-espresso-800 text-cream-100 px-2 py-0.5 rounded">
                  {incident.mitre_technique.technique_id}
                </span>
              </div>

              <div className="space-y-3">
                <div>
                  <p className="text-[12.5px] font-bold text-charcoal-muted uppercase tracking-wider">
                    Technique Name
                  </p>
                  <p className="text-[16px] font-bold text-espresso-900 mt-0.5">
                    {incident.mitre_technique.name}
                  </p>
                </div>

                <div>
                  <p className="text-[12.5px] font-bold text-charcoal-muted uppercase tracking-wider">
                    Tactic Category
                  </p>
                  <p className="text-[14px] font-semibold text-caramel mt-0.5">
                    {incident.mitre_technique.tactic}
                  </p>
                </div>

                <div>
                  <p className="text-[12.5px] font-bold text-charcoal-muted uppercase tracking-wider">
                    Defensive Mitigation
                  </p>
                  <p className="text-[13.5px] text-charcoal mt-0.5 leading-relaxed">
                    {incident.mitre_technique.mitigation || 'Implement rate limiting and multi-factor authentication.'}
                  </p>
                </div>
              </div>
            </div>
          ) : null}

          {/* Telemetry Profile */}
          <div className="cream-card p-6">
            <h3 className="text-[17px] font-extrabold text-espresso-900 border-b border-cream-200 pb-3 mb-4">
              Target Telemetry Profile
            </h3>

            <div className="space-y-3 text-[14px]">
              <div className="flex items-center justify-between">
                <span className="text-charcoal-muted">Origin Source IP:</span>
                <span className="font-mono font-bold text-espresso-900">{incident.source_ip || 'Unknown'}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-charcoal-muted">Target Service:</span>
                <span className="font-bold text-espresso-900">{incident.target_service?.toUpperCase() || 'General'}</span>
              </div>
              {incident.affected_asset && (
                <div className="flex items-center justify-between">
                  <span className="text-charcoal-muted">Affected Asset:</span>
                  <span className="font-mono font-bold text-espresso-900">{incident.affected_asset}</span>
                </div>
              )}
              <div className="flex items-center justify-between">
                <span className="text-charcoal-muted">Failed Attempts:</span>
                <span className="font-bold text-soc-danger">{incident.failed_attempts}</span>
              </div>
              {incident.target_accounts && incident.target_accounts.length > 0 && (
                <div className="pt-2 border-t border-cream-200">
                  <span className="text-charcoal-muted block mb-1">Targeted Accounts:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {incident.target_accounts.map((acc, i) => (
                      <span key={i} className="px-2 py-0.5 rounded bg-cream-200 font-mono text-[12.5px] font-bold text-espresso-900">
                        {acc}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
