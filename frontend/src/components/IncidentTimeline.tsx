import React, { useState } from 'react';
import { TimelineEvent } from '../types';
import {
  Clock,
  Radio,
  Search,
  Sparkles,
  ShieldCheck,
  Lock,
  RotateCcw,
  CheckCircle,
  FileEdit,
  PlusCircle,
  User,
} from 'lucide-react';
import { useToast } from './Toast';
import { api } from '../services/api';

interface IncidentTimelineProps {
  incidentId: string;
  events: TimelineEvent[];
  onEventAdded?: () => void;
}

export const IncidentTimeline: React.FC<IncidentTimelineProps> = ({
  incidentId,
  events,
  onEventAdded,
}) => {
  const { showToast } = useToast();
  const [showAddModal, setShowAddModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newType, setNewType] = useState('INITIAL_INVESTIGATION');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const getEventIcon = (type: string) => {
    switch (type.toUpperCase()) {
      case 'DETECTION':
        return { icon: Radio, color: 'bg-red-100 text-red-700 border-red-300' };
      case 'INITIAL_INVESTIGATION':
        return { icon: Search, color: 'bg-blue-100 text-blue-700 border-blue-300' };
      case 'AI_ANALYSIS':
        return { icon: Sparkles, color: 'bg-amber-100 text-amber-700 border-amber-300' };
      case 'THREAT_CONFIRMED':
        return { icon: ShieldCheck, color: 'bg-orange-100 text-orange-700 border-orange-300' };
      case 'CONTAINMENT':
        return { icon: Lock, color: 'bg-purple-100 text-purple-700 border-purple-300' };
      case 'RECOVERY':
        return { icon: RotateCcw, color: 'bg-teal-100 text-teal-700 border-teal-300' };
      case 'RESOLUTION':
        return { icon: CheckCircle, color: 'bg-emerald-100 text-emerald-700 border-emerald-300' };
      case 'NOTE_ADDED':
      default:
        return { icon: FileEdit, color: 'bg-cream-200 text-espresso-800 border-cream-300' };
    }
  };

  const handleAddEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle.trim() || !newDesc.trim()) return;

    setIsSubmitting(true);
    try {
      await api.addTimelineEvent(incidentId, {
        event_type: newType,
        title: newTitle.trim(),
        description: newDesc.trim(),
        source: 'SOC Web UI',
        actor: 'Security Analyst',
      });
      showToast('success', 'Timeline Updated', 'New investigation milestone logged.');
      setNewTitle('');
      setNewDesc('');
      setShowAddModal(false);
      if (onEventAdded) onEventAdded();
    } catch (err: any) {
      showToast('error', 'Failed to Add Event', err.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="cream-card p-6">
      <div className="flex items-center justify-between border-b border-cream-200 pb-4 mb-6">
        <div>
          <h3 className="text-[18px] font-extrabold text-espresso-900 flex items-center gap-2">
            <Clock className="w-5 h-5 text-caramel" />
            Incident Forensic Timeline
          </h3>
          <p className="text-[13.5px] text-charcoal-muted mt-0.5">
            Chronological log of detection, AI analysis, containment, and resolution
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cream-200 hover:bg-cream-300 text-espresso-900 font-bold text-[13px] border border-cream-300 transition-colors"
        >
          <PlusCircle className="w-4 h-4 text-caramel" />
          <span>Add Milestone</span>
        </button>
      </div>

      {/* Timeline Stream */}
      {events.length === 0 ? (
        <div className="py-8 text-center text-charcoal-muted text-[14.5px]">
          No timeline milestones recorded for this incident yet.
        </div>
      ) : (
        <div className="relative pl-6 space-y-6 before:absolute before:left-3.5 before:top-3 before:bottom-3 before:w-0.5 before:bg-cream-300">
          {events.map((evt, idx) => {
            const { icon: Icon, color } = getEventIcon(evt.event_type);
            const dateStr = new Date(evt.timestamp).toLocaleString('en-US', {
              month: 'short',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
            });

            return (
              <div key={evt.id || idx} className="relative flex items-start gap-4">
                {/* Node Icon */}
                <div
                  className={`w-7 h-7 rounded-full border flex items-center justify-center shrink-0 -ml-7 z-10 shadow-xs ${color}`}
                >
                  <Icon className="w-3.5 h-3.5" />
                </div>

                {/* Event Content Card */}
                <div className="flex-1 bg-cream-100 p-4 rounded-xl border border-cream-200 shadow-xs">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <h4 className="font-bold text-[15px] text-espresso-900">
                      {evt.title}
                    </h4>
                    <span className="text-[12.5px] font-mono text-charcoal-subtle">
                      {dateStr}
                    </span>
                  </div>

                  <p className="text-[14px] text-charcoal mt-1.5 leading-relaxed whitespace-pre-wrap">
                    {evt.description}
                  </p>

                  <div className="mt-3 pt-2.5 border-t border-cream-200 flex items-center justify-between text-[12.5px] text-charcoal-muted">
                    <span className="flex items-center gap-1.5">
                      <User className="w-3.5 h-3.5 text-caramel" />
                      <span>Actor: <strong className="text-espresso-900">{evt.actor}</strong></span>
                    </span>
                    <span className="bg-cream-200 px-2 py-0.5 rounded font-mono text-[11.5px] text-espresso-800 font-semibold">
                      {evt.source}
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Add Milestone Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl border border-cream-300 shadow-elevated max-w-lg w-full p-6 animate-in fade-in zoom-in-95">
            <h3 className="text-[20px] font-black text-espresso-900 mb-1">
              Add Timeline Milestone
            </h3>
            <p className="text-[13.5px] text-charcoal-muted mb-4">
              Record a significant triage observation, containment action, or forensic finding.
            </p>

            <form onSubmit={handleAddEvent} className="space-y-4">
              <div>
                <label className="block text-[13.5px] font-bold text-espresso-900 mb-1">
                  Milestone Category
                </label>
                <select
                  value={newType}
                  onChange={(e) => setNewType(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-cream-300 bg-cream-100 text-espresso-900 font-medium text-[14.5px] focus:outline-none focus:border-caramel"
                >
                  <option value="INITIAL_INVESTIGATION">Initial Investigation</option>
                  <option value="AI_ANALYSIS">AI Analysis Review</option>
                  <option value="THREAT_CONFIRMED">Threat Confirmed</option>
                  <option value="CONTAINMENT">Containment Executed</option>
                  <option value="RECOVERY">Host Recovery</option>
                  <option value="RESOLUTION">Remediation / Resolution</option>
                  <option value="NOTE_ADDED">Analyst Remark</option>
                </select>
              </div>

              <div>
                <label className="block text-[13.5px] font-bold text-espresso-900 mb-1">
                  Milestone Title
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Memory dump acquired from workstation-fin-08"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-cream-300 bg-cream-100 text-espresso-900 font-medium text-[14.5px] focus:outline-none focus:border-caramel"
                />
              </div>

              <div>
                <label className="block text-[13.5px] font-bold text-espresso-900 mb-1">
                  Detailed Findings / Action Description
                </label>
                <textarea
                  required
                  rows={3}
                  placeholder="Explain forensic evidence, process IDs, or network verification..."
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-cream-300 bg-cream-100 text-espresso-900 font-medium text-[14.5px] focus:outline-none focus:border-caramel resize-none"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-3 border-t border-cream-200">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded-xl text-[14px] font-bold text-charcoal-muted hover:bg-cream-200 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-5 py-2 rounded-xl bg-espresso-900 hover:bg-espresso-800 text-cream-100 font-bold text-[14px] shadow-sm transition-all"
                >
                  {isSubmitting ? 'Logging...' : 'Save Milestone'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
