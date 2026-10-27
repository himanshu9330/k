import React, { useEffect, useState } from 'react';
import {
  Globe2,
  Search,
  ShieldAlert,
  ShieldCheck,
  Hash,
  Link2,
  Cpu,
  Layers,
  Info,
  ExternalLink,
  RefreshCw,
} from 'lucide-react';
import { api } from '../services/api';
import { ThreatEnrichment, ThreatIndicator } from '../types';
import { SeverityBadge } from '../components/SeverityBadge';
import { useToast } from '../components/Toast';

export const ThreatIntelPage: React.FC = () => {
  const { showToast } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [enrichment, setEnrichment] = useState<ThreatEnrichment | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [activeIndicators, setActiveIndicators] = useState<ThreatIndicator[]>([]);
  const [isLoadingIndicators, setIsLoadingIndicators] = useState(true);
  const [filterType, setFilterType] = useState<string>('ALL');

  const loadIndicators = async () => {
    setIsLoadingIndicators(true);
    try {
      const data = await api.getThreatIndicators(filterType !== 'ALL' ? filterType : undefined);
      setActiveIndicators(data);
    } catch (err: any) {
      console.error(err);
    } finally {
      setIsLoadingIndicators(false);
    }
  };

  useEffect(() => {
    loadIndicators();
  }, [filterType]);

  const handleSearch = async (valToSearch?: string) => {
    const val = (valToSearch || searchQuery).trim();
    if (!val) return;

    setIsSearching(true);
    try {
      const data = await api.lookupThreat(val);
      setEnrichment(data);
      showToast('success', 'Enrichment Complete', `Threat intelligence profile resolved for ${val}.`);
    } catch (err: any) {
      showToast('error', 'Enrichment Failed', err.message);
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-16">
      {/* Header */}
      <div>
        <h1 className="text-[28px] md:text-[32px] font-black text-espresso-900 tracking-tight">
          Threat Intelligence & IOC Enrichment
        </h1>
        <p className="text-[15px] text-charcoal-muted mt-1">
          Investigate adversary IPs, domain infrastructure, malware hashes, and malicious URLs with transparent provenance scoring.
        </p>
      </div>

      {/* Interactive IOC Lookup Search Bar */}
      <div className="cream-card p-6 shadow-card">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch();
          }}
          className="flex flex-col sm:flex-row items-center gap-3"
        >
          <div className="relative flex-1 w-full">
            <Search className="w-5 h-5 absolute left-4 top-3.5 text-charcoal-muted" />
            <input
              type="text"
              required
              placeholder="Enter IP (192.168.1.15), domain (c2.darkshadow-botnet.net), MD5/SHA256 hash, or URL..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 rounded-xl border border-cream-300 bg-cream-100 text-espresso-900 font-mono font-medium text-[15px] focus:outline-none focus:border-caramel"
            />
          </div>
          <button
            type="submit"
            disabled={isSearching || !searchQuery.trim()}
            className="w-full sm:w-auto px-6 py-3 rounded-xl bg-espresso-900 hover:bg-espresso-800 text-cream-100 font-extrabold text-[15px] shadow-sm disabled:opacity-50 transition-all flex items-center justify-center gap-2 shrink-0"
          >
            <Cpu className="w-4 h-4 text-caramel" />
            <span>{isSearching ? 'Querying Intel...' : 'Enrich Indicator'}</span>
          </button>
        </form>

        {/* Example Quick Links */}
        <div className="mt-3.5 flex flex-wrap items-center gap-2 text-[13px] text-charcoal-muted">
          <span className="font-bold uppercase tracking-wider text-[11.5px]">Try Quick IOC:</span>
          {['192.168.1.15', '203.0.113.88', '198.51.100.44', 'c2.darkshadow-botnet.net', '44d88612fea8a8f36de82e1278abb02f'].map((demoIoc) => (
            <button
              key={demoIoc}
              onClick={() => {
                setSearchQuery(demoIoc);
                handleSearch(demoIoc);
              }}
              className="px-2.5 py-1 rounded bg-cream-200 hover:bg-cream-300 font-mono font-bold text-[12px] text-espresso-900 border border-cream-300 transition-colors"
            >
              {demoIoc}
            </button>
          ))}
        </div>
      </div>

      {/* Enrichment Results Card */}
      {enrichment && (
        <div className="cream-card p-6 border-l-6 border-l-copper animate-in fade-in zoom-in-95 space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-cream-200 pb-4">
            <div>
              <div className="flex items-center gap-2.5 mb-1.5">
                <span className="px-2.5 py-0.5 rounded bg-espresso-900 text-cream-100 font-mono font-bold text-[12px]">
                  {enrichment.indicator_type}
                </span>
                <SeverityBadge severity={enrichment.risk_level} size="sm" />
                <span className="text-[13px] text-charcoal-muted font-mono font-semibold">
                  Source: {enrichment.source_provenance}
                </span>
              </div>
              <h2 className="font-mono font-black text-[22px] md:text-[26px] text-espresso-900 break-all select-all">
                {enrichment.indicator}
              </h2>
              <p className="text-[15px] font-bold text-copper mt-0.5">
                {enrichment.threat_classification}
              </p>
            </div>

            <div className="bg-cream-100 p-4 rounded-xl border border-cream-200 text-right shrink-0">
              <span className="text-[12px] font-bold text-charcoal-muted uppercase tracking-wider block">
                Reputation Score
              </span>
              <span className="text-[32px] font-black text-soc-danger leading-tight">
                {enrichment.reputation_score}
                <span className="text-[14px] text-charcoal-muted font-normal">/100</span>
              </span>
              <span className="block text-[12px] font-bold text-charcoal-muted uppercase">
                {enrichment.is_malicious ? '🔴 High Malice Probability' : '🟢 Benign Indicator'}
              </span>
            </div>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-cream-100 p-4 rounded-xl border border-cream-200 space-y-2">
              <p className="text-[12px] font-bold text-charcoal-muted uppercase tracking-wider">
                Geographic & ASN Origin
              </p>
              <p className="text-[15px] font-bold text-espresso-900">
                {enrichment.country || 'Internal / Unresolved'}
              </p>
              <p className="text-[13px] font-mono text-charcoal-muted">
                {enrichment.asn || 'Standard Transit Route'}
              </p>
            </div>

            <div className="bg-cream-100 p-4 rounded-xl border border-cream-200 space-y-2">
              <p className="text-[12px] font-bold text-charcoal-muted uppercase tracking-wider">
                Attribution & Actor Group
              </p>
              <p className="text-[15px] font-bold text-espresso-900">
                {enrichment.actor_group || 'Unattributed / Botnet Node'}
              </p>
              <p className="text-[13px] text-charcoal-muted">
                Confidence Rating: {Math.round(enrichment.confidence * 100)}%
              </p>
            </div>

            <div className="bg-cream-100 p-4 rounded-xl border border-cream-200 space-y-2">
              <p className="text-[12px] font-bold text-charcoal-muted uppercase tracking-wider">
                Associated MITRE Techniques
              </p>
              <div className="flex flex-wrap gap-1.5 mt-1">
                {enrichment.mitre_techniques?.map((t, i) => (
                  <span key={i} className="px-2 py-0.5 rounded bg-espresso-800 text-cream-100 font-mono font-bold text-[12px]">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Mitigation Strategy */}
          <div className="bg-cream-200/80 p-4 rounded-xl border border-cream-300">
            <h4 className="font-extrabold text-[14px] text-espresso-900 uppercase tracking-wider mb-1">
              Recommended Defensive Containment
            </h4>
            <p className="text-[14.5px] text-charcoal leading-relaxed">
              {enrichment.recommended_mitigation}
            </p>
          </div>
        </div>
      )}

      {/* Active Incident IOCs Library */}
      <div className="cream-card p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-cream-200 pb-4 mb-5">
          <div>
            <h3 className="text-[20px] font-black text-espresso-900">
              Active IOC Intelligence Library
            </h3>
            <p className="text-[14px] text-charcoal-muted mt-0.5">
              Curated and observed indicators across live security telemetry
            </p>
          </div>

          {/* Type Filter */}
          <div className="flex items-center gap-2">
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-3.5 py-2 rounded-xl border border-cream-300 bg-cream-100 text-espresso-900 font-bold text-[13.5px] focus:outline-none focus:border-caramel"
            >
              <option value="ALL">All Indicator Types</option>
              <option value="IP">IP Addresses</option>
              <option value="DOMAIN">Domains</option>
              <option value="HASH_MD5">MD5 / SHA256 Hashes</option>
              <option value="URL">URLs</option>
            </select>
          </div>
        </div>

        {isLoadingIndicators ? (
          <div className="p-8 text-center">
            <div className="w-8 h-8 rounded-full border-3 border-espresso-800 border-t-caramel animate-spin mx-auto" />
            <p className="mt-2 text-[14px] font-bold text-espresso-900">Loading indicators...</p>
          </div>
        ) : activeIndicators.length === 0 ? (
          <div className="p-8 text-center text-charcoal-muted text-[14.5px]">
            No threat indicators recorded matching the current filter.
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {activeIndicators.map((ioc) => (
              <div
                key={ioc.id}
                onClick={() => {
                  setSearchQuery(ioc.value);
                  handleSearch(ioc.value);
                }}
                className="bg-cream-100 p-4 rounded-xl border border-cream-200 hover:border-caramel transition-all cursor-pointer space-y-2 shadow-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="px-2 py-0.5 rounded bg-cream-200 text-espresso-900 font-mono text-[11.5px] font-bold">
                    {ioc.indicator_type}
                  </span>
                  <SeverityBadge severity={ioc.risk_level} size="sm" />
                </div>
                <p className="font-mono font-bold text-[14.5px] text-espresso-900 break-all">
                  {ioc.value}
                </p>
                <p className="text-[12.5px] text-charcoal-muted">
                  {ioc.threat_type}
                </p>
                <div className="pt-2 border-t border-cream-200 flex items-center justify-between text-[12px]">
                  <span className="text-charcoal-muted">Reputation: <strong className="text-soc-danger">{ioc.reputation_score}/100</strong></span>
                  <span className="text-caramel font-bold">Enrich →</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
