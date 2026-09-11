import React, { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowDownToLine, ArrowUpRight, ChevronRight, CircleHelp, FolderOpen, Plus, RefreshCw, Search, SlidersHorizontal, Sprout, Database } from 'lucide-react';
import { liveWorkspaceApi } from '../../services/liveWorkspaceApi';
import { exportFields } from '../../services/reportExport';
import { useDemoMode } from '../../context/DemoModeContext';
import { demoWorkspaceToFarms } from '../../services/demoWorkspaceAdapters';
import { Farm } from '../../types';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

const assessmentStyles: Record<string, string> = { 'At Risk': 'attention', Healthy: 'clear', Uncertain: 'uncertain', 'Not assessed': 'unscanned' };
const signals = [
    { status: 'At Risk', label: 'Disease indication', color: '#b16b45' },
    { status: 'Healthy', label: 'No clear symptoms', color: '#487d63' },
    { status: 'Uncertain', label: 'Uncertain', color: '#b79a54' },
    { status: 'Not assessed', label: 'Not yet assessed', color: '#d0d8d1' },
];

export const OrgDashboard: React.FC = () => {
    const { enabled: isDemoMode, workspace, setEnabled: setDemoMode } = useDemoMode();
    const [farms, setFarms] = useState<Farm[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [district, setDistrict] = useState('all');
    const [search, setSearch] = useState('');
    const [assessment, setAssessment] = useState('all');

    async function load() {
        setLoading(true);
        setError('');
        try {
            if (isDemoMode && workspace) {
                setFarms(demoWorkspaceToFarms(workspace));
            } else {
                setFarms(await liveWorkspaceApi.getFarms());
            }
        }
        catch (e) {
            setError(e instanceof Error ? e.message : 'Could not load your organization');
        }
        finally {
            setLoading(false);
        }
    }

    useEffect(() => { void load(); }, [isDemoMode, workspace]);

    const districts = Array.from(new Set(farms.map(farm => farm.district))).sort();
    const visible = useMemo(() => farms.filter(farm => district === 'all' || farm.district === district).map(farm => ({ ...farm, fields: farm.fields.filter(field => (assessment === 'all' || field.healthStatus === assessment) && `${farm.name} ${field.name}`.toLowerCase().includes(search.trim().toLowerCase()))
    })).filter(farm => farm.fields.length), [farms, district, search, assessment]);
    const fields = visible.flatMap(farm => farm.fields);
    const distribution = signals.map(signal => ({ ...signal, value: fields.filter(field => field.healthStatus === signal.status).length }));
    const unscanned = distribution[3].value;
    const reviewed = fields.length - unscanned;
    const attention = distribution[0].value + distribution[2].value;
    const filtered = search || district !== 'all' || assessment !== 'all';

    return <div className="farmer-workspace portfolio-page">
    <header className="workspace-heading">
        <div>
            <span className="page-context">{isDemoMode ? 'Rakshak Demonstration Cooperative' : 'Your organization at a glance'}</span>
            <h1>Field overview</h1>
            <p>{isDemoMode ? 'Shared demonstration dataset of 6 farms and 12 soybean fields.' : 'A shared view of your fields and their latest observations.'}</p>
        </div>
        {!isDemoMode && <Link className="action" to="/organization/scans"><Plus size={16}/>Add field evidence</Link>}
    </header>

    {isDemoMode && (
      <section className="rounded-2xl border border-amber-200 bg-amber-50 p-4 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2.5 text-amber-900 font-semibold">
          <Database size={17} className="shrink-0 text-amber-800" />
          <span>Viewing shared demonstration cooperative data. Field assessments have not been fabricated.</span>
        </div>
        <button className="action secondary text-xs py-1.5 px-3" onClick={() => setDemoMode(false)}>
          Switch to Live workspace
        </button>
      </section>
    )}

    {error && <div className="message error" role="alert">{error}<button onClick={() => void load()}>Try again</button></div>}
    {loading ? <div className="portfolio-loading" role="status" aria-busy="true"><RefreshCw size={18} className="ui-spinner"/>Loading field records…</div> : <>
      <dl className="portfolio-metrics">{[
                { label: 'Fields in view', value: fields.length, description: `Across ${visible.length} ${visible.length === 1 ? 'farm' : 'farms'}`, style: 'neutral' },
                { label: 'With an assessment', value: reviewed, description: 'Latest scan available', style: 'clear' },
                { label: 'Need a closer look', value: attention, description: 'Disease indication or uncertainty', style: 'attention' },
                { label: 'Awaiting first scan', value: unscanned, description: 'No assessment recorded', style: 'unscanned' },
            ].map(item => <div key={item.label}><dt><span className={`metric-dot ${item.style}`}/>{item.label}</dt><dd>{item.value.toLocaleString()}</dd><p>{item.description}</p></div>)}</dl>
      {fields.length > 0 && <div className="portfolio-analysis"><section className="portfolio-chart-panel"><div className="panel-title"><div><h2>Latest indications</h2><p>The most recent assessment for each field</p></div><span className="subtle-tag">{fields.length} fields</span></div><div className="portfolio-distribution"><div className="portfolio-donut" aria-hidden="true"><ResponsiveContainer width="100%" height={205}><PieChart><Pie data={distribution} dataKey="value" innerRadius={66} outerRadius={86} paddingAngle={fields.length > 1 ? 2 : 0} stroke="none" isAnimationActive={false}>{distribution.map(item => <Cell key={item.status} fill={item.color}/>)}</Pie></PieChart></ResponsiveContainer><span><strong>{fields.length}</strong>in view</span></div><ul className="distribution-legend">{distribution.map(item => <li key={item.status}><i style={{ background: item.color }}/><span>{item.label}</span><strong>{item.value}</strong></li>)}</ul></div></section><section className="portfolio-next"><div className="panel-title"><div><h2>Your next steps</h2><p>Move the right observations forward</p></div><ArrowUpRight size={18}/></div><button onClick={() => setAssessment('Not assessed')}><span className="next-icon"><Sprout size={19}/></span><span><strong>Start with a first observation</strong><small>{unscanned} {unscanned === 1 ? 'field is' : 'fields are'} waiting for a scan</small></span><ChevronRight size={16}/></button><button onClick={() => setAssessment('Uncertain')}><span className="next-icon"><CircleHelp size={19}/></span><span><strong>Revisit uncertain results</strong><small>{distribution[2].value} {distribution[2].value === 1 ? 'field needs' : 'fields need'} more context</small></span><ChevronRight size={16}/></button><Link to="/organization/reports" className="next-footer">Open assessment reports <ArrowUpRight size={15}/></Link></section></div>}
    </>}
    <section className="portfolio-records"><div className="records-title"><div><h2>Field records <span>{loading ? '…' : fields.length}</span></h2><p>Original observations, organized by farm.</p></div><div className="records-actions"><button aria-label="Refresh field records" title="Refresh field records" disabled={loading} onClick={() => void load()}><RefreshCw size={16}/></button><button disabled={loading || !fields.length} onClick={() => exportFields(visible)}><ArrowDownToLine size={15}/><span>Export CSV</span></button></div></div>
      <div className="portfolio-toolbar"><label className="portfolio-search"><Search size={16}/><span className="sr-only">Find a farm or field</span><input type="search" placeholder="Search farms or fields…" value={search} onChange={e => setSearch(e.target.value)}/></label><div className="portfolio-selects"><SlidersHorizontal size={15} aria-hidden="true"/><label><span className="sr-only">District</span><select value={district} onChange={e => setDistrict(e.target.value)}><option value="all">All districts</option>{districts.map(item => <option key={item}>{item}</option>)}</select></label><label><span className="sr-only">Assessment</span><select value={assessment} onChange={e => setAssessment(e.target.value)}><option value="all">All assessments</option>{signals.map(item => <option key={item.status} value={item.status}>{item.label}</option>)}</select></label>{filtered && <button className="text-action" onClick={() => { setSearch(''); setDistrict('all'); setAssessment('all'); }}>Clear filters</button>}</div></div>
      {!loading && !fields.length && <div className="portfolio-empty"><FolderOpen size={30}/><h3>{filtered ? 'No fields match these filters' : 'Your field story starts here'}</h3><p>{filtered ? 'Try another name, district or assessment.' : 'Add a field and capture its first observation to build your organization’s overview.'}</p>{filtered ? <button className="action secondary" onClick={() => { setSearch(''); setDistrict('all'); setAssessment('all'); }}>Show all fields</button> : <Link className="action" to="/organization/scans">Add your first field <Plus size={15}/></Link>}</div>}
      {!loading && fields.length > 0 && <div className="portfolio-table-wrap"><table className="portfolio-table"><thead><tr><th>Field / farm</th><th>Latest indication</th><th>Last observation</th><th><span className="sr-only">Evidence</span></th></tr></thead><tbody>{visible.flatMap(farm => farm.fields.map(field => <tr key={field.id}><td><div className="record-identity"><span className="record-field-icon"><Sprout size={19}/></span><div><Link to={`/organization/fields/${field.id}`}>{field.name}</Link><Link className="record-farm" to={`/organization/farms/${farm.id}`}>{farm.name} · {farm.district}</Link></div></div></td><td><span className={`assessment-pill ${assessmentStyles[field.healthStatus] || 'unscanned'}`}><i />{signals.find(item => item.status === field.healthStatus)?.label || field.healthStatus}</span>{field.latestScanDate && <small className="record-signal">{field.primaryDiseaseSignal}</small>}</td><td><span className="record-date">{field.latestScanDate ? new Date(field.latestScanDate).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' }) : 'No scan recorded'}</span></td><td><Link className="record-open" to={`/organization/fields/${field.id}`}>View details <ArrowUpRight size={14}/></Link></td></tr>))}</tbody></table><div className="records-bottom">Showing {fields.length} {fields.length === 1 ? 'field' : 'fields'}{filtered ? ' matching your filters' : ' in your organization'}<span>{isDemoMode ? 'Shared demonstration records' : 'Private organization records'}</span></div></div>}
    </section><p className="portfolio-disclaimer"><CircleHelp size={14}/>Visual indications from baseline models, not confirmed diagnoses. Filters apply to all figures and exported rows.</p>
  </div>;
};

