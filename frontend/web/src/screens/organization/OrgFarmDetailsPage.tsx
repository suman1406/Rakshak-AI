import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { mockApi } from '../../services/mockApi';
import { Farm } from '../../types';
import { SeverityBadge } from '../../components/shared/RoleBadge';
import { ArrowLeft, Building2, MapPin, ExternalLink, ShieldAlert, FileText } from 'lucide-react';

export const OrgFarmDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [farm, setFarm] = useState<Farm | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchFarm = async () => {
      const found = await mockApi.getFarmById(id || 'farm-001');
      setFarm(found || (await mockApi.getFarmById('farm-001')));
      setLoading(false);
    };
    fetchFarm();
  }, [id]);

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
          <span className="font-extrabold text-xl text-field-ink font-mono">{farm.healthScore}/100</span>
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
                  <td className="p-3 font-mono font-bold text-field-ink">{f.healthScore}/100</td>
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
        {farm.recentCases.map((c) => (
          <div key={c.id} className="p-3.5 bg-field-canvas rounded-2xl border border-structural flex items-center justify-between">
            <div>
              <p className="font-bold text-field-ink">Case #{c.id} • {c.aiIndication}</p>
              <p className="text-[11px] text-muted-leaf">{new Date(c.submittedAt).toLocaleDateString()} • {c.confidence}% Confidence</p>
            </div>
            <Link
              to={`/agronomist/cases/${c.id}`}
              className="px-3 py-1.5 bg-pure-surface border border-structural font-bold rounded-lg text-field-ink hover:bg-gray-200 transition"
            >
              Open Case Details
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
};
