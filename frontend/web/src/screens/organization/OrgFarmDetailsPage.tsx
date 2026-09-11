import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { liveWorkspaceApi } from '../../services/liveWorkspaceApi';
import { Farm } from '../../types';
import { ArrowLeft, ExternalLink } from 'lucide-react';
import { useDemoMode } from '../../context/DemoModeContext';
import { getDemoFarmByReference, isDemoReference } from '../../services/demoWorkspaceAdapters';

export const OrgFarmDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { enabled: isDemoMode, workspace } = useDemoMode();
  const [farm, setFarm] = useState<Farm | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [revision, setRevision] = useState(0);

  useEffect(() => {
    const fetchFarm = async () => {
      setLoading(true); setError('');
      if (!id) throw new Error('A farm identifier is required.');
      if ((isDemoMode || isDemoReference(id)) && workspace) {
        const demoFarm = getDemoFarmByReference(workspace, id);
        if (demoFarm) {
          setFarm(demoFarm);
          setLoading(false);
          return;
        }
      }
      setFarm(await liveWorkspaceApi.getFarmById(id));
      setLoading(false);
    };
    fetchFarm().catch(e => { setError(e.message); setLoading(false); });
  }, [id, revision, isDemoMode, workspace]);

  if (error) return <div className="message error" role="alert">{error}<button onClick={() => setRevision(value => value + 1)}>Try again</button></div>;

  if (loading || !farm) {
    return <div className="p-8 text-center text-xs text-muted-leaf">Loading farm intelligence profile...</div>;
  }

  return (
    <div className="space-y-6 font-sans max-w-5xl mx-auto">
      {/* Top Header */}
      <div className="flex items-center gap-3">
        <Link
          to="/organization/dashboard"
          className="p-2 bg-pure-surface border border-structural rounded-xl text-field-ink hover:bg-field-canvas transition"
        >
          <ArrowLeft size={18} />
        </Link>
        <div>
          <h1 className="text-xl font-extrabold text-field-ink">{farm.name} Details</h1>
          <p className="text-xs text-muted-leaf">
            Owner: {farm.ownerName} • {farm.fpoName} • {farm.district} District
          </p>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
        <div className="p-4 bg-pure-surface rounded-2xl border border-structural shadow-xs">
          <span className="text-[10px] text-muted-leaf uppercase font-mono block">Health Score</span>
          <span className="font-extrabold text-xl text-field-ink font-mono">Not yet validated</span>
        </div>
        <div className="p-4 bg-pure-surface rounded-2xl border border-structural shadow-xs">
          <span className="text-[10px] text-muted-leaf uppercase font-mono block">Risk Status</span>
          <span className="font-extrabold text-sm text-warning-orange block mt-1">{farm.riskStatus}</span>
        </div>
        <div className="p-4 bg-pure-surface rounded-2xl border border-structural shadow-xs">
          <span className="text-[10px] text-muted-leaf uppercase font-mono block">Total Fields</span>
          <span className="font-extrabold text-xl text-field-ink font-mono">{farm.totalFieldsCount} Plots</span>
        </div>
        <div className="p-4 bg-pure-surface rounded-2xl border border-structural shadow-xs">
          <span className="text-[10px] text-muted-leaf uppercase font-mono block">Disease Signals</span>
          <span className="font-extrabold text-xl text-alert-red font-mono">{farm.diseaseSignalsCount} Active</span>
        </div>
      </div>

      {/* Field List Table */}
      <div className="bg-pure-surface border border-structural rounded-3xl p-6 shadow-xs space-y-4 text-xs">
        <h3 className="font-bold text-sm text-field-ink">Field Plot Register</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-field-canvas border-b border-structural text-muted-leaf font-mono uppercase text-[10px]">
                <th className="p-3 font-bold">Field Name</th>
                <th className="p-3 font-bold">Crop</th>
                <th className="p-3 font-bold">Area</th>
                <th className="p-3 font-bold">Health Score</th>
                <th className="p-3 font-bold">Primary Signal</th>
                <th className="p-3 font-bold text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-structural">
              {farm.fields.map((f) => (
                <tr key={f.id} className="hover:bg-field-canvas/60 transition">
                  <td className="p-3 font-bold text-field-ink">{f.name}</td>
                  <td className="p-3 text-muted-leaf">{f.crop}</td>
                  <td className="p-3 text-muted-leaf font-mono">{f.areaAcres} Acres</td>
                  <td className="p-3 text-field-ink">Not validated</td>
                  <td className="p-3 font-semibold text-alert-red">{f.primaryDiseaseSignal || 'Healthy'}</td>
                  <td className="p-3 text-right">
                    <Link
                      to={`/organization/fields/${f.id}`}
                      className="px-3 py-1.5 bg-field-ink text-white font-bold text-xs rounded-xl hover:bg-opacity-90 transition inline-flex items-center gap-1"
                    >
                      <span>Inspect Field</span>
                      <ExternalLink size={12} className="text-lime-signal" />
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Video Cases */}
      <div className="bg-pure-surface border border-structural rounded-3xl p-6 shadow-xs space-y-3 text-xs">
        <h3 className="font-bold text-sm text-field-ink">Recent Video Analyses</h3>
        {farm.recentCases.length === 0 ? (
          <p className="text-muted-leaf py-2">No recent video analyses recorded for this farm.</p>
        ) : (
          farm.recentCases.map((c) => (
            <div key={c.id} className="p-3.5 bg-field-canvas rounded-2xl border border-structural flex items-center justify-between">
              <div>
                <p className="font-bold text-field-ink">Field case • {c.aiIndication}</p>
                <p className="text-[11px] text-muted-leaf">{new Date(c.submittedAt).toLocaleDateString()} • {c.confidence}% Confidence</p>
              </div>
              <Link
                to={`/agronomist/cases/${c.id}`}
                className="px-3 py-1.5 bg-pure-surface border border-structural font-bold rounded-lg text-field-ink hover:bg-gray-200 transition"
              >
                Open Case Details
              </Link>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
