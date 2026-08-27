import React, { useState, useEffect } from 'react';
import { mockApi } from '../../services/mockApi';
import { GeneratedReport } from '../../types';
import { FileBarChart, Download, Plus, Loader2, Sparkles, Filter } from 'lucide-react';

export const OrgReportsPage: React.FC = () => {
  const [reports, setReports] = useState<GeneratedReport[]>([]);
  const [reportType, setReportType] = useState<GeneratedReport['type']>('disease_outbreak');
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    mockApi.getReports().then(setReports);
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    const titles: Record<GeneratedReport['type'], string> = {
      disease_outbreak: 'Latur & Amravati Soybean Outbreak Heat Map Summary',
      fpo_health: 'Shinde FPO Monthly Cluster Crop Health Index',
      agronomist_sla: 'Agronomist Field Response SLA & Verification Audit',
      field_risk: 'High Risk Field Plot Escalation Register',
    };
    const rep = await mockApi.generateReport(titles[reportType], reportType);
    setReports((prev) => [rep, ...prev]);
    setGenerating(false);
  };

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

      {/* Report Generator Controls */}
      <div className="bg-pure-surface border border-structural p-6 rounded-3xl shadow-xs space-y-4 text-xs">
        <h3 className="font-bold text-sm text-field-ink">Generate New Intelligence Report</h3>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="block font-bold mb-1">Report Category</label>
            <select
              value={reportType}
              onChange={(e) => setReportType(e.target.value as any)}
              className="w-full p-2.5 rounded-xl border border-structural bg-field-canvas text-xs outline-none font-medium"
            >
              <option value="disease_outbreak">Disease Outbreak Heat Map Summary</option>
              <option value="fpo_health">FPO Cluster Crop Health Index</option>
              <option value="agronomist_sla">Agronomist Response SLA Audit</option>
              <option value="field_risk font-medium">High Risk Field Plot Escalation Register</option>
            </select>
          </div>

          <div>
            <label className="block font-bold mb-1">Date Range</label>
            <select className="w-full p-2.5 rounded-xl border border-structural bg-field-canvas text-xs outline-none font-medium">
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
              <option value="ytd">Year To Date</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="w-full py-2.5 bg-field-ink text-white font-bold rounded-xl hover:bg-opacity-90 transition flex items-center justify-center gap-2 shadow-xs"
            >
              {generating ? (
                <Loader2 size={16} className="animate-spin text-lime-signal" />
              ) : (
                <Sparkles size={16} className="text-lime-signal" />
              )}
              <span>{generating ? 'Generating Report...' : 'Generate report'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Report List */}
      <div className="bg-pure-surface border border-structural p-6 rounded-3xl shadow-xs space-y-4 text-xs">
        <h3 className="font-bold text-sm text-field-ink">Recently Generated Intelligence Exports</h3>
        {reports.length === 0 ? (
          <div className="p-8 text-center text-muted-leaf">No reports generated yet.</div>
        ) : (
          <div className="space-y-3">
            {reports.map((rep) => (
              <div
                key={rep.id}
                className="p-4 bg-field-canvas rounded-2xl border border-structural flex items-center justify-between gap-4"
              >
                <div>
                  <p className="font-bold text-field-ink">{rep.title}</p>
                  <p className="text-[11px] text-muted-leaf">
                    Generated {rep.generatedAt} • Format: <strong className="font-mono">{rep.format}</strong> ({rep.size})
                  </p>
                </div>
                <button
                  onClick={() => alert(`Exporting ${rep.title}`)}
                  className="px-3.5 py-2 bg-pure-surface border border-structural font-bold text-field-ink rounded-xl hover:bg-gray-200 transition flex items-center gap-1.5"
                >
                  <Download size={14} /> Download Export
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
