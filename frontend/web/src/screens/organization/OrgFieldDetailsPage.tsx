import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { liveWorkspaceApi } from '../../services/liveWorkspaceApi';
import { useDemoMode } from '../../context/DemoModeContext';
import { getDemoFieldByReference, isDemoReference } from '../../services/demoWorkspaceAdapters';
import { Field, Case } from '../../types';
import { EvidenceViewer } from '../../components/shared/EvidenceViewer';
import { SafetyBanner } from '../../components/shared/SafetyBanner';
import { SeverityBadge } from '../../components/shared/RoleBadge';
import { ArrowLeft, FileText, CheckCircle2, Database, Sprout } from 'lucide-react';

export const OrgFieldDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { enabled: isDemoMode, workspace, setEnabled: setDemoMode } = useDemoMode();
  const [field, setField] = useState<Field | null>(null);
  const [activeCase, setActiveCase] = useState<Case | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchFieldData = async () => {
      if (!id) throw new Error('A field identifier is required.');
      setLoading(true); setError('');
      if ((isDemoMode || isDemoReference(id)) && workspace) {
        const demoField = getDemoFieldByReference(workspace, id);
        if (demoField) {
          setField(demoField);
          setActiveCase(null);
          setLoading(false);
          return;
        }
      }
      const [f, c] = await Promise.all([liveWorkspaceApi.getFieldById(id), liveWorkspaceApi.getLatestFieldCase(id)]);
      setField(f);
      setActiveCase(c);
      setLoading(false);
    };
    fetchFieldData().catch(e => { setError(e.message); setLoading(false); });
  }, [id, isDemoMode, workspace]);

  if (loading) {
    return <div className="p-8 text-center text-xs text-muted-leaf">Loading field intelligence profile...</div>;
  }

  if (error) return <div className="message error" role="alert">{error}</div>;
  if (!field) return <div className="farmer-workspace"><p>Field not found.</p><Link className="text-action" to="/organization/dashboard">Return to field overview</Link></div>;

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

        {activeCase && (
          <Link
            to="#evidence"
            className="px-4 py-2.5 bg-field-ink text-white font-bold text-xs rounded-xl hover:bg-opacity-90 transition flex items-center gap-2 shadow-xs"
          >
            <FileText size={14} className="text-lime-signal" />
            <span>View Latest Crop Report</span>
          </Link>
        )}
      </div>

      {(isDemoMode || isDemoReference(field.id)) && (
        <section className="rounded-2xl border border-amber-200 bg-amber-50 p-4 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2.5 text-amber-900 font-semibold">
            <Database size={17} className="shrink-0 text-amber-800" />
            <span>Demo workspace field plot record. No simulated crop scan or AI analysis has been fabricated.</span>
          </div>
          <button className="action secondary text-xs py-1.5 px-3" onClick={() => setDemoMode(false)}>
            Switch to Live workspace
          </button>
        </section>
      )}

      <SafetyBanner />

      {/* Field Health Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
        <div className="p-4 bg-pure-surface rounded-2xl border border-structural shadow-xs">
          <span className="text-[10px] text-muted-leaf uppercase font-mono block">Health Score</span>
          <span className="font-extrabold text-xl text-field-ink font-mono">Not yet validated</span>
        </div>
        <div className="p-4 bg-pure-surface rounded-2xl border border-structural shadow-xs">
          <span className="text-[10px] text-muted-leaf uppercase font-mono block">Health Status</span>
          <span className="font-bold text-xs text-warning-orange block mt-1">{field.healthStatus}</span>
        </div>
        <div className="p-4 bg-pure-surface rounded-2xl border border-structural shadow-xs">
          <span className="text-[10px] text-muted-leaf uppercase font-mono block">Primary Disease</span>
          <span className="font-bold text-xs text-muted-leaf block mt-1">{field.primaryDiseaseSignal || 'No scan recorded'}</span>
        </div>
        <div className="p-4 bg-pure-surface rounded-2xl border border-structural shadow-xs">
          <span className="text-[10px] text-muted-leaf uppercase font-mono block">Total Scans</span>
          <span className="font-extrabold text-xl text-field-ink font-mono">{field.totalScansCount} Scans</span>
        </div>
      </div>

      {activeCase ? (
        <>
          {/* Integrated Shared Evidence Viewer */}
          <div className="space-y-2">
            <h3 className="font-bold text-xs text-field-ink uppercase font-mono tracking-wider">
              Latest Scan Multi-Frame Evidence Analysis
            </h3>
            <EvidenceViewer
              videoUrl={activeCase.videoUrl}
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
                    <th className="p-3 font-bold">Agronomist Verified</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-structural">
                  {field.scanHistory.map((s) => (
                    <tr key={s.id} className="hover:bg-field-canvas/60 transition">
                      <td className="p-3 font-mono text-field-ink">{new Date(s.date).toLocaleString()}</td>
                      <td className="p-3 font-bold text-field-ink">{s.diseaseIndication}</td>
                      <td className="p-3 font-mono">{s.confidence == null ? 'Not available' : `${s.confidence}%`}</td>
                      <td className="p-3">
                        <SeverityBadge severity={s.severity} />
                      </td>
                      <td className="p-3">
                        {s.verifiedByAgronomist ? (
                          <span className="inline-flex items-center gap-1 text-emerald-700 font-bold">
                            <CheckCircle2 size={14} /> Verified
                          </span>
                        ) : (
                          <span className="text-muted-leaf font-mono">No review recorded</span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      ) : (
        <section className="bg-pure-surface border border-structural rounded-3xl p-8 text-xs space-y-3">
          <div className="flex items-center gap-3 text-field-ink">
            <Sprout size={24} className="text-muted-leaf" />
            <h3 className="font-bold text-base">No Scans Recorded</h3>
          </div>
          <p className="text-muted-leaf max-w-2xl leading-relaxed">
            No processed video scans or AI assessments exist for <strong>{field.name}</strong>.
            {isDemoMode || isDemoReference(field.id)
              ? ' Shared demonstration fields include spatial registration records without simulated disease findings.'
              : ' Upload a video walk-through in Live Mode to generate an AI assessment for this field plot.'}
          </p>
          <div className="pt-2">
            <Link to="/organization/dashboard" className="text-action text-xs font-bold">
              ← Return to field overview
            </Link>
          </div>
        </section>
      )}
    </div>
  );
};
