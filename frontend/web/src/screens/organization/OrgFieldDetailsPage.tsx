import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { mockApi } from '../../services/mockApi';
import { Field, Case } from '../../types';
import { EvidenceViewer } from '../../components/shared/EvidenceViewer';
import { SafetyBanner } from '../../components/shared/SafetyBanner';
import { SeverityBadge, ReviewStatusBadge } from '../../components/shared/RoleBadge';
import { ArrowLeft, FileText, CheckCircle2 } from 'lucide-react';

export const OrgFieldDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [field, setField] = useState<Field | null>(null);
  const [activeCase, setActiveCase] = useState<Case | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFieldData = async () => {
      const f = await mockApi.getFieldById(id || 'field-north-plot');
      const c = await mockApi.getCaseById('FASAL-10482');
      setField(f || (await mockApi.getFieldById('field-north-plot')));
      setActiveCase(c);
      setLoading(false);
    };
    fetchFieldData();
  }, [id]);

  if (loading || !field || !activeCase) {
    return <div className="p-8 text-center text-xs text-muted-leaf">Loading field intelligence profile...</div>;
  }

  return (
    <div className="space-y-6 font-sans max-w-5xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link
            to="/organization/dashboard"
            className="p-2 bg-pure-surface border border-structural rounded-xl text-field-ink hover:bg-field-canvas transition"
          >
            <ArrowLeft size={18} />
          </Link>
          <div>
            <h1 className="text-xl font-extrabold text-field-ink">Field Plot: {field.name}</h1>
            <p className="text-xs text-muted-leaf">
              Farm: <strong>{field.farmName}</strong> • Crop: <strong>{field.crop}</strong> ({field.areaAcres} Acres) • {field.fpoName} ({field.district})
            </p>
          </div>
        </div>

        <Link
          to={`/agronomist/cases/${activeCase.id}`}
          className="px-4 py-2.5 bg-field-ink text-white font-bold text-xs rounded-xl hover:bg-opacity-90 transition flex items-center gap-2 shadow-xs"
        >
          <FileText size={14} className="text-lime-signal" />
          <span>View Latest Crop Report</span>
        </Link>
      </div>

      <SafetyBanner />

      {/* Field Health Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
        <div className="p-4 bg-pure-surface rounded-2xl border border-structural shadow-xs">
          <span className="text-[10px] text-muted-leaf uppercase font-mono block">Health Score</span>
          <span className="font-extrabold text-xl text-field-ink font-mono">{field.healthScore}/100</span>
        </div>
        <div className="p-4 bg-pure-surface rounded-2xl border border-structural shadow-xs">
          <span className="text-[10px] text-muted-leaf uppercase font-mono block">Health Status</span>
          <span className="font-bold text-xs text-warning-orange block mt-1">{field.healthStatus}</span>
        </div>
        <div className="p-4 bg-pure-surface rounded-2xl border border-structural shadow-xs">
          <span className="text-[10px] text-muted-leaf uppercase font-mono block">Primary Disease</span>
          <span className="font-bold text-xs text-alert-red block mt-1">{field.primaryDiseaseSignal}</span>
        </div>
        <div className="p-4 bg-pure-surface rounded-2xl border border-structural shadow-xs">
          <span className="text-[10px] text-muted-leaf uppercase font-mono block">Total Scans</span>
          <span className="font-extrabold text-xl text-field-ink font-mono">{field.totalScansCount} Scans</span>
        </div>
      </div>

      {/* Integrated Shared Evidence Viewer */}
      <div className="space-y-2">
        <h3 className="font-bold text-xs text-field-ink uppercase font-mono tracking-wider">
          Latest Scan Multi-Frame Evidence Analysis
        </h3>
        <EvidenceViewer
          evidenceFrames={activeCase.evidenceFrames}
          aiIndication={activeCase.aiIndication}
          confidence={activeCase.confidence}
          caseId={activeCase.id}
        />
      </div>

      {/* Field Scan History Table */}
      <div className="bg-pure-surface border border-structural p-6 rounded-3xl shadow-xs space-y-4 text-xs">
        <h3 className="font-bold text-sm text-field-ink">Field Scan History</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-field-canvas border-b border-structural text-muted-leaf font-mono uppercase text-[10px]">
                <th className="p-3 font-bold">Scan Date</th>
                <th className="p-3 font-bold">Disease Indication</th>
                <th className="p-3 font-bold">Confidence</th>
                <th className="p-3 font-bold">Severity</th>
                <th className="p-3 font-bold">Health Score</th>
                <th className="p-3 font-bold">Agronomist Verified</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-structural">
              {field.scanHistory.map((s) => (
                <tr key={s.id} className="hover:bg-field-canvas/60 transition">
                  <td className="p-3 font-mono text-field-ink">{s.date}</td>
                  <td className="p-3 font-bold text-field-ink">{s.diseaseIndication}</td>
                  <td className="p-3 font-mono">{s.confidence}%</td>
                  <td className="p-3">
                    <SeverityBadge severity={s.severity} />
                  </td>
                  <td className="p-3 font-mono font-bold text-field-ink">{s.healthScore}/100</td>
                  <td className="p-3">
                    {s.verifiedByAgronomist ? (
                      <span className="inline-flex items-center gap-1 text-emerald-700 font-bold">
                        <CheckCircle2 size={14} /> Verified
                      </span>
                    ) : (
                      <span className="text-muted-leaf font-mono">Pending</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
