import React from 'react';
import { FileBarChart } from 'lucide-react';

export const AgronomistReportsPage: React.FC = () => {
  return (
    <div className="space-y-6 font-sans">
      <div className="bg-pure-surface border border-structural p-6 rounded-3xl shadow-2xs space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="p-1.5 bg-field-ink text-lime-signal rounded-lg">
              <FileBarChart size={18} />
            </span>
            <h1 className="text-2xl font-extrabold text-field-ink">Agronomist Audit Reports</h1>
          </div>
        </div>
        <p className="text-xs text-muted-leaf">Exportable logs for verification SLAs and disease trend audits</p>
      </div>

      <div className="bg-pure-surface border border-structural p-6 rounded-3xl shadow-xs space-y-4">
        <h3 className="font-bold text-xs text-field-ink">Report API unavailable</h3>
        <p className="text-xs text-muted-leaf">The backend has no agronomist SLA export endpoint. Demo reports and fake downloads were removed rather than presenting them as live records.</p>
      </div>
    </div>
  );
};
