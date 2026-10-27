import React from 'react';
import { IncidentStatus } from '../types';

interface StatusBadgeProps {
  status: IncidentStatus | string;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const norm = (status || 'OPEN').toUpperCase();

  const styles: Record<string, { bg: string; text: string; border: string; label: string }> = {
    OPEN: {
      bg: 'bg-[#FEF2F2]',
      text: 'text-[#B91C1C]',
      border: 'border-[#FECACA]',
      label: 'Open / Untriaged',
    },
    INVESTIGATING: {
      bg: 'bg-[#EFF6FF]',
      text: 'text-[#1D4ED8]',
      border: 'border-[#BFDBFE]',
      label: 'Investigating',
    },
    CONTAINED: {
      bg: 'bg-[#FFFBEB]',
      text: 'text-[#B45309]',
      border: 'border-[#FDE68A]',
      label: 'Contained',
    },
    RESOLVED: {
      bg: 'bg-[#F0FDF4]',
      text: 'text-[#15803D]',
      border: 'border-[#BBF7D0]',
      label: 'Resolved',
    },
    FALSE_POSITIVE: {
      bg: 'bg-[#F3F4F6]',
      text: 'text-[#4B5563]',
      border: 'border-[#E5E7EB]',
      label: 'False Positive',
    },
  };

  const current = styles[norm] || styles.OPEN;

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-[12px] font-semibold',
    md: 'px-2.5 py-1 text-[13.5px] font-bold',
    lg: 'px-3.5 py-1.5 text-[15px] font-bold',
  };

  return (
    <span
      className={`inline-flex items-center rounded-lg border font-medium ${current.bg} ${current.text} ${current.border} ${sizeClasses[size]}`}
    >
      {current.label}
    </span>
  );
};
