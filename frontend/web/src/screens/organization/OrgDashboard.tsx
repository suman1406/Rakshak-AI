import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { liveWorkspaceApi } from '../../services/liveWorkspaceApi';
import { OrgDashboardMetrics, Farm } from '../../types';
import { SeverityBadge } from '../../components/shared/RoleBadge';
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import {
  Building2,
  Filter,
  Download,
  AlertTriangle,
  TrendingUp,
  ExternalLink,
  ShieldAlert,
  Search,
} from 'lucide-react';

export const OrgDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<OrgDashboardMetrics | null>(null);
  const [farms, setFarms] = useState<Farm[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [timeRange, setTimeRange] = useState('30d');
  const [district, setDistrict] = useState('all');
  const [fpo, setFpo] = useState('all');
  const [severity, setSeverity] = useState('all');

  useEffect(() => {
    const fetchOrgData = async () => {
      const [m, f] = await Promise.all([liveWorkspaceApi.getOrgMetrics(), liveWorkspaceApi.getFarms(district)]);
      setMetrics(m);
      setFarms(f);
      setLoading(false);
    };
    fetchOrgData();
  }, [district, timeRange]);

  if (loading || !metrics) {
    return <div className="space-y-6 p-6" aria-busy="true" aria-label="Loading organization command center">
      <div className="h-28 animate-pulse rounded-3xl bg-white/70 border border-structural" />
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">{Array.from({ length: 5 }).map((_, index) => <div key={index} className="h-24 animate-pulse rounded-2xl bg-white/70 border border-structural" />)}</div>
      <div className="h-80 animate-pulse rounded-3xl bg-white/70 border border-structural" />
    </div>;
  }

  // Chart dataset for health status breakdown
  const healthStatusData = [
    { name: 'Healthy', value: metrics.healthyPercent, color: '#66766D' },
    { name: 'At Risk', value: metrics.atRiskPercent, color: '#B86B36' },
    { name: 'Disease Detected', value: metrics.diseaseDetectedPercent, color: '#A84B45' },
  ];

  return (
    <div className="space-y-6 font-sans">
      {/* Top Header & Filter Controls */}
      <div className="bg-pure-surface border border-structural p-6 rounded-3xl shadow-2xs space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="p-1.5 bg-field-ink text-lime-signal rounded-lg">
                <Building2 size={18} />
              </span>
              <h1 className="text-2xl font-extrabold text-field-ink">Organization Command Center</h1>
            </div>
            <p className="text-xs text-muted-leaf mt-1">
              Organization field health intelligence
            </p>
            <p className="mt-2 text-[10px] font-mono uppercase tracking-wider text-muted-leaf">Live backend data · {timeRange === '30d' ? '30-day view' : timeRange}</p>
          </div>

          <div className="flex items-center gap-2 text-xs">
            <Link
              to="/organization/reports"
              className="px-4 py-2.5 bg-field-ink text-white font-bold rounded-xl hover:bg-opacity-90 transition shadow-xs flex items-center gap-1.5"
            >
              <Download size={14} className="text-lime-signal" /> Export Cluster Report
            </Link>
          </div>
        </div>

        {/* Filters Bar */}
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 pt-2 border-t border-structural text-xs">
          <div>
            <label className="block text-[10px] text-muted-leaf font-bold uppercase mb-1">Time Range</label>
            <select
              value={timeRange}
              onChange={(e) => setTimeRange(e.target.value)}
              className="w-full p-2 rounded-xl border border-structural bg-field-canvas text-xs font-medium outline-none"
            >
              <option value="7d">Last 7 Days</option>
              <option value="30d">Last 30 Days</option>
              <option value="90d">Last 90 Days</option>
              <option value="ytd">Year to Date</option>
            </select>
          </div>

          <div>
            <label className="block text-[10px] text-muted-leaf font-bold uppercase mb-1">District</label>
            <select
              value={district}
              onChange={(e) => setDistrict(e.target.value)}
              className="w-full p-2 rounded-xl border border-structural bg-field-canvas text-xs font-medium outline-none"
            >
              <option value="all">All districts</option>
              {Array.from(new Set(farms.map((farm) => farm.district).filter(Boolean))).map((value) => <option key={value} value={value}>{value}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-[10px] text-muted-leaf font-bold uppercase mb-1">FPO Collective</label>
            <select
              value={fpo}
              onChange={(e) => setFpo(e.target.value)}
              className="w-full p-2 rounded-xl border border-structural bg-field-canvas text-xs font-medium outline-none"
            >
              <option value="all">All organizations</option>
              {Array.from(new Set(farms.map((farm) => farm.fpoName).filter((value) => value && value !== 'Not available'))).map((value) => <option key={value} value={value}>{value}</option>)}
            </select>
          </div>

          <div>
            <label className="block text-[10px] text-muted-leaf font-bold uppercase mb-1">Crop Type</label>
            <select
              defaultValue="Soybean"
              className="w-full p-2 rounded-xl border border-structural bg-field-canvas text-xs font-medium outline-none"
            >
              <option value="Soybean">Soybean (Glycine max)</option>
            </select>
          </div>

          <div>
            <label className="block text-[10px] text-muted-leaf font-bold uppercase mb-1">Filter Severity</label>
            <select
              value={severity}
              onChange={(e) => setSeverity(e.target.value)}
              className="w-full p-2 rounded-xl border border-structural bg-field-canvas text-xs font-medium outline-none"
            >
              <option value="all">All Severities</option>
              <option value="Moderate">Moderate Risk</option>
              <option value="Severe">High Risk / Severe</option>
            </select>
          </div>
        </div>
      </div>

      {/* Top 5 Metrics Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 text-xs">
        <div className="p-4 bg-pure-surface rounded-2xl border border-structural shadow-2xs space-y-1">
          <span className="text-[10px] text-muted-leaf uppercase font-mono block">Total Monitored Farms</span>
          <span className="font-extrabold text-xl text-field-ink font-mono">{metrics.totalFarms.toLocaleString()}</span>
        </div>
        <div className="p-4 bg-pure-surface rounded-2xl border border-structural shadow-2xs space-y-1">
          <span className="text-[10px] text-emerald-800 uppercase font-mono block">Healthy Crop %</span>
          <span className="font-extrabold text-xl text-emerald-900 font-mono">{metrics.healthyPercent}%</span>
        </div>
        <div className="p-4 bg-pure-surface rounded-2xl border border-structural shadow-2xs space-y-1">
          <span className="text-[10px] text-amber-800 uppercase font-mono block">At Risk %</span>
          <span className="font-extrabold text-xl text-warning-orange font-mono">{metrics.atRiskPercent}%</span>
        </div>
        <div className="p-4 bg-pure-surface rounded-2xl border border-structural shadow-2xs space-y-1">
          <span className="text-[10px] text-alert-red uppercase font-mono block">Disease Detected %</span>
          <span className="font-extrabold text-xl text-alert-red font-mono">{metrics.diseaseDetectedPercent}%</span>
        </div>
        <div className="p-4 bg-red-50 rounded-2xl border border-red-200 shadow-2xs space-y-1">
          <span className="text-[10px] text-red-800 uppercase font-mono block">High-Risk Farms</span>
          <span className="font-extrabold text-xl text-alert-red font-mono">{metrics.highRiskFarmsCount}</span>
        </div>
      </div>

      {/* Backend-provided disease distribution */}
      <div className="grid grid-cols-1 gap-6">
        <div className="bg-pure-surface border border-structural p-6 rounded-3xl shadow-xs space-y-4">
          <h3 className="font-bold text-xs text-field-ink">Top Disease Signals Breakdown</h3>
          <div className="h-48 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={metrics.diseaseDistribution}
                  dataKey="percentage"
                  nameKey="disease"
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={4}
                >
                  {metrics.diseaseDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-2 text-xs">
            {metrics.diseaseDistribution.map((item) => (
              <div key={item.disease} className="flex items-center justify-between p-2 rounded-xl bg-field-canvas border border-structural">
                <div className="flex items-center gap-2">
                  <span className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                  <span className="font-semibold text-field-ink">{item.disease}</span>
                </div>
                <span className="font-mono font-bold text-field-ink">{item.percentage}%</span>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* High-Risk Farms Table */}
      <div className="bg-pure-surface border border-structural rounded-3xl shadow-xs p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-structural pb-3">
          <div className="flex items-center gap-2">
            <span className="p-1 bg-red-100 text-alert-red rounded-lg">
              <ShieldAlert size={16} />
            </span>
            <h3 className="font-bold text-xs text-field-ink">High-Risk Farm Escalate List</h3>
          </div>
          <span className="text-[11px] text-muted-leaf">Click farm to view field details</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-field-canvas border-b border-structural text-muted-leaf font-mono uppercase text-[10px]">
                <th className="p-3 font-bold">Farm & Owner</th>
                <th className="p-3 font-bold">Field Plot</th>
                <th className="p-3 font-bold">FPO / District</th>
                <th className="p-3 font-bold">Disease Signal</th>
                <th className="p-3 font-bold">Risk Level</th>
                <th className="p-3 font-bold text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-structural">
              {farms.map((farm) => (
                <tr key={farm.id} className="hover:bg-field-canvas/60 transition">
                  <td className="p-3 font-bold text-field-ink">{farm.name} ({farm.ownerName})</td>
                  <td className="p-3 text-muted-leaf">{farm.fields[0]?.name || 'No fields'}</td>
                  <td className="p-3 text-muted-leaf">{farm.fpoName} • {farm.district}</td>
                  <td className="p-3 font-semibold text-alert-red">
                    {farm.fields[0]?.primaryDiseaseSignal || 'No scan result'}
                  </td>
                  <td className="p-3">
                    <SeverityBadge severity={farm.fields[0]?.severity || 'Uncertain'} />
                  </td>
                  <td className="p-3 text-right">
                    <Link
                      to={`/organization/farms/${farm.id}`}
                      className="px-3 py-1.5 bg-field-canvas border border-structural font-bold text-xs rounded-xl hover:bg-gray-200 transition inline-flex items-center gap-1"
                    >
                      <span>Farm Details</span>
                      <ExternalLink size={12} />
                    </Link>
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
