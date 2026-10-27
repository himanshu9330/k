import React, { useEffect, useState } from 'react';
import {
  ShieldAlert,
  Flame,
  Activity,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  TrendingUp,
  FileText,
  Radio,
  Layers,
  Sparkles,
} from 'lucide-react';
import { DashboardSummary, Incident } from '../types';
import { api } from '../services/api';
import { StatsCard } from '../components/StatsCard';
import { SeverityBadge } from '../components/SeverityBadge';
import { StatusBadge } from '../components/StatusBadge';

interface DashboardPageProps {
  onNavigate: (path: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [attackDist, setAttackDist] = useState<any[]>([]);
  const [mitreDist, setMitreDist] = useState<any[]>([]);
  const [topAttackers, setTopAttackers] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const [sumRes, atkRes, mitRes, topRes] = await Promise.all([
          api.getDashboardSummary(),
          api.getAttackDistribution(),
          api.getMitreDistribution(),
          api.getTopAttackers(),
        ]);
        setSummary(sumRes);
        setAttackDist(atkRes);
        setMitreDist(mitRes);
        setTopAttackers(topRes);
      } catch (err) {
        console.error('Error loading dashboard:', err);
      } finally {
        setIsLoading(false);
      }
    };
    loadDashboard();
  }, []);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh]">
        <div className="w-12 h-12 rounded-full border-4 border-espresso-800 border-t-caramel animate-spin" />
        <p className="mt-4 font-bold text-[16px] text-espresso-900">
          Loading Security Operations Telemetry...
        </p>
      </div>
    );
  }

  const criticalCount = summary?.severity_breakdown.critical || 0;
  const highCount = summary?.severity_breakdown.high || 0;
  const openCount = summary?.status_breakdown.open || 0;
  const investigatingCount = summary?.status_breakdown.investigating || 0;

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Top Banner with Alert State */}
      <div className="bg-espresso-900 text-[#EFE6D8] rounded-2xl p-7 shadow-espresso border border-espresso-700 relative overflow-hidden flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div className="z-10 max-w-2xl">
          <div className="flex items-center gap-2.5 px-3 py-1 rounded-full bg-espresso-800 border border-caramel/40 text-caramel text-[12.5px] font-mono font-bold w-fit mb-3">
            <Radio className="w-3.5 h-3.5 animate-pulse text-red-500" />
            <span>REAL-TIME THREAT DEFENSE ACTIVE</span>
          </div>
          <h1 className="text-[28px] md:text-[34px] font-black text-cream-100 tracking-tight leading-tight">
            Security Operations Center (SOC)
          </h1>
          <p className="text-[15.5px] text-cream-300 mt-2 leading-relaxed">
            Multi-source log telemetry ingestion, autonomous Gemini AI investigation,
            deterministic 6-factor risk scoring, and MITRE ATT&CK alignment.
          </p>
        </div>

        <div className="z-10 flex flex-wrap items-center gap-3">
          <button
            onClick={() => onNavigate('/upload')}
            className="px-5 py-3 rounded-xl bg-caramel hover:bg-caramel-hover text-white font-extrabold text-[15px] shadow-sm transition-all hover:scale-[1.02]"
          >
            + Analyze New Log
          </button>
          <button
            onClick={() => onNavigate('/copilot')}
            className="px-5 py-3 rounded-xl bg-espresso-800 hover:bg-espresso-700 text-cream-100 border border-espresso-600 font-extrabold text-[15px] transition-all flex items-center gap-2"
          >
            <Sparkles className="w-4 h-4 text-caramel" />
            <span>AI Copilot</span>
          </button>
        </div>
      </div>

      {/* Primary KPI Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatsCard
          title="Active Triage Queue"
          value={openCount + investigatingCount}
          subtitle={`${criticalCount} Critical, ${highCount} High priority`}
          icon={ShieldAlert}
          accentColor={criticalCount > 0 ? 'danger' : 'warning'}
        />
        <StatsCard
          title="Average Risk Score"
          value={`${summary?.average_risk_score || 0} / 100`}
          subtitle="Multi-factor mathematical rating"
          icon={Flame}
          accentColor="caramel"
        />
        <StatsCard
          title="Total Events Analyzed"
          value={summary?.total_events_normalized.toLocaleString() || '0'}
          subtitle={`Across ${summary?.total_logs_processed || 0} security log streams`}
          icon={Activity}
          accentColor="espresso"
        />
        <StatsCard
          title="Pending Response Actions"
          value={summary?.pending_response_actions || 0}
          subtitle="Awaiting Human-in-the-Loop review"
          icon={CheckCircle2}
          accentColor="success"
        />
      </div>

      {/* Main Grid: Incident Queue & Threat Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Incidents Feed (2 Cols) */}
        <div className="lg:col-span-2 cream-card p-6 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b border-cream-200 pb-4 mb-5">
              <div>
                <h3 className="text-[20px] font-black text-espresso-900">
                  Active Incidents Feed
                </h3>
                <p className="text-[14px] text-charcoal-muted mt-0.5">
                  Latest threat events prioritized by deterministic risk score
                </p>
              </div>
              <button
                onClick={() => onNavigate('/incidents')}
                className="text-[14px] font-bold text-caramel hover:text-copper flex items-center gap-1"
              >
                <span>View All ({summary?.total_incidents || 0})</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>

            {/* List of Incidents */}
            <div className="space-y-3">
              {summary?.recent_incidents?.slice(0, 5).map((inc) => (
                <div
                  key={inc.id}
                  onClick={() => onNavigate(`/incidents/${inc.incident_id}`)}
                  className="p-4 rounded-xl bg-cream-100 hover:bg-cream-200 border border-cream-200 transition-all cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-4"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2.5 mb-1.5">
                      <span className="font-mono font-bold text-[13px] text-espresso-900 bg-cream-200 px-2 py-0.5 rounded">
                        {inc.incident_id}
                      </span>
                      <SeverityBadge severity={inc.severity} size="sm" />
                      <StatusBadge status={inc.status} size="sm" />
                    </div>

                    <h4 className="font-bold text-[16px] text-espresso-900 truncate">
                      {inc.title}
                    </h4>

                    <div className="mt-1 flex flex-wrap items-center gap-3 text-[13px] text-charcoal-muted">
                      <span>Source: <strong className="font-mono text-espresso-900">{inc.source_ip || 'N/A'}</strong></span>
                      <span>Target: <strong className="text-espresso-900">{inc.target_service?.toUpperCase() || 'General'}</strong></span>
                      {inc.mitre_technique_id && (
                        <span className="bg-espresso-800 text-cream-100 font-mono text-[11.5px] px-2 py-0.5 rounded font-semibold">
                          {inc.mitre_technique_id}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex sm:flex-col items-end justify-between shrink-0">
                    <div className="text-right">
                      <div className="text-[20px] font-black text-espresso-900">
                        {inc.risk_score}<span className="text-[12px] text-charcoal-muted font-normal">/100</span>
                      </div>
                      <div className="text-[12px] font-semibold text-charcoal-muted uppercase">
                        {inc.risk_level} Risk
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-5 pt-4 border-t border-cream-200 text-center">
            <button
              onClick={() => onNavigate('/incidents')}
              className="w-full py-2.5 rounded-xl bg-cream-200 hover:bg-cream-300 text-espresso-900 font-bold text-[14.5px] transition-colors"
            >
              Open Full Incident Investigation Queue →
            </button>
          </div>
        </div>

        {/* Threat Distribution & MITRE Heatmap (1 Col) */}
        <div className="space-y-6">
          {/* Attack Classification */}
          <div className="cream-card p-6">
            <div className="flex items-center justify-between border-b border-cream-200 pb-3 mb-4">
              <h3 className="text-[17px] font-extrabold text-espresso-900">
                Threat Classification
              </h3>
              <span className="text-[12px] font-bold text-charcoal-muted uppercase">
                Distribution
              </span>
            </div>

            <div className="space-y-3">
              {attackDist.slice(0, 4).map((atk, idx) => (
                <div key={idx} className="bg-cream-100 p-3 rounded-xl border border-cream-200">
                  <div className="flex items-center justify-between text-[14px] font-bold text-espresso-900">
                    <span className="truncate pr-2">{atk.incident_type}</span>
                    <span className="font-mono text-caramel">{atk.count}</span>
                  </div>
                  <div className="w-full h-2 bg-cream-200 rounded-full mt-2 overflow-hidden">
                    <div
                      className="h-full bg-caramel rounded-full"
                      style={{ width: `${Math.min(atk.percentage * 2, 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Top Adversary Sources */}
          <div className="cream-card p-6">
            <div className="flex items-center justify-between border-b border-cream-200 pb-3 mb-4">
              <h3 className="text-[17px] font-extrabold text-espresso-900">
                Top Adversary Sources
              </h3>
              <span className="text-[12px] font-bold text-charcoal-muted uppercase">
                Velocity
              </span>
            </div>

            <div className="space-y-2.5">
              {topAttackers.slice(0, 4).map((atk, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-2.5 rounded-lg bg-cream-100 border border-cream-200"
                >
                  <div>
                    <p className="font-mono font-bold text-[14px] text-espresso-900">
                      {atk.source_ip}
                    </p>
                    <p className="text-[12px] text-charcoal-muted">
                      {atk.failed_attempts} failed bursts
                    </p>
                  </div>
                  <SeverityBadge severity={atk.severity} size="sm" showDot={false} />
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
