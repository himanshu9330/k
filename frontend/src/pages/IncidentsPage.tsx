import React, { useEffect, useState } from 'react';
import { Incident, Severity, IncidentStatus } from '../types';
import { api } from '../services/api';
import { SeverityBadge } from '../components/SeverityBadge';
import { StatusBadge } from '../components/StatusBadge';
import { useToast } from '../components/Toast';
import {
  Search,
  Filter,
  ShieldAlert,
  ArrowUpDown,
  RefreshCw,
  Eye,
  CheckCircle,
} from 'lucide-react';

interface IncidentsPageProps {
  onNavigate: (path: string) => void;
}

export const IncidentsPage: React.FC<IncidentsPageProps> = ({ onNavigate }) => {
  const { showToast } = useToast();
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSeverity, setSelectedSeverity] = useState<string>('ALL');
  const [selectedStatus, setSelectedStatus] = useState<string>('ALL');

  const loadIncidents = async () => {
    setIsLoading(true);
    try {
      const params: Record<string, string> = {};
      if (selectedSeverity !== 'ALL') params.severity = selectedSeverity;
      if (selectedStatus !== 'ALL') params.status = selectedStatus;
      if (searchTerm.trim()) params.search = searchTerm.trim();

      const data = await api.getIncidents(params);
      setIncidents(data);
    } catch (err: any) {
      showToast('error', 'Failed to Load Incidents', err.message);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadIncidents();
  }, [selectedSeverity, selectedStatus]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadIncidents();
  };

  const handleQuickStatusChange = async (incidentId: string, newStatus: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await api.updateIncidentStatus(incidentId, newStatus);
      showToast('success', 'Status Updated', `Incident ${incidentId} set to ${newStatus}.`);
      loadIncidents();
    } catch (err: any) {
      showToast('error', 'Status Update Failed', err.message);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-[28px] md:text-[32px] font-black text-espresso-900 tracking-tight">
            Incident Triage & Response Queue
          </h1>
          <p className="text-[15px] text-charcoal-muted mt-1">
            Prioritized operational queue with AI-assisted risk classification and mitigation playbooks.
          </p>
        </div>

        <button
          onClick={loadIncidents}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-cream-200 hover:bg-cream-300 text-espresso-900 font-bold text-[14px] border border-cream-300 transition-colors self-start sm:self-auto"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh Queue</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="cream-card p-5">
        <form onSubmit={handleSearchSubmit} className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Search Input */}
          <div className="relative sm:col-span-2">
            <Search className="w-5 h-5 absolute left-3.5 top-3 text-charcoal-muted" />
            <input
              type="text"
              placeholder="Search by ID, IP, threat type, or affected asset..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-11 pr-4 py-2.5 rounded-xl border border-cream-300 bg-cream-100 text-espresso-900 font-medium text-[15px] focus:outline-none focus:border-caramel placeholder:text-charcoal-muted/70"
            />
          </div>

          {/* Severity Dropdown */}
          <div>
            <select
              value={selectedSeverity}
              onChange={(e) => setSelectedSeverity(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-cream-300 bg-cream-100 text-espresso-900 font-semibold text-[14.5px] focus:outline-none focus:border-caramel"
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">🔴 Critical Severity</option>
              <option value="HIGH">🟠 High Severity</option>
              <option value="MEDIUM">🟡 Medium Severity</option>
              <option value="LOW">🟢 Low Severity</option>
            </select>
          </div>

          {/* Status Dropdown */}
          <div>
            <select
              value={selectedStatus}
              onChange={(e) => setSelectedStatus(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-cream-300 bg-cream-100 text-espresso-900 font-semibold text-[14.5px] focus:outline-none focus:border-caramel"
            >
              <option value="ALL">All Lifecycle Statuses</option>
              <option value="OPEN">Open / Untriaged</option>
              <option value="INVESTIGATING">Under Investigation</option>
              <option value="CONTAINED">Contained</option>
              <option value="RESOLVED">Resolved</option>
              <option value="FALSE_POSITIVE">False Positive</option>
            </select>
          </div>
        </form>
      </div>

      {/* Incidents Table / List (Optimized Vertical Density) */}
      <div className="cream-card overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center">
            <div className="w-10 h-10 rounded-full border-4 border-espresso-800 border-t-caramel animate-spin mx-auto" />
            <p className="mt-3 font-bold text-espresso-900">Filtering incidents...</p>
          </div>
        ) : incidents.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <ShieldAlert className="w-12 h-12 text-charcoal-muted mx-auto" />
            <h3 className="text-[18px] font-extrabold text-espresso-900">
              No matching incidents found
            </h3>
            <p className="text-[14px] text-charcoal-muted max-w-md mx-auto">
              Try adjusting your search criteria or ingest a new log stream using the Log Analyzer.
            </p>
          </div>
        ) : (
          <div className="divide-y divide-cream-200">
            {incidents.map((inc) => (
              <div
                key={inc.id}
                onClick={() => onNavigate(`/incidents/${inc.incident_id}`)}
                className="p-5 hover:bg-cream-100/80 transition-colors cursor-pointer flex flex-col md:flex-row md:items-center justify-between gap-4"
              >
                {/* Left Telemetry Column */}
                <div className="flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2.5 mb-1.5">
                    <span className="font-mono font-black text-[14px] text-espresso-900 bg-cream-200 px-2.5 py-0.5 rounded border border-cream-300">
                      {inc.incident_id}
                    </span>
                    <SeverityBadge severity={inc.severity} size="sm" />
                    <StatusBadge status={inc.status} size="sm" />
                    {inc.mitre_technique_id && (
                      <span className="bg-espresso-800 text-cream-100 font-mono text-[12px] px-2 py-0.5 rounded font-bold">
                        MITRE {inc.mitre_technique_id}
                      </span>
                    )}
                  </div>

                  <h3 className="font-extrabold text-[17px] text-espresso-900 hover:text-caramel transition-colors">
                    {inc.title}
                  </h3>

                  {inc.description && (
                    <p className="text-[14px] text-charcoal-muted mt-1 line-clamp-1">
                      {inc.description}
                    </p>
                  )}

                  <div className="mt-2.5 flex flex-wrap items-center gap-4 text-[13.5px] text-charcoal-muted">
                    <span>
                      Attacker IP: <strong className="font-mono text-espresso-900">{inc.source_ip || 'Unresolved'}</strong>
                    </span>
                    <span>
                      Target Service: <strong className="text-espresso-900">{inc.target_service?.toUpperCase() || 'HTTP/SSH'}</strong>
                    </span>
                    {inc.affected_asset && (
                      <span>
                        Asset: <strong className="font-mono text-espresso-900">{inc.affected_asset}</strong>
                      </span>
                    )}
                    <span>
                      Observed: <strong className="text-espresso-900">{new Date(inc.created_at).toLocaleDateString()}</strong>
                    </span>
                  </div>
                </div>

                {/* Right Risk Score & Quick Actions */}
                <div className="flex items-center justify-between md:justify-end gap-6 shrink-0 pt-3 md:pt-0 border-t md:border-t-0 border-cream-200">
                  <div className="text-left md:text-right">
                    <div className="text-[24px] font-black text-espresso-900 leading-none">
                      {inc.risk_score}<span className="text-[13px] text-charcoal-muted font-normal">/100</span>
                    </div>
                    <span className="text-[12px] font-bold text-charcoal-muted uppercase tracking-wider">
                      {inc.risk_level} Risk
                    </span>
                  </div>

                  <div className="flex items-center gap-2">
                    {/* Quick Status Shift */}
                    <select
                      value={inc.status}
                      onClick={(e) => e.stopPropagation()}
                      onChange={(e) => handleQuickStatusChange(inc.incident_id, e.target.value, e as any)}
                      className="px-3 py-1.5 rounded-lg border border-cream-300 bg-white text-espresso-900 font-bold text-[13px] focus:outline-none focus:border-caramel"
                    >
                      <option value="OPEN">Open</option>
                      <option value="INVESTIGATING">Investigate</option>
                      <option value="CONTAINED">Contained</option>
                      <option value="RESOLVED">Resolved</option>
                      <option value="FALSE_POSITIVE">False Alarm</option>
                    </select>

                    <button
                      onClick={() => onNavigate(`/incidents/${inc.incident_id}`)}
                      className="p-2 rounded-lg bg-espresso-900 hover:bg-espresso-800 text-cream-100 transition-colors"
                      title="View Deep-Dive Investigation"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
