import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { mockApi } from '../../services/mockApi';
import { apiClient } from '../../services/apiClient';
import { Case, AgronomistMetrics, ReviewStatus } from '../../types';
import { SeverityBadge, ReviewStatusBadge } from '../../components/shared/RoleBadge';
import {
  ClipboardList,
  Search,
  Filter,
  CheckCircle2,
  Clock,
  AlertTriangle,
  ArrowUpDown,
  ExternalLink,
  RotateCcw,
  UserCheck,
} from 'lucide-react';

export const AgronomistDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<AgronomistMetrics | null>(null);
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState<ReviewStatus | 'all'>('all');
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [cropFilter, setCropFilter] = useState<string>('all');
  const [diseaseFilter, setDiseaseFilter] = useState<string>('all');
  const [confidenceMin, setConfidenceMin] = useState<number>(0);
  const [sortBy, setSortBy] = useState<'priority' | 'date'>('priority');

  const fetchQueue = async () => {
    setLoading(true);
    const m = await mockApi.getAgronomistMetrics();
    let c = await mockApi.getCases({
      status: statusFilter,
      severity: severityFilter,
      crop: cropFilter,
      disease: diseaseFilter,
      confidenceMin: confidenceMin > 0 ? confidenceMin : undefined,
      search: search,
    });
    try {
      const live = await apiClient.getAgronomistQueue();
      if (Array.isArray(live) && live.length > 0) {
        c = live.map((item: any) => ({ ...cases[0], id: item.video_diagnosis_id, aiIndication: item.disease, confidence: Math.round((item.confidence || 0) * 100), severity: item.severity_level >= 3 ? 'Severe' : item.severity_level > 0 ? 'Moderate' : 'Healthy', submittedAt: item.created_at, reviewStatus: 'awaiting_review', priority: item.confidence < 0.65 ? 'high' : 'medium' }));
      }
    } catch (_) { /* Keep fixture queue when the API is unavailable. */ }

    // Sorting
    let sorted = [...c];
    if (sortBy === 'priority') {
      const pOrder = { high: 1, medium: 2, low: 3 };
      sorted.sort((a, b) => pOrder[a.priority] - pOrder[b.priority]);
    } else {
      sorted.sort((a, b) => new Date(b.submittedAt).getTime() - new Date(a.submittedAt).getTime());
    }

    setMetrics(m);
    setCases(sorted);
    setLoading(false);
  };

  useEffect(() => {
    fetchQueue();
  }, [search, statusFilter, severityFilter, cropFilter, diseaseFilter, confidenceMin, sortBy]);

  const handleResetFilters = () => {
    setSearch('');
    setStatusFilter('all');
    setSeverityFilter('all');
    setCropFilter('all');
    setDiseaseFilter('all');
    setConfidenceMin(0);
    setSortBy('priority');
  };

  return (
    <div className="space-y-6 font-sans">
      {/* Page Title & Metrics Bar */}
      <div className="bg-pure-surface border border-structural p-6 rounded-3xl shadow-2xs space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="flex items-center gap-2">
              <span className="p-1.5 bg-field-ink text-lime-signal rounded-lg font-bold">
                <ClipboardList size={18} />
              </span>
              <h1 className="text-2xl font-extrabold text-field-ink">Agronomist Case Verification Queue</h1>
            </div>
            <p className="text-xs text-muted-leaf mt-1">
              Audit AI-generated soybean crop disease indications and issue verified advice
            </p>
          </div>

          <span className="text-xs font-mono bg-soft-healthy text-emerald-800 px-3 py-1 rounded-full font-bold">
            Lab Operational SLA: 11m
          </span>
        </div>

        {/* 5 Header Metrics Cards */}
        {metrics && (
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 pt-2 text-xs">
            <div className="p-3.5 bg-field-canvas rounded-2xl border border-structural">
              <span className="text-[10px] text-muted-leaf uppercase font-mono block">Open Cases</span>
              <span className="font-extrabold text-lg text-field-ink font-mono">{metrics.openCases}</span>
            </div>
            <div className="p-3.5 bg-amber-50 rounded-2xl border border-amber-200">
              <span className="text-[10px] text-amber-800 uppercase font-mono block">High Priority</span>
              <span className="font-extrabold text-lg text-amber-900 font-mono">{metrics.highPriorityCases}</span>
            </div>
            <div className="p-3.5 bg-field-canvas rounded-2xl border border-structural">
              <span className="text-[10px] text-muted-leaf uppercase font-mono block">Awaiting Review</span>
              <span className="font-extrabold text-lg text-field-ink font-mono">{metrics.awaitingReview}</span>
            </div>
            <div className="p-3.5 bg-emerald-50 rounded-2xl border border-emerald-200">
              <span className="text-[10px] text-emerald-800 uppercase font-mono block">Reviewed This Week</span>
              <span className="font-extrabold text-lg text-emerald-900 font-mono">{metrics.reviewedThisWeek}</span>
            </div>
            <div className="p-3.5 bg-field-canvas rounded-2xl border border-structural">
              <span className="text-[10px] text-muted-leaf uppercase font-mono block">Avg Review Time</span>
              <span className="font-extrabold text-lg text-field-ink font-mono">{metrics.averageReviewTimeMinutes} mins</span>
            </div>
          </div>
        )}
      </div>

      {/* Filter Toolbar */}
      <div className="bg-pure-surface border border-structural p-5 rounded-3xl shadow-xs space-y-4 text-xs">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="relative flex-1 min-w-[240px]">
            <Search size={16} className="absolute left-3.5 top-3 text-muted-leaf" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search by Case ID, Farm, Field, or FPO..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-structural bg-field-canvas text-xs outline-none"
            />
          </div>

          <div className="flex items-center gap-2">
            <span className="text-muted-leaf font-bold flex items-center gap-1">
              <Filter size={14} /> Filter Queue:
            </span>
            <button
              onClick={handleResetFilters}
              className="px-3 py-1.5 bg-field-canvas hover:bg-gray-200 border border-structural rounded-lg text-muted-leaf text-xs font-semibold transition flex items-center gap-1"
            >
              <RotateCcw size={12} /> Reset
            </button>
          </div>
        </div>

        {/* Filter Dropdowns Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-6 gap-3">
          <div>
            <label className="block text-[10px] text-muted-leaf font-bold uppercase mb-1">Status</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value as any)}
              className="w-full p-2 rounded-xl border border-structural bg-field-canvas text-xs font-medium outline-none"
            >
              <option value="all">All Statuses</option>
              <option value="awaiting_review">Awaiting Review</option>
              <option value="reviewed">Reviewed</option>
              <option value="needs_inspection">Needs Inspection</option>
            </select>
          </div>

          <div>
            <label className="block text-[10px] text-muted-leaf font-bold uppercase mb-1">Severity</label>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="w-full p-2 rounded-xl border border-structural bg-field-canvas text-xs font-medium outline-none"
            >
              <option value="all">All Severities</option>
              <option value="Early">Early</option>
              <option value="Moderate">Moderate</option>
              <option value="Severe">Severe</option>
              <option value="Uncertain">Uncertain</option>
            </select>
          </div>

          <div>
            <label className="block text-[10px] text-muted-leaf font-bold uppercase mb-1">Disease Signal</label>
            <select
              value={diseaseFilter}
              onChange={(e) => setDiseaseFilter(e.target.value)}
              className="w-full p-2 rounded-xl border border-structural bg-field-canvas text-xs font-medium outline-none"
            >
              <option value="all">All Diseases</option>
              <option value="Rust">Soybean Rust</option>
              <option value="Blight">Bacterial Blight</option>
              <option value="Cercospora">Cercospora</option>
            </select>
          </div>

          <div>
            <label className="block text-[10px] text-muted-leaf font-bold uppercase mb-1">Min Confidence</label>
            <select
              value={confidenceMin}
              onChange={(e) => setConfidenceMin(Number(e.target.value))}
              className="w-full p-2 rounded-xl border border-structural bg-field-canvas text-xs font-medium outline-none font-mono"
            >
              <option value={0}>Any Confidence</option>
              <option value={50}>≥ 50% Confidence</option>
              <option value={75}>≥ 75% Confidence</option>
              <option value={85}>≥ 85% Confidence</option>
            </select>
          </div>

          <div>
            <label className="block text-[10px] text-muted-leaf font-bold uppercase mb-1">Sort Order</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="w-full p-2 rounded-xl border border-structural bg-field-canvas text-xs font-medium outline-none"
            >
              <option value="priority">Sort by Priority</option>
              <option value="date">Sort by Date</option>
            </select>
          </div>

          <div className="flex items-end">
            <span className="text-muted-leaf text-[11px] font-mono font-semibold py-2">
              Showing {cases.length} cases
            </span>
          </div>
        </div>
      </div>

      {/* Case Queue Table */}
      <div className="bg-pure-surface border border-structural rounded-3xl shadow-xs overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-xs text-muted-leaf">Updating agronomist queue...</div>
        ) : cases.length === 0 ? (
          <div className="p-12 text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-field-canvas border border-structural flex items-center justify-center mx-auto text-muted-leaf">
              <Search size={20} />
            </div>
            <p className="font-bold text-sm text-field-ink">No matching cases found</p>
            <p className="text-xs text-muted-leaf">Try clearing your search query or adjusting filter parameters.</p>
            <button
              onClick={handleResetFilters}
              className="px-4 py-2 bg-field-ink text-white font-bold text-xs rounded-xl"
            >
              Reset Filters
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-field-canvas border-b border-structural text-muted-leaf font-mono uppercase text-[10px]">
                  <th className="p-4 font-bold">Case ID</th>
                  <th className="p-4 font-bold">Crop & Field</th>
                  <th className="p-4 font-bold">AI Indication</th>
                  <th className="p-4 font-bold">Confidence</th>
                  <th className="p-4 font-bold">Severity</th>
                  <th className="p-4 font-bold">Submitted Date</th>
                  <th className="p-4 font-bold">Review Status</th>
                  <th className="p-4 font-bold text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-structural">
                {cases.map((c) => (
                  <tr key={c.id} className="hover:bg-field-canvas/60 transition">
                    <td className="p-4 font-mono font-bold text-field-ink">
                      <div className="flex items-center gap-1.5">
                        {c.priority === 'high' && (
                          <span className="w-2 h-2 rounded-full bg-alert-red animate-pulse" title="High Priority" />
                        )}
                        <span>#{c.id}</span>
                      </div>
                    </td>
                    <td className="p-4">
                      <p className="font-bold text-field-ink">{c.crop}</p>
                      <p className="text-[11px] text-muted-leaf">
                        {c.farmName} • {c.fieldName} ({c.fpoName})
                      </p>
                    </td>
                    <td className="p-4 font-semibold text-field-ink">{c.aiIndication}</td>
                    <td className="p-4 font-mono font-bold text-field-ink">{c.confidence}%</td>
                    <td className="p-4">
                      <SeverityBadge severity={c.severity} />
                    </td>
                    <td className="p-4 text-muted-leaf font-mono">{new Date(c.submittedAt).toLocaleDateString()}</td>
                    <td className="p-4">
                      <ReviewStatusBadge status={c.reviewStatus} />
                    </td>
                    <td className="p-4 text-right">
                      <Link
                        to={`/agronomist/cases/${c.id}`}
                        className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-field-ink text-white text-xs font-bold rounded-xl hover:bg-opacity-90 transition shadow-2xs"
                      >
                        <span>Review</span>
                        <ExternalLink size={12} className="text-lime-signal" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
