import React from 'react';
import { Severity } from '../types';

interface SeverityBadgeProps {
  severity: Severity | string;
  size?: 'sm' | 'md' | 'lg';
  showDot?: boolean;
}

export const SeverityBadge: React.FC<SeverityBadgeProps> = ({
  severity,
  size = 'md',
  showDot = true,
}) => {
  const norm = (severity || 'MEDIUM').toUpperCase();

  const styles: Record<string, { bg: string; text: string; border: string; dot: string }> = {
    CRITICAL: {
      bg: 'bg-[#FDF2F2]',
      text: 'text-[#991B1B]',
      border: 'border-[#F87171]/40',
      dot: 'bg-[#DC2626]',
    },
    HIGH: {
      bg: 'bg-[#FFF7ED]',
      text: 'text-[#C2410C]',
      border: 'border-[#FB923C]/40',
      dot: 'bg-[#EA580C]',
    },
    MEDIUM: {
      bg: 'bg-[#FEFCE8]',
      text: 'text-[#A16207]',
      border: 'border-[#FACC15]/40',
      dot: 'bg-[#CA8A04]',
    },
    LOW: {
      bg: 'bg-[#F0FDF4]',
      text: 'text-[#166534]',
      border: 'border-[#4ADE80]/40',
      dot: 'bg-[#16A34A]',
    },
  };

  const current = styles[norm] || styles.MEDIUM;

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-[12px] font-bold',
    md: 'px-2.5 py-1 text-[13.5px] font-bold',
    lg: 'px-3.5 py-1.5 text-[15px] font-extrabold',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-lg border uppercase tracking-wider font-mono shadow-xs ${current.bg} ${current.text} ${current.border} ${sizeClasses[size]}`}
    >
      {showDot && <span className={`w-2 h-2 rounded-full ${current.dot}`} />}
      <span>{norm}</span>
    </span>
  );
};
