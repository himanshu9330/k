import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  accentColor?: 'espresso' | 'caramel' | 'danger' | 'warning' | 'success';
}

export const StatsCard: React.FC<StatsCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  accentColor = 'espresso',
}) => {
  const accentStyles = {
    espresso: 'bg-cream-200 text-espresso-900 border-cream-300',
    caramel: 'bg-caramel-light text-copper border-caramel/30',
    danger: 'bg-red-50 text-soc-danger border-red-200',
    warning: 'bg-amber-50 text-soc-warning border-amber-200',
    success: 'bg-emerald-50 text-soc-success border-emerald-200',
  };

  return (
    <div className="cream-card p-6 flex flex-col justify-between hover:shadow-elevated transition-shadow duration-200">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[13.5px] font-bold text-charcoal-muted uppercase tracking-wider">
            {title}
          </p>
          <p className="text-[32px] font-black text-espresso-900 mt-1 leading-tight tracking-tight">
            {value}
          </p>
        </div>
        <div className={`p-3 rounded-xl border ${accentStyles[accentColor]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>

      {(subtitle || trend) && (
        <div className="mt-4 pt-3 border-t border-cream-200 flex items-center justify-between text-[13.5px]">
          {subtitle && <span className="text-charcoal-muted font-medium">{subtitle}</span>}
          {trend && (
            <span
              className={`font-bold flex items-center gap-1 ${
                trend.isPositive ? 'text-soc-success' : 'text-soc-danger'
              }`}
            >
              {trend.value}
            </span>
          )}
        </div>
      )}
    </div>
  );
};
