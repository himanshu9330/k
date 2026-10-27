import React from 'react';
import { ThreatIndicator } from '../types';
import { Globe, Hash, Link2, ShieldAlert, Cpu } from 'lucide-react';
import { SeverityBadge } from './SeverityBadge';

interface ThreatIndicatorCardProps {
  indicator: ThreatIndicator;
  onEnrich?: (val: string) => void;
}

export const ThreatIndicatorCard: React.FC<ThreatIndicatorCardProps> = ({
  indicator,
  onEnrich,
}) => {
  const getTypeIcon = (type: string) => {
    switch (type.toUpperCase()) {
      case 'IP':
        return <Globe className="w-4 h-4 text-caramel" />;
      case 'DOMAIN':
        return <Globe className="w-4 h-4 text-copper" />;
      case 'HASH_MD5':
      case 'HASH_SHA256':
        return <Hash className="w-4 h-4 text-espresso-700" />;
      case 'URL':
        return <Link2 className="w-4 h-4 text-blue-600" />;
      default:
        return <ShieldAlert className="w-4 h-4 text-amber-600" />;
    }
  };

  return (
    <div className="bg-cream-100 p-4 rounded-xl border border-cream-200 shadow-xs flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between gap-2 mb-2">
          <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded bg-cream-200 text-espresso-900 font-mono text-[12px] font-bold">
            {getTypeIcon(indicator.indicator_type)}
            <span>{indicator.indicator_type}</span>
          </div>
          <SeverityBadge severity={indicator.risk_level} size="sm" />
        </div>

        <div className="font-mono font-bold text-[15px] text-espresso-900 break-all select-all">
          {indicator.value}
        </div>

        <p className="text-[13px] text-charcoal-muted mt-1">
          {indicator.threat_type}
        </p>

        {indicator.country && indicator.country !== 'Reserved / Internal' && (
          <div className="mt-2.5 flex flex-wrap gap-1.5 text-[12px]">
            <span className="px-2 py-0.5 rounded bg-cream-200 text-charcoal font-medium">
              📍 {indicator.country}
            </span>
            {indicator.asn && (
              <span className="px-2 py-0.5 rounded bg-cream-200 text-charcoal font-mono">
                {indicator.asn}
              </span>
            )}
          </div>
        )}
      </div>

      <div className="mt-4 pt-3 border-t border-cream-200 flex items-center justify-between">
        <div className="text-[12.5px] font-medium text-charcoal-muted">
          Reputation: <strong className="text-soc-danger">{indicator.reputation_score}/100</strong>
        </div>
        {onEnrich && (
          <button
            onClick={() => onEnrich(indicator.value)}
            className="text-[12.5px] font-bold text-caramel hover:text-copper underline"
          >
            Enrich IOC →
          </button>
        )}
      </div>
    </div>
  );
};
