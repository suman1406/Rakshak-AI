import React from 'react';
import { AlertCircle, ShieldCheck } from 'lucide-react';

interface SafetyBannerProps {
  compact?: boolean;
  className?: string;
}

export const SafetyBanner: React.FC<SafetyBannerProps> = ({ compact = false, className = '' }) => {
  if (compact) {
    return (
      <div className={`inline-flex items-center gap-1.5 px-3 py-1 bg-soft-healthy text-soft-healthy border border-emerald-200 text-xs font-medium rounded-full ${className}`}>
        <ShieldCheck size={14} className="shrink-0 text-emerald-700" />
        <span>AI indication, not confirmed diagnosis</span>
      </div>
    );
  }

  return (
    <div className={`bg-amber-50/80 border border-amber-200/80 rounded-xl p-3.5 flex items-start gap-3 text-xs text-amber-900 ${className}`}>
      <AlertCircle size={16} className="text-amber-700 shrink-0 mt-0.5" />
      <div>
        <span className="font-semibold text-amber-950">Safety Disclaimer:</span> AI indication, not confirmed diagnosis. All disease predictions represent probabilistic machine vision signals based on visual evidence frames and require verification by a qualified agronomist before applying chemical treatments.
      </div>
    </div>
  );
};
