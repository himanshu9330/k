/**
 * SentinelAI-X Frontend API Client Service
 * ========================================
 * Provides typed fetch functions communicating with FastAPI backend.
 */

import {
  Incident,
  IncidentDetail,
  DashboardSummary,
  MitreTechnique,
  AuditLog,
  TimelineEvent,
  ThreatIndicator,
  ThreatEnrichment,
  CopilotSuggestion,
  ReportItem,
  ApiResponse
} from '../types';

const API_BASE = '/api';

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: options.body instanceof FormData ? options.headers : { ...defaultHeaders, ...options.headers },
  });

  if (!response.ok) {
    let errorMsg = `HTTP Error ${response.status}: ${response.statusText}`;
    try {
      const errJson = await response.json();
      if (errJson.detail) errorMsg = errJson.detail;
      else if (errJson.error?.message) errorMsg = errJson.error.message;
    } catch {
      // fallback
    }
    throw new Error(errorMsg);
  }

  const json: ApiResponse<T> = await response.json();
  return json.data;
}

export const api = {
  // Dashboard & Metrics
  getDashboardSummary: () => request<DashboardSummary>('/dashboard/summary'),
  getAttackDistribution: () => request<any[]>('/dashboard/attacks'),
  getMitreDistribution: () => request<any[]>('/dashboard/mitre-distribution'),
  getTopAttackers: () => request<any[]>('/dashboard/top-attackers'),

  // Incidents
  getIncidents: (params: Record<string, string | number> = {}) => {
    const query = new URLSearchParams(params as Record<string, string>).toString();
    return request<Incident[]>(`/incidents${query ? `?${query}` : ''}`);
  },
  getIncidentDetails: (id: string) => request<IncidentDetail>(`/incidents/${id}`),
  updateIncidentStatus: (id: string, status: string, notes?: string) =>
    request<Incident>(`/incidents/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status, notes }),
    }),
  addIncidentNote: (id: string, note: string) =>
    request<IncidentDetail>(`/incidents/${id}/notes`, {
      method: 'POST',
      body: JSON.stringify({ note }),
    }),
  updateActionStatus: (incidentId: string, actionId: number, status: string) =>
    request<any>(`/incidents/${incidentId}/response-actions/${actionId}/status`, {
      method: 'POST',
      body: JSON.stringify({ status }),
    }),

  // Timeline
  getIncidentTimeline: (id: string) => request<TimelineEvent[]>(`/incidents/${id}/timeline`),
  addTimelineEvent: (id: string, data: { event_type: string; title: string; description: string; source?: string; actor?: string }) =>
    request<TimelineEvent>(`/incidents/${id}/timeline`, {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Threat Intelligence & IOCs
  lookupThreat: (indicator: string, indicator_type?: string) =>
    request<ThreatEnrichment>('/threats/lookup', {
      method: 'POST',
      body: JSON.stringify({ indicator, indicator_type }),
    }),
  getThreatIndicators: (indicator_type?: string) => {
    const query = indicator_type ? `?indicator_type=${indicator_type}` : '';
    return request<ThreatIndicator[]>(`/threats/indicators${query}`);
  },

  // AI Copilot
  copilotChat: (message: string, incident_id?: string, chat_history?: { role: string; content: string }[]) =>
    request<{ reply: string; incident_id?: string; suggested_followups: string[]; referenced_evidence: string[]; mitre_references: string[]; copilot_mode: string }>('/copilot/chat', {
      method: 'POST',
      body: JSON.stringify({ message, incident_id, chat_history }),
    }),
  getCopilotSuggestions: () => request<CopilotSuggestion[]>('/copilot/suggestions'),

  // Log Upload & Analysis
  uploadLog: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return request<any>('/logs/upload', {
      method: 'POST',
      body: formData,
    });
  },

  // Reports
  generateReport: (incident_id: string, report_type: string = 'EXECUTIVE_BRIEFING', analyst_notes?: string) =>
    request<ReportItem>('/reports/generate', {
      method: 'POST',
      body: JSON.stringify({ incident_id, report_type, analyst_notes }),
    }),
  getReports: (report_type?: string) => {
    const query = report_type ? `?report_type=${report_type}` : '';
    return request<ReportItem[]>(`/reports${query}`);
  },
  getReportById: (report_id: string) => request<ReportItem>(`/reports/${report_id}`),
  getIncidentBriefing: (incident_id: string) => request<any>(`/incidents/${incident_id}/report`),

  // MITRE & Audit
  getMitreTechniques: () => request<MitreTechnique[]>('/mitre/techniques'),
  getAuditLogs: () => request<AuditLog[]>('/audit'),
  healthCheck: () => request<any>('/health'),
};
