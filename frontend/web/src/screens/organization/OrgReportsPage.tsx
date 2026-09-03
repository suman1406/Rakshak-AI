import React from 'react';
import { FileBarChart } from 'lucide-react';

export const OrgReportsPage: React.FC = () => {
  return (
    <div className="space-y-6 font-sans">
      <div className="bg-pure-surface border border-structural p-6 rounded-3xl shadow-2xs space-y-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="p-1.5 bg-field-ink text-lime-signal rounded-lg">
              <FileBarChart size={18} />
            </span>
            <h1 className="text-2xl font-extrabold text-field-ink">Organization Intelligence Reports</h1>
          </div>
        </div>
        <p className="text-xs text-muted-leaf">Generate exportable PDF/CSV reports for FPO management and regional authorities</p>
      </div>

      <div className="bg-pure-surface border border-structural p-6 rounded-3xl shadow-xs space-y-4 text-xs">
        <h3 className="font-bold text-sm text-field-ink">Report exports are not available yet</h3>
        <p className="text-muted-leaf leading-relaxed">The current backend exposes dashboard and drill-down analytics, but it does not provide report creation, storage, or download endpoints. Fixture reports have been removed so this screen does not claim that an export was generated.</p>
      </div>
    </div>
  );
};
