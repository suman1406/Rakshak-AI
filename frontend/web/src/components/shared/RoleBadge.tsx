import React from 'react';
import { UserRole, SeverityLevel, ReviewStatus } from '../../types';
import { UserCheck, Shield, Sprout, AlertTriangle, CheckCircle, Clock, Search } from 'lucide-react';

export const RoleBadge: React.FC<{ role: UserRole; className?: string }> = ({ role, className = '' }) => {
  const configs: Record<UserRole, { label: string; bg: string; text: string; icon: React.ReactNode }> = {
    farmer: {
      label: 'Farmer',
      bg: 'bg-emerald-50 border-emerald-200',
      text: 'text-emerald-800',
      icon: <Sprout size={12} className="text-emerald-600" />,
    },
    agronomist: {
      label: 'Agronomist',
      bg: 'bg-blue-50 border-blue-200',
      text: 'text-blue-800',
      icon: <UserCheck size={12} className="text-blue-600" />,
    },
    org_admin: {
      label: 'Organization Admin',
      bg: 'bg-amber-50 border-amber-200',
      text: 'text-amber-800',
      icon: <Shield size={12} className="text-amber-600" />,
    },
  };

  const config = configs[role] || configs.farmer;

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border text-xs font-semibold ${config.bg} ${config.text} ${className}`}>
      {config.icon}
      {config.label}
    </span>
  );
};

export const SeverityBadge: React.FC<{ severity: SeverityLevel; className?: string }> = ({ severity, className = '' }) => {
  const configs: Record<SeverityLevel, { bg: string; text: string }> = {
    Healthy: { bg: 'bg-soft-healthy border-emerald-200', text: 'text-soft-healthy' },
    Early: { bg: 'bg-amber-50 border-amber-200', text: 'text-amber-800' },
    Moderate: { bg: 'bg-orange-50 border-orange-200', text: 'text-warning-orange' },
    Severe: { bg: 'bg-red-50 border-red-200', text: 'text-alert-red' },
    Uncertain: { bg: 'bg-gray-100 border-gray-300', text: 'text-muted-leaf' },
  };

  const config = configs[severity] || configs.Uncertain;

  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-md border text-xs font-semibold ${config.bg} ${config.text} ${className}`}>
      {severity}
    </span>
  );
};

export const ReviewStatusBadge: React.FC<{ status: ReviewStatus; className?: string }> = ({ status, className = '' }) => {
  const configs: Record<ReviewStatus, { label: string; bg: string; text: string; icon: React.ReactNode }> = {
    awaiting_review: {
      label: 'Awaiting Review',
      bg: 'bg-amber-50 border-amber-200',
      text: 'text-amber-800',
      icon: <Clock size={12} />,
    },
    reviewed: {
      label: 'Verified by Agronomist',
      bg: 'bg-emerald-50 border-emerald-200',
      text: 'text-emerald-800',
      icon: <CheckCircle size={12} />,
    },
    needs_inspection: {
      label: 'Needs Field Inspection',
      bg: 'bg-purple-50 border-purple-200',
      text: 'text-purple-800',
      icon: <Search size={12} />,
    },
  };

  const config = configs[status] || configs.awaiting_review;

  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full border text-xs font-medium ${config.bg} ${config.text} ${className}`}>
      {config.icon}
      {config.label}
    </span>
  );
};
