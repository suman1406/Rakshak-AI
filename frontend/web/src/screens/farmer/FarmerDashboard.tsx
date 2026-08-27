import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { mockApi } from '../../services/mockApi';
import { Case, Field } from '../../types';
import { SafetyBanner } from '../../components/shared/SafetyBanner';
import { SeverityBadge, ReviewStatusBadge } from '../../components/shared/RoleBadge';
import {
  Camera,
  History,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  Sprout,
  Activity,
  FileText,
  ShieldAlert,
  ChevronRight,
} from 'lucide-react';

export const FarmerDashboard: React.FC = () => {
  const [field, setField] = useState<Field | null>(null);
  const [recentCases, setRecentCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      const fieldData = await mockApi.getFieldById('field-north-plot');
      const caseList = await mockApi.getCases();
      setField(fieldData);
      setRecentCases(caseList.slice(0, 3));
      setLoading(false);
    };
    fetchData();
  }, []);

  if (loading || !field) {
    return (
      <div className="p-8 text-center text-xs text-muted-leaf">
        Loading farmer field summary...
      </div>
    );
  }

  return (
    <div className="space-y-6 font-sans">
      {/* Top Banner / Welcome */}
      <div className="bg-pure-surface border border-structural p-6 rounded-3xl shadow-2xs flex flex-wrap items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="p-1 bg-soft-healthy rounded-lg text-emerald-800">
              <Sprout size={18} />
            </span>
            <span className="text-xs font-mono font-bold text-muted-leaf uppercase">Field Intelligence Portal</span>
          </div>
          <h1 className="text-2xl font-extrabold text-field-ink">Patil Farm • North Plot</h1>
          <p className="text-xs text-muted-leaf">Soybean (Glycine max) • 4.5 Acres • Latur District</p>
        </div>

        <Link
          to="/farmer/scan"
          className="px-5 py-3 bg-lime-signal text-field-ink font-bold text-xs rounded-xl hover:brightness-105 transition shadow-xs flex items-center gap-2"
        >
          <Camera size={16} />
          <span>Start New Field Scan</span>
        </Link>
      </div>

      <SafetyBanner />

      {/* Main Grid: Field Summary Card & Recent Scan Signals */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Field Health Status Card (5 cols) */}
        <div className="lg:col-span-5 bg-pure-surface border border-structural p-6 rounded-3xl shadow-xs space-y-6">
          <div className="flex items-center justify-between border-b border-structural pb-3">
            <span className="font-bold text-xs text-field-ink">Field Crop Health Index</span>
            <SeverityBadge severity={field.severity || 'Moderate'} />
          </div>

          {/* Health Gauge / Score */}
          <div className="flex items-center gap-5">
            <div className="relative w-24 h-24 rounded-full bg-field-canvas border-4 border-warning-orange flex items-center justify-center shrink-0">
              <div className="text-center">
                <span className="text-2xl font-black text-field-ink font-mono">{field.healthScore}</span>
                <span className="text-[10px] text-muted-leaf block">/100</span>
              </div>
            </div>

            <div className="space-y-1 text-xs">
              <h3 className="font-bold text-field-ink">Current Signal: {field.primaryDiseaseSignal}</h3>
              <p className="text-muted-leaf">
                Latest video scan captured on {field.latestScanDate}. Visual indicators suggest moderate foliar rust.
              </p>
              <p className="text-[11px] font-medium text-emerald-800 pt-1">
                Estimated affected plants: ~20%
              </p>
            </div>
          </div>

          {/* Metrics breakdown */}
          <div className="grid grid-cols-2 gap-3 pt-2 text-xs">
            <div className="p-3 bg-field-canvas rounded-2xl border border-structural">
              <span className="text-[10px] text-muted-leaf block">Analyzed Frames</span>
              <span className="font-bold text-field-ink font-mono text-sm">16 Frames</span>
            </div>
            <div className="p-3 bg-field-canvas rounded-2xl border border-structural">
              <span className="text-[10px] text-muted-leaf block">Leaf Regions</span>
              <span className="font-bold text-field-ink font-mono text-sm">43 Inspected</span>
            </div>
          </div>

          <Link
            to="/farmer/report/FASAL-10482"
            className="w-full py-2.5 bg-field-ink text-white font-bold text-xs rounded-xl hover:bg-opacity-90 transition flex items-center justify-center gap-2 block text-center"
          >
            <FileText size={14} className="text-lime-signal" />
            <span>View Full Crop-Health Report</span>
          </Link>
        </div>

        {/* Recent Scan History List (7 cols) */}
        <div className="lg:col-span-7 bg-pure-surface border border-structural p-6 rounded-3xl shadow-xs space-y-4">
          <div className="flex items-center justify-between border-b border-structural pb-3">
            <h3 className="font-bold text-xs text-field-ink">Recent Scan Signals</h3>
            <Link to="/farmer/history" className="text-xs text-muted-leaf hover:text-field-ink font-semibold flex items-center gap-1">
              View All History <ChevronRight size={14} />
            </Link>
          </div>

          <div className="space-y-3">
            {recentCases.map((c) => (
              <div
                key={c.id}
                className="p-4 bg-field-canvas rounded-2xl border border-structural hover:border-gray-300 transition flex items-center justify-between gap-4 text-xs"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-bold text-field-ink">#{c.id}</span>
                    <span className="text-[10px] text-muted-leaf">{new Date(c.submittedAt).toLocaleDateString()}</span>
                  </div>
                  <p className="font-semibold text-field-ink">{c.aiIndication} ({c.confidence}% Confidence)</p>
                  <ReviewStatusBadge status={c.reviewStatus} />
                </div>

                <Link
                  to={`/farmer/report/${c.id}`}
                  className="px-3 py-1.5 bg-pure-surface border border-structural font-bold text-xs text-field-ink rounded-lg hover:bg-gray-200 transition"
                >
                  View Report
                </Link>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
