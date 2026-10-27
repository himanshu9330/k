import React, { useEffect, useState } from 'react';
import { ScrollText, Search, ShieldCheck, RefreshCw, Lock } from 'lucide-react';
import { api } from '../services/api';
import { AuditLog } from '../types';

export const AuditPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(true);

  const loadAuditLogs = async () => {
    setIsLoading(true);
    try {
      const data = await api.getAuditLogs();
      setLogs(data);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAuditLogs();
  }, []);

  const filtered = logs.filter((l) => {
    const search = searchTerm.toLowerCase();
    return (
      l.action.toLowerCase().includes(search) ||
      (l.username && l.username.toLowerCase().includes(search)) ||
      (l.entity_id && l.entity_id.toLowerCase().includes(search)) ||
      (l.details && l.details.toLowerCase().includes(search))
    );
  });

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-[28px] md:text-[32px] font-black text-espresso-900 tracking-tight">
            Forensic Audit & Compliance Trail
          </h1>
          <p className="text-[15px] text-charcoal-muted mt-1">
            Immutable SOC tamper-evident audit log with automatic credential redaction and RBAC tracking.
          </p>
        </div>

        <button
          onClick={loadAuditLogs}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-cream-200 hover:bg-cream-300 text-espresso-900 font-bold text-[14px] border border-cream-300 transition-colors self-start sm:self-auto"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          <span>Refresh Audit</span>
        </button>
      </div>

      {/* Filter Bar */}
      <div className="cream-card p-4">
        <div className="relative">
          <Search className="w-5 h-5 absolute left-3.5 top-3 text-charcoal-muted" />
          <input
            type="text"
            placeholder="Filter audit entries by action, username, or incident ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-11 pr-4 py-2.5 rounded-xl border border-cream-300 bg-cream-100 text-espresso-900 font-medium text-[15px] focus:outline-none focus:border-caramel"
          />
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="cream-card overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center">
            <div className="w-8 h-8 rounded-full border-3 border-espresso-800 border-t-caramel animate-spin mx-auto" />
            <p className="mt-3 font-bold text-espresso-900">Loading audit trail...</p>
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center text-charcoal-muted text-[15px]">
            No audit records matching criteria.
          </div>
        ) : (
          <div className="divide-y divide-cream-200">
            {filtered.map((log) => (
              <div key={log.id} className="p-4 hover:bg-cream-100 transition-colors">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-3">
                    <span className="px-2.5 py-0.5 rounded bg-espresso-900 text-cream-100 font-mono text-[12px] font-bold">
                      {log.action}
                    </span>
                    <span className="font-bold text-[15px] text-espresso-900">
                      {log.username || 'System Engine'}
                    </span>
                    {log.entity_id && (
                      <span className="font-mono text-[13px] bg-cream-200 px-2 py-0.5 rounded text-charcoal font-semibold">
                        {log.entity_id}
                      </span>
                    )}
                  </div>

                  <span className="text-[13px] font-mono text-charcoal-muted">
                    {new Date(log.timestamp).toLocaleString()}
                  </span>
                </div>

                {log.details && (
                  <div className="mt-2 text-[13.5px] font-mono text-charcoal bg-cream-100/90 p-2.5 rounded-lg border border-cream-200 whitespace-pre-wrap break-all">
                    {log.details}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
