import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { liveWorkspaceApi } from '../../services/liveWorkspaceApi';
import { exportFields } from '../../services/reportExport';
import { Farm } from '../../types';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

export const OrgDashboard: React.FC = () => {
  const [farms, setFarms] = useState<Farm[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [district, setDistrict] = useState('all');
  const [search, setSearch] = useState('');
  const [assessment, setAssessment] = useState('all');
  async function load() {
    setLoading(true); setError('');
    try { setFarms(await liveWorkspaceApi.getFarms()); }
    catch (e) { setError(e instanceof Error ? e.message : 'Could not load your organization'); }
    finally { setLoading(false); }
  }
  useEffect(() => { void load(); }, []);
  const districts = Array.from(new Set(farms.map(farm => farm.district))).sort();
  const visible = useMemo(() => farms.filter(farm => district === 'all' || farm.district === district).map(farm => ({ ...farm, fields: farm.fields.filter(field =>
    (assessment === 'all' || field.healthStatus === assessment) && `${farm.name} ${field.name}`.toLowerCase().includes(search.trim().toLowerCase()))
  })).filter(farm => farm.fields.length), [farms, district, search, assessment]);
  const fields = visible.flatMap(farm => farm.fields);
  const counts = [
    ['Fields shown', fields.length],
    ['Disease indications', fields.filter(field => field.healthStatus === 'At Risk').length],
    ['No clear symptoms', fields.filter(field => field.healthStatus === 'Healthy').length],
    ['Uncertain or unscanned', fields.filter(field => ['Uncertain', 'Not assessed'].includes(field.healthStatus)).length],
  ];
  return <div className="farmer-workspace">
    <header className="workspace-heading"><div><p className="eyebrow">ORGANIZATION FIELD CARE</p><h1>Field overview</h1><p>See which fields need attention. Each indication comes from the latest scan.</p></div><div className="flex flex-wrap gap-2"><button className="action secondary" disabled={loading} onClick={() => void load()}>Refresh records</button><button className="action secondary" disabled={loading || !fields.length} onClick={() => exportFields(visible)}>Export visible fields</button></div></header>
    {error && <div className="message error" role="alert">{error}<button onClick={() => void load()}>Try again</button></div>}
    <section className="workspace-panel organization-filters"><label>Find a farm or field<input type="search" placeholder="Search your portfolio" value={search} onChange={e => setSearch(e.target.value)} /></label><label>District<select value={district} onChange={e => setDistrict(e.target.value)}><option value="all">All districts</option>{districts.map(item => <option key={item}>{item}</option>)}</select></label><label>Assessment<select value={assessment} onChange={e => setAssessment(e.target.value)}><option value="all">All fields</option>{['At Risk', 'Healthy', 'Uncertain', 'Not assessed'].map(item => <option key={item}>{item}</option>)}</select></label>{(search || district !== 'all' || assessment !== 'all') && <button className="text-action" onClick={() => { setSearch(''); setDistrict('all'); setAssessment('all'); }}>Clear all filters</button>}</section>
    {loading ? <p aria-busy="true">Loading field records…</p> : <>
      <dl className="report-facts">{counts.map(([label, count]) => <div key={label}><dt>{label}</dt><dd>{count}</dd></div>)}</dl>
      {fields.length > 0 && <div className="portfolio-insights"><section className="workspace-panel"><p className="eyebrow">Portfolio snapshot</p><h2>Latest field indications</h2><div className="portfolio-distribution"><div className="portfolio-donut" aria-hidden="true"><ResponsiveContainer width="100%" height={210}><PieChart><Pie data={counts.slice(1).map(([name, value]) => ({ name, value: Number(value) }))} dataKey="value" innerRadius={65} outerRadius={92} paddingAngle={3} isAnimationActive={false}>{['#b86b38', '#2c7254', '#b8c2b8'].map(color => <Cell key={color} fill={color}/>)}</Pie></PieChart></ResponsiveContainer><span><strong>{fields.length}</strong>fields</span></div><ul className="distribution-legend">{counts.slice(1).map(([label, count], index) => <li key={label}><i style={{ background: ['#b86b38', '#2c7254', '#b8c2b8'][index] }}/><span>{label}</span><strong>{count}</strong></li>)}</ul></div></section><section className="workspace-panel attention-panel"><p className="eyebrow">Next steps</p><h2>Keep the evidence moving.</h2><p>{fields.some(field => field.healthStatus === 'At Risk') ? 'Open fields with disease indications and review their supporting frames before deciding on follow-up.' : 'Review uncertain assessments or capture the first scan for fields without evidence.'}</p><Link className="action" to="/organization/reports">Explore assessment reports</Link><Link className="text-action" to="/organization/scans">Capture new field evidence</Link></section></div>}
      <p className="safety-copy">These are visual indications from baseline models, not confirmed diagnoses or a validated farm health score. Filters apply to all figures and exported rows.</p>
      {!fields.length && <section className="workspace-panel"><h2>No matching fields</h2><p>{farms.length ? 'Change your filters to see more fields.' : 'Add your first field and record a scan to start your organization overview.'}</p><Link className="action" to="/organization/scans">Manage fields and scans</Link></section>}
      {visible.map(farm => <section className="workspace-panel" key={farm.id}><div className="section-heading"><div><h2>{farm.name}</h2><p>{farm.district}</p></div><Link className="text-action" to={`/organization/farms/${farm.id}`}>View farm</Link></div><ul className="scan-list">{farm.fields.map(field => <li key={field.id}><div><strong>{field.name}</strong><p>{field.latestScanDate ? `${field.primaryDiseaseSignal} · ${field.severity}` : 'No assessment recorded'}</p><p>{field.latestScanDate ? new Date(field.latestScanDate).toLocaleString() : 'No scan recorded'}</p></div><span className="status-label">{field.healthStatus}</span><Link className="text-action" to={`/organization/fields/${field.id}`}>View evidence</Link></li>)}</ul></section>)}
    </>}
  </div>;
};
