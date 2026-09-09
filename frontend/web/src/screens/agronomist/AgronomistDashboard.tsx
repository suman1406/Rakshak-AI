import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { liveWorkspaceApi } from '../../services/liveWorkspaceApi';
import { Case, AgronomistMetrics, ReviewStatus } from '../../types';
import { ReviewStatusBadge } from '../../components/shared/RoleBadge';
import { ClipboardList, Search, Filter, AlertTriangle, ExternalLink, RotateCcw, } from 'lucide-react';
export const AgronomistDashboard: React.FC = () => {
    const [metrics, setMetrics] = useState<AgronomistMetrics | null>(null);
    const [cases, setCases] = useState<Case[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const requestVersion = useRef(0);
    // Filters
    const [search, setSearch] = useState('');
    const [statusFilter, setStatusFilter] = useState<ReviewStatus | 'all'>('all');
    const [severityFilter, setSeverityFilter] = useState<string>('all');
    const [cropFilter, setCropFilter] = useState<string>('all');
    const [diseaseFilter, setDiseaseFilter] = useState<string>('all');
    const [confidenceMin, setConfidenceMin] = useState<number>(0);
    const [sortBy, setSortBy] = useState<'priority' | 'date'>('priority');
    const fetchQueue = async () => {
        const version = ++requestVersion.current;
        setLoading(true);
        setError('');
        try {
            let c = await liveWorkspaceApi.getCases();
            c = c.filter((item) => (statusFilter === 'all' || item.reviewStatus === statusFilter) &&
                (severityFilter === 'all' || item.severity === severityFilter) &&
                (cropFilter === 'all' || item.crop.toLowerCase() === cropFilter.toLowerCase()) &&
                (diseaseFilter === 'all' || item.aiIndication.toLowerCase().includes(diseaseFilter.toLowerCase())) &&
                (!confidenceMin || item.confidence >= confidenceMin) &&
                (!search.trim() || [item.id, item.farmName, item.fieldName, item.fpoName].some((value) => value.toLowerCase().includes(search.trim().toLowerCase()))));
            const m = await liveWorkspaceApi.getAgronomistMetrics(c);
            // Sorting
            let sorted = [...c];
            if (sortBy === 'priority') {
                const pOrder = { high: 1, medium: 2, low: 3 };
                sorted.sort((a, b) => pOrder[a.priority] - pOrder[b.priority]);
            }
            else {
                sorted.sort((a, b) => new Date(b.submittedAt).getTime() - new Date(a.submittedAt).getTime());
            }
            if (version !== requestVersion.current)
                return;
            setMetrics(m);
            setCases(sorted);
        }
        catch (e) {
            if (version === requestVersion.current)
                setError(e instanceof Error ? e.message : 'Could not load review queue');
        }
        finally {
            if (version === requestVersion.current)
                setLoading(false);
        }
    };
    useEffect(() => {
        fetchQueue();
        return () => { requestVersion.current++; };
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
    return <div className="farmer-workspace review-workspace">
    <header className="workspace-heading"><div><span className="page-context">Your independent perspective</span><h1>Review queue</h1><p>Crop observations waiting for a closer look. Evidence first, judgment yours.</p></div><button className="action secondary" disabled={loading} onClick={() => void fetchQueue()}><RotateCcw size={15}/>Refresh queue</button></header>
    {error && <div className="message error" role="alert">{error}<button onClick={() => void fetchQueue()}>Try again</button></div>}
    {metrics && <dl className="portfolio-metrics review-metrics">{[
                ['Open cases', metrics.openCases, 'In the filtered queue'], ['High priority', metrics.highPriorityCases, 'Prioritized for attention'], ['Awaiting review', metrics.awaitingReview, 'Ready for assessment'], ['Reviewed this week', metrics.reviewedThisWeek, 'Your reviews in the last 7 days'], ['Upload to review', metrics.averageReviewTimeMinutes !== null ? `${metrics.averageReviewTimeMinutes} min` : '—', 'Includes time in queue'],
            ].map(([label, value, detail]) => <div key={label}><dt>{label}</dt><dd>{value}</dd><p>{detail}</p></div>)}</dl>}
    <section className="portfolio-records"><div className="records-title"><div><h2>Requested assessments <span>{loading ? '…' : cases.length}</span></h2><p>Cases shared for expert review</p></div><span className="subtle-tag">Human review</span></div>
      <div className="portfolio-toolbar"><label className="portfolio-search"><Search size={16}/><span className="sr-only">Search review queue</span><input type="search" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search case, farm, field or organization…"/></label><div className="portfolio-selects"><select aria-label="Status" value={statusFilter} onChange={e => setStatusFilter(e.target.value as ReviewStatus | 'all')}><option value="all">All statuses</option><option value="awaiting_review">Awaiting review</option><option value="reviewed">Reviewed</option><option value="needs_inspection">Needs inspection</option></select><select aria-label="Sort order" value={sortBy} onChange={e => setSortBy(e.target.value as 'priority' | 'date')}><option value="priority">Priority first</option><option value="date">Newest first</option></select></div></div>
      <details className="review-filters"><summary><Filter size={14}/>Refine the queue{(severityFilter !== 'all' || diseaseFilter !== 'all' || confidenceMin > 0) && <span>Filters active</span>}</summary><div><label>Severity<select aria-label="Severity" value={severityFilter} onChange={e => setSeverityFilter(e.target.value)}><option value="all">All severities</option>{['Early', 'Moderate', 'Severe', 'Uncertain'].map(value => <option key={value}>{value}</option>)}</select></label><label>Disease signal<select aria-label="Disease signal" value={diseaseFilter} onChange={e => setDiseaseFilter(e.target.value)}><option value="all">All indications</option><option value="Rust">Soybean rust</option><option value="Blight">Bacterial blight</option><option value="Frogeye">Frogeye leaf spot</option></select></label><label>Minimum confidence<select aria-label="Minimum confidence" value={confidenceMin} onChange={e => setConfidenceMin(Number(e.target.value))}><option value={0}>Any confidence</option><option value={50}>At least 50%</option><option value={75}>At least 75%</option><option value={85}>At least 85%</option></select></label><button className="action secondary" onClick={handleResetFilters}>Clear all filters</button></div></details>
      {loading ? <div className="portfolio-loading" role="status" aria-busy="true"><RotateCcw size={17} className="ui-spinner"/>Updating the review queue…</div> : !cases.length ? <div className="portfolio-empty"><ClipboardList size={30}/><h3>No matching cases</h3><p>New requests appear when a farmer asks for review. Clear filters to see all accessible cases.</p><button className="action secondary" onClick={handleResetFilters}>Show all cases</button></div> : <div className="review-table-wrap" tabIndex={0} role="region" aria-label="Review cases, scroll horizontally for all columns"><p className="table-scroll-hint">Scroll across to see all case details and actions.</p><table className="review-table"><thead><tr><th>Field / organization</th><th>AI perspective</th><th>Requested</th><th>Review status</th><th><span className="sr-only">Open case</span></th></tr></thead><tbody>{cases.map(c => <tr key={c.id}><td><Link className="review-field-name" to={`/agronomist/cases/${c.id}`}>{c.fieldName}</Link><p>{c.farmName} · {c.fpoName}</p><small>{c.crop}{c.priority === 'high' ? ' · High priority' : ''}</small></td><td><strong>{c.aiIndication}</strong><p>{c.confidence}% confidence · {c.severity}</p></td><td><span>{new Date(c.submittedAt).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })}</span></td><td><ReviewStatusBadge status={c.reviewStatus}/></td><td><Link className="record-open" to={`/agronomist/cases/${c.id}`}>Review evidence <ExternalLink size={14}/></Link></td></tr>)}</tbody></table><div className="records-bottom">Showing {cases.length} {cases.length === 1 ? 'case' : 'cases'}<span>Queue counts reflect filters; review history is account-wide</span></div></div>}
    </section><p className="portfolio-disclaimer"><AlertTriangle size={14}/>Model indications are advisory. Inspect the original evidence before recording your assessment.</p>
  </div>;
};
