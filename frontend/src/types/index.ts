export type Severity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type IncidentStatus = 'OPEN' | 'INVESTIGATING' | 'CONTAINED' | 'RESOLVED' | 'FALSE_POSITIVE';
export type ActionStatus = 'PROPOSED' | 'APPROVED' | 'REJECTED' | 'EXECUTED';
export type ActionPriority = 'P1' | 'P2' | 'P3' | 'P4';
export type UserRole = 'ADMIN' | 'ANALYST' | 'VIEWER';

export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface SecurityEvent {
  id?: number;
  timestamp?: string;
  event_type: string;
  source_ip?: string;
  destination_ip?: string;
  username?: string;
  service?: string;
  port?: number;
  status?: string;
  raw_log?: string;
}

export interface SecurityLog {
  id: number;
  filename: string;
  file_size: number;
  log_format: string;
  event_count: number;
  created_at: string;
}

export interface MitreTechnique {
  technique_id: string;
  name: string;
  tactic: string;
  description: string;
  detection?: string;
  mitigation?: string;
  url?: string;
}

export interface RiskFactor {
  name: string;
  score: number;
  max_score: number;
  description: string;
  evidence?: string;
}

export interface RiskAssessment {
  risk_score: number;
  risk_level: Severity;
  base_score?: number;
  frequency_score?: number;
  privilege_score?: number;
  service_score?: number;
  pattern_score?: number;
  confidence_score?: number;
  formula: string;
  summary: string;
  factors: RiskFactor[];
}

export interface ResponseAction {
  id: number;
  incident_id: number;
  action: string;
  reason: string;
  priority: ActionPriority;
  risk_level: string;
  command_preview?: string;
  status: ActionStatus;
  requires_approval: boolean;
  approved_by_id?: number;
  approved_at?: string;
  created_at: string;
}

export interface TimelineEvent {
  id: number;
  incident_id: number;
  timestamp: string;
  event_type: string;
  title: string;
  description: string;
  source: string;
  actor: string;
  status_after?: string;
}

export interface ThreatIndicator {
  id: number;
  incident_id?: number;
  indicator_type: string;
  value: string;
  threat_type: string;
  reputation_score: number;
  risk_level: string;
  confidence: number;
  source: string;
  country?: string;
  asn?: string;
  actor_group?: string;
  mitre_technique_id?: string;
  details?: string;
  first_seen: string;
  last_seen: string;
}

export interface ThreatEnrichment {
  indicator: string;
  indicator_type: string;
  reputation_score: number;
  risk_level: string;
  threat_classification: string;
  confidence: number;
  source_provenance: string;
  is_malicious: boolean;
  country?: string;
  asn?: string;
  actor_group?: string;
  mitre_techniques: string[];
  associated_attacks: string[];
  recommended_mitigation: string;
  raw_details: Record<string, any>;
}

export interface Incident {
  id: number;
  incident_id: string;
  title: string;
  description?: string;
  incident_type: string;
  severity: Severity;
  risk_score: number;
  risk_level: Severity;
  status: IncidentStatus;
  source_ip?: string;
  destination_ip?: string;
  target_service?: string;
  affected_asset?: string;
  target_accounts: string[];
  failed_attempts: number;
  mitre_technique_id?: string;
  confidence: number;
  ai_status: 'COMPLETED' | 'FALLBACK' | 'UNAVAILABLE';
  created_at: string;
  updated_at: string;
}

export interface IncidentDetail extends Incident {
  ai_explanation?: string;
  investigation_steps: string[];
  analyst_notes?: string;
  mitre_technique?: MitreTechnique;
  risk_assessment?: RiskAssessment;
  response_actions: ResponseAction[];
  evidence_events: SecurityEvent[];
  timeline_events: TimelineEvent[];
  threat_indicators: ThreatIndicator[];
}

export interface CopilotMessage {
  id: string;
  sender: 'user' | 'copilot';
  text: string;
  timestamp: string;
  suggestedFollowups?: string[];
  referencedEvidence?: string[];
  mitreReferences?: string[];
  copilotMode?: string;
}

export interface CopilotSuggestion {
  id: string;
  category: string;
  prompt: string;
  description: string;
}

export interface ReportItem {
  id: number;
  report_id: string;
  incident_id?: number;
  report_type: string;
  title: string;
  classification: string;
  executive_summary: string;
  threat_summary?: string;
  mitre_analysis?: string;
  recommended_actions?: string;
  analyst_notes?: string;
  resolution?: string;
  generated_by: string;
  created_at: string;
}

export interface AuditLog {
  id: number;
  user_id?: number;
  username?: string;
  action: string;
  entity_type: string;
  entity_id?: string;
  details?: string;
  ip_address?: string;
  timestamp: string;
}

export interface DashboardSummary {
  total_incidents: number;
  severity_breakdown: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  status_breakdown: {
    open: number;
    investigating: number;
    contained: number;
    resolved: number;
    false_positive: number;
  };
  average_risk_score: number;
  total_logs_processed: number;
  total_events_normalized: number;
  pending_response_actions: number;
  recent_incidents: Incident[];
}

export interface AttackDistributionItem {
  incident_type: string;
  count: number;
  percentage: number;
}

export interface MitreDistributionItem {
  technique_id: string;
  technique_name: string;
  tactic: string;
  count: number;
}

export interface TopSourceIpItem {
  source_ip: string;
  incident_count: number;
  failed_attempts: number;
  severity: Severity;
}

export interface TopTargetItem {
  target: string;
  count: number;
  service: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message: string;
  error?: {
    code: string;
    message: string;
  };
}
