import React from 'react';
import { Settings, ShieldCheck, Database, Cpu, Lock, CheckCircle2, Server, Globe } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  return (
    <div className="space-y-8 max-w-5xl mx-auto pb-16">
      {/* Header */}
      <div>
        <h1 className="text-[28px] md:text-[32px] font-black text-espresso-900 tracking-tight">
          System Configuration & DevSecOps
        </h1>
        <p className="text-[15px] text-charcoal-muted mt-1">
          Operational controls, database connection parameters, and security architecture status.
        </p>
      </div>

      {/* Security Architecture Hardening Grid */}
      <div className="cream-card p-6 space-y-6">
        <h3 className="text-[18px] font-extrabold text-espresso-900 border-b border-cream-200 pb-3 flex items-center gap-2">
          <ShieldCheck className="w-5 h-5 text-soc-success" />
          DevSecOps Defense & Hardening Layer
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-cream-100 p-4 rounded-xl border border-cream-200 space-y-1.5">
            <div className="flex items-center gap-2 text-espresso-900 font-bold text-[15px]">
              <Lock className="w-4 h-4 text-caramel" />
              <span>Prompt Injection Boundary Encapsulation</span>
            </div>
            <p className="text-[13.5px] text-charcoal leading-relaxed">
              Untrusted log content is rigorously sandboxed within explicit tag delimiters (<code>&lt;&lt;&lt;UNTRUSTED_SECURITY_LOG_DATA_START&gt;&gt;&gt;</code>) to prevent adversarial instruction hijack.
            </p>
          </div>

          <div className="bg-cream-100 p-4 rounded-xl border border-cream-200 space-y-1.5">
            <div className="flex items-center gap-2 text-espresso-900 font-bold text-[15px]">
              <CheckCircle2 className="w-4 h-4 text-soc-success" />
              <span>Multi-Format Normalization Engine</span>
            </div>
            <p className="text-[13.5px] text-charcoal leading-relaxed">
              Normalizes syslog (SSH/sudo), Nginx web access logs, raw JSON, and CSV into structured telemetry events with zero hallucinated parameters.
            </p>
          </div>

          <div className="bg-cream-100 p-4 rounded-xl border border-cream-200 space-y-1.5">
            <div className="flex items-center gap-2 text-espresso-900 font-bold text-[15px]">
              <Lock className="w-4 h-4 text-caramel" />
              <span>JWT Authentication & RBAC</span>
            </div>
            <p className="text-[13.5px] text-charcoal leading-relaxed">
              HS256 JWT tokens with bcrypt password hashing and granular role enforcement (Admin, Analyst, Viewer).
            </p>
          </div>

          <div className="bg-cream-100 p-4 rounded-xl border border-cream-200 space-y-1.5">
            <div className="flex items-center gap-2 text-espresso-900 font-bold text-[15px]">
              <CheckCircle2 className="w-4 h-4 text-soc-success" />
              <span>Automated Secret Redaction</span>
            </div>
            <p className="text-[13.5px] text-charcoal leading-relaxed">
              Audit logging pipeline redacts API keys, JWT tokens, and sensitive system passwords before database persistence.
            </p>
          </div>
        </div>
      </div>

      {/* Engine & Database Telemetry */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Database Configuration */}
        <div className="cream-card p-6 space-y-4">
          <div className="flex items-center gap-2.5 text-espresso-900 font-extrabold text-[17px] border-b border-cream-200 pb-3">
            <Database className="w-5 h-5 text-caramel" />
            <span>Database Backend</span>
          </div>

          <div className="space-y-3 text-[14px]">
            <div className="flex items-center justify-between">
              <span className="text-charcoal-muted">Active ORM Engine:</span>
              <span className="font-bold text-espresso-900">SQLAlchemy 2.0</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-charcoal-muted">Persistence Mode:</span>
              <span className="font-mono bg-cream-200 px-2 py-0.5 rounded text-espresso-900 font-bold">
                SQLite / PostgreSQL Ready
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-charcoal-muted">Schema Auto-Seeding:</span>
              <span className="text-soc-success font-bold">Enabled</span>
            </div>
          </div>
        </div>

        {/* AI Model Configuration */}
        <div className="cream-card p-6 space-y-4">
          <div className="flex items-center gap-2.5 text-espresso-900 font-extrabold text-[17px] border-b border-cream-200 pb-3">
            <Cpu className="w-5 h-5 text-caramel" />
            <span>AI Reasoning Engine</span>
          </div>

          <div className="space-y-3 text-[14px]">
            <div className="flex items-center justify-between">
              <span className="text-charcoal-muted">Primary LLM Provider:</span>
              <span className="font-bold text-espresso-900">Google Gemini</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-charcoal-muted">Target Model:</span>
              <span className="font-mono bg-caramel-light px-2 py-0.5 rounded text-copper font-bold">
                gemini-2.5-flash
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-charcoal-muted">Deterministic Fallback:</span>
              <span className="text-soc-success font-bold">Active (Zero-Downtime)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
