import React, { useState, useEffect } from 'react';
import { mockApi } from '../../services/mockApi';
import { GeneratedReport } from '../../types';
import { FileBarChart, Download, Plus, Loader2, Sparkles } from 'lucide-react';

export const AgronomistReportsPage: React.FC = () => {
  const [reports, setReports] = useState<GeneratedReport[]>([]);
  const [generating, setGenerating] = useState(false);
  const [downloadedReport, setDownloadedReport] = useState<string | null>(null);

  useEffect(() => {
    mockApi.getReports().then(setReports);
  }, []);

  const handleGenerate = async () => {
    setGenerating(true);
    const rep = await mockApi.generateReport('Agronomist Review Quality & SLA Audit', 'agronomist_sla');
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
            <h1 className="text-2xl font-extrabold text-field-ink">Agronomist Audit Reports</h1>
          </div>
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="px-4 py-2.5 bg-field-ink text-white font-bold text-xs rounded-xl hover:bg-opacity-90 transition shadow-xs flex items-center gap-2"
          >
            {generating ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} className="text-lime-signal" />}
            <span>Generate New SLA Report</span>
          </button>
        </div>
        <p className="text-xs text-muted-leaf">Exportable logs for verification SLAs and disease trend audits</p>
      </div>

      <div className="bg-pure-surface border border-structural p-6 rounded-3xl shadow-xs space-y-4">
        <h3 className="font-bold text-xs text-field-ink">Generated Audit Reports</h3>
        <div className="space-y-3">
          {reports.map((rep) => (
            <div
              key={rep.id}
              className="p-4 bg-field-canvas rounded-2xl border border-structural flex items-center justify-between gap-4 text-xs"
            >
              <div>
                <p className="font-bold text-field-ink">{rep.title}</p>
                <p className="text-[11px] text-muted-leaf">
                  Generated {rep.generatedAt} • {rep.format} ({rep.size})
                </p>
              </div>
              <a
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  setDownloadedReport(rep.id);
                }}
                className="px-3 py-1.5 bg-pure-surface border border-structural font-bold text-field-ink rounded-lg hover:bg-gray-200 transition flex items-center gap-1"
              >
                <Download size={12} /> Download {rep.format}
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
