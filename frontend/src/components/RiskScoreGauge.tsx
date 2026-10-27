import React from 'react';
import { RiskAssessment } from '../types';
import { ShieldAlert, Info } from 'lucide-react';

interface RiskScoreGaugeProps {
  score: number;
  level: string;
  assessment?: RiskAssessment;
}

export const RiskScoreGauge: React.FC<RiskScoreGaugeProps> = ({
  score,
  level,
  assessment,
}) => {
  const getRiskColor = (s: number) => {
    if (s >= 80) return { text: 'text-[#DC2626]', bg: 'bg-[#DC2626]', stroke: '#DC2626', badge: 'bg-red-100 text-red-800' };
    if (s >= 60) return { text: 'text-[#EA580C]', bg: 'bg-[#EA580C]', stroke: '#EA580C', badge: 'bg-orange-100 text-orange-800' };
    if (s >= 30) return { text: 'text-[#D97706]', bg: 'bg-[#D97706]', stroke: '#D97706', badge: 'bg-amber-100 text-amber-800' };
    return { text: 'text-[#16A34A]', bg: 'bg-[#16A34A]', stroke: '#16A34A', badge: 'bg-emerald-100 text-emerald-800' };
  };

  const colors = getRiskColor(score);
  const strokeDashoffset = 283 - (283 * score) / 100;

  return (
    <div className="cream-card p-6 flex flex-col">
      <div className="flex items-center justify-between border-b border-cream-200 pb-4">
        <div>
          <h3 className="text-[18px] font-extrabold text-espresso-900 flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-caramel" />
            Deterministic Risk Score
          </h3>
          <p className="text-[13.5px] text-charcoal-muted mt-0.5">
            Multi-factor mathematical evaluation (0–100 scale)
          </p>
        </div>
        <span className={`px-3 py-1 rounded-full text-[13px] font-extrabold tracking-wider ${colors.badge}`}>
          {level.toUpperCase()} RISK
        </span>
      </div>

      {/* Radial Gauge Meter */}
      <div className="flex items-center justify-center my-6">
        <div className="relative w-44 h-44 flex items-center justify-center">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
            {/* Background Track */}
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="transparent"
              stroke="#EFE6D8"
              strokeWidth="9"
            />
            {/* Value Progress */}
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="transparent"
              stroke={colors.stroke}
              strokeWidth="9"
              strokeDasharray="283"
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              className="transition-all duration-1000 ease-out"
            />
          </svg>
          <div className="absolute flex flex-col items-center justify-center text-center">
            <span className={`text-[38px] font-black leading-none ${colors.text}`}>
              {score}
            </span>
            <span className="text-[13px] font-bold text-charcoal-muted mt-1 uppercase tracking-wider">
              / 100
            </span>
          </div>
        </div>
      </div>

      {/* Formula & Breakdown */}
      {assessment?.factors && assessment.factors.length > 0 && (
        <div className="mt-2 space-y-3 pt-4 border-t border-cream-200">
          <p className="text-[13px] font-bold text-charcoal-muted uppercase tracking-wider">
            Risk Factor Breakdown
          </p>
          <div className="grid grid-cols-1 gap-2.5">
            {assessment.factors.map((factor, idx) => {
              const pct = Math.round((factor.score / factor.max_score) * 100) || 0;
              return (
                <div key={idx} className="bg-cream-100 p-2.5 rounded-lg border border-cream-200">
                  <div className="flex items-center justify-between text-[13.5px] font-semibold text-espresso-900">
                    <span>{factor.name}</span>
                    <span className="font-mono font-bold">
                      {factor.score} / {factor.max_score} pts
                    </span>
                  </div>
                  <div className="w-full h-2 bg-cream-200 rounded-full mt-1.5 overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        pct > 70 ? 'bg-[#DC2626]' : pct > 40 ? 'bg-caramel' : 'bg-espresso-600'
                      }`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                  {factor.evidence && (
                    <p className="text-[12px] text-charcoal-muted mt-1 font-mono">
                      {factor.evidence}
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Mathematical Formula Explanation */}
      {assessment?.formula && (
        <div className="mt-4 p-3 rounded-lg bg-cream-200/80 border border-cream-300 flex items-start gap-2.5 text-[12.5px] text-charcoal-muted">
          <Info className="w-4 h-4 text-caramel shrink-0 mt-0.5" />
          <div>
            <span className="font-bold text-espresso-900">Scoring Formula: </span>
            <span className="font-mono text-espresso-800">{assessment.formula}</span>
          </div>
        </div>
      )}
    </div>
  );
};
