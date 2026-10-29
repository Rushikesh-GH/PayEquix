import React from 'react';

interface StatusBadgeProps {
  status: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status }) => {
  const normalized = status.toUpperCase();

  let styles = 'bg-slate-100 text-slate-700 border-slate-200';
  let dotColor = 'bg-slate-400';

  if (normalized === 'VALID' || normalized === 'APPLIED' || normalized === 'RESOLVED') {
    styles = 'bg-emerald-50 text-emerald-700 border-emerald-200';
    dotColor = 'bg-emerald-500';
  } else if (normalized === 'REVIEW_CANDIDATE' || normalized === 'PENDING_REVIEW' || normalized === 'INVESTIGATED') {
    styles = 'bg-amber-50 text-amber-800 border-amber-200';
    dotColor = 'bg-amber-500';
  } else if (normalized === 'DATA_QUALITY_EXCEPTION' || normalized === 'REJECTED' || normalized === 'CRITICAL') {
    styles = 'bg-rose-50 text-rose-700 border-rose-200';
    dotColor = 'bg-rose-500';
  } else if (normalized === 'APPROVED' || normalized === 'HIGH') {
    styles = 'bg-indigo-50 text-indigo-700 border-indigo-200';
    dotColor = 'bg-indigo-500';
  } else if (normalized === 'DRAFT' || normalized === 'RETURNED_FOR_REVISION') {
    styles = 'bg-slate-100 text-slate-700 border-slate-300';
    dotColor = 'bg-slate-500';
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${styles}`}>
      <span className={`w-1.5 h-1.5 mr-1.5 rounded-full ${dotColor}`}></span>
      {status.replace(/_/g, ' ')}
    </span>
  );
};
