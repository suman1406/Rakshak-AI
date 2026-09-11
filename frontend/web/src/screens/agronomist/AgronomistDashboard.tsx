import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { liveWorkspaceApi } from '../../services/liveWorkspaceApi';
import { useDemoMode } from '../../context/DemoModeContext';
import { Case, AgronomistMetrics, ReviewStatus } from '../../types';
import { ReviewStatusBadge } from '../../components/shared/RoleBadge';
import { ClipboardList, Search, Filter, AlertTriangle, ExternalLink, RotateCcw, Database } from 'lucide-react';

export const AgronomistDashboard: React.FC = () => {
    const { enabled: isDemoMode, setEnabled: setDemoMode } = useDemoMode();
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
            if (isDemoMode) {
                if (version !== requestVersion.current) return;
                setMetrics({
                    openCases: 0,
                    highPriorityCases: 0,
                    awaitingReview: 0,
                    reviewedThisWeek: 0,
                    averageReviewTimeMinutes: null,
                });
                setCases([]);
                setLoading(false);
                return;
            }

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
    }, [isDemoMode, search, statusFilter, severityFilter, cropFilter, diseaseFilter, confidenceMin, sortBy]);

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
    <header className="workspace-heading">
        <div>
            <span className="page-context">{isDemoMode ? 'Demo Workspace Active' : 'Your independent perspective'}</span>
            <h1>Review queue</h1>
            <p>{isDemoMode ? 'Rakshak Demonstration Cooperative contains 6 farms and 12 soybean fields.' : 'Crop observations waiting for a closer look. Evidence first, judgment yours.'}</p>
        </div>
        {!isDemoMode && <button className="action secondary" disabled={loading} onClick={() => void fetchQueue()}><RotateCcw size={15}/>Refresh queue</button>}
    </header>

    {isDemoMode && (
      <section className="rounded-2xl border border-amber-200 bg-amber-50 p-4 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2.5 text-amber-900 font-semibold">
          <Database size={17} className="shrink-0 text-amber-800" />
          <span>Demo farms for <strong>Rakshak Demonstration Cooperative</strong> belong to <strong>Rakshak Demo Farmer</strong> (<code>farmer@rakshak.local</code>). No review cases are shown because demo mode never fabricates AI diagnoses or human-review work.</span>
        </div>
        <button className="action secondary text-xs py-1.5 px-3" onClick={() => setDemoMode(false)}>
          Switch to Live workspace
        </button>
      </section>
    )}

    {error && <div className="message error" role="alert">{error}<button onClick={() => void fetchQueue()}>Try again</button></div>}

    {metrics && <dl className="portfolio-metrics review-metrics">{[
                ['Open cases', metrics.openCases, isDemoMode ? 'No demo cases' : 'In the filtered queue'],
                ['High priority', metrics.highPriorityCases, isDemoMode ? 'No demo cases' : 'Prioritized for attention'],
                ['Awaiting review', metrics.awaitingReview, isDemoMode ? 'No demo cases' : 'Ready for assessment'],
                ['Reviewed this week', metrics.reviewedThisWeek, 'Your reviews in the last 7 days'],
                ['Upload to review', metrics.averageReviewTimeMinutes !== null ? `${metrics.averageReviewTimeMinutes} min` : '—', 'Includes time in queue'],
            ].map(([label, value, detail]) => <div key={label}><dt>{label}</dt><dd>{value}</dd><p>{detail}</p></div>)}</dl>}

    <section className="portfolio-records">
      <div className="records-title">
        <div>
            <h2>Requested assessments <span>{loading ? '…' : cases.length}</span></h2>
            <p>{isDemoMode ? 'No simulated review cases' : 'Cases shared for expert review'}</p>
        </div>
        <span className="subtle-tag">{isDemoMode ? 'Demo mode' : 'Human review'}</span>
      </div>

      {!isDemoMode && (
        <>
          <div className="portfolio-toolbar"><label className="portfolio-search"><Search size={16}/><span className="sr-only">Search review queue</span><input type="search" value={search} onChange={e => setSearch(e.target.value)} placeholder="Search case, farm, field or organization…"/></label><div className="portfolio-selects"><select aria-label="Status" value={statusFilter} onChange={e => setStatusFilter(e.target.value as ReviewStatus | 'all')}><option value="all">All statuses</option><option value="awaiting_review">Awaiting review</option><option value="reviewed">Reviewed</option><option value="needs_inspection">Needs inspection</option></select><select aria-label="Sort order" value={sortBy} onChange={e => setSortBy(e.target.value as 'priority' | 'date')}><option value="priority">Priority first</option><option value="date">Newest first</option></select></div></div>
          <details className="review-filters"><summary><Filter size={14}/>Refine the queue{(severityFilter !== 'all' || diseaseFilter !== 'all' || confidenceMin > 0) && <span>Filters active</span>}</summary><div><label>Severity<select aria-label="Severity" value={severityFilter} onChange={e => setSeverityFilter(e.target.value)}><option value="all">All severities</option>{['Early', 'Moderate', 'Severe', 'Uncertain'].map(value => <option key={value}>{value}</option>)}</select></label><label>Disease signal<select aria-label="Disease signal" value={diseaseFilter} onChange={e => setDiseaseFilter(e.target.value)}><option value="all">All indications</option><option value="Rust">Soybean rust</option><option value="Blight">Bacterial blight</option><option value="Frogeye">Frogeye leaf spot</option></select></label><label>Minimum confidence<select aria-label="Minimum confidence" value={confidenceMin} onChange={e => setConfidenceMin(Number(e.target.value))}><option value={0}>Any confidence</option><option value={50}>At least 50%</option><option value={75}>At least 75%</option><option value={85}>At least 85%</option></select></label><button className="action secondary" onClick={handleResetFilters}>Clear all filters</button></div></details>
        </>
      )}

      {loading ? (
        <div className="portfolio-loading" role="status" aria-busy="true"><RotateCcw size={17} className="ui-spinner"/>Updating the review queue…</div>
      ) : isDemoMode ? (
        <div className="p-6 space-y-4 bg-pure-surface rounded-2xl border border-structural text-xs">
          <div className="flex items-center gap-3">
            <ClipboardList size={28} className="text-muted-leaf shrink-0" />
            <div>
              <h3 className="font-bold text-sm text-field-ink">Demo Context: 0 Real Review Cases</h3>
              <p className="text-muted-leaf mt-0.5">
                The demonstration workspace contains <strong>6 farms</strong> and <strong>12 soybean fields</strong> owned by <strong>Rakshak Demo Farmer</strong> (<code>farmer@rakshak.local</code>) under <strong>Rakshak Demonstration Cooperative</strong>.
                Fasal Rakshak AI never fabricates artificial AI diagnoses, confidence metrics, or review cases.
              </p>
            </div>
          </div>
          <div className="p-4 bg-field-canvas rounded-xl border border-structural space-y-2">
            <div className="font-bold text-field-ink text-xs">Seeded Demo Infrastructure (Rakshak Demo Farmer):</div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
              {[
                { farm: "Narmada Field Collective", district: "Sehore", fields: "North Plot 1, South Plot 1" },
                { farm: "Green Ridge Farm", district: "Sehore", fields: "North Plot 2, South Plot 2" },
                { farm: "Riverbend Soybean Farm", district: "Dewas", fields: "North Plot 3, South Plot 3" },
                { farm: "Sankalp Field Group", district: "Dewas", fields: "North Plot 4, South Plot 4" },
                { farm: "Ujjain Crop Circle", district: "Ujjain", fields: "North Plot 5, South Plot 5" },
                { farm: "Malwa Demonstration Farm", district: "Ujjain", fields: "North Plot 6, South Plot 6" },
              ].map(item => (
                <div key={item.farm} className="p-2.5 bg-pure-surface rounded-lg border border-structural">
                  <p className="font-bold text-field-ink">{item.farm}</p>
                  <p className="text-[11px] text-muted-leaf">{item.district} District · 2 fields</p>
                  <p className="text-[10px] font-mono text-muted-leaf mt-1">{item.fields}</p>
                </div>
              ))}
            </div>
          </div>
          <div className="flex items-center justify-between pt-1">
            <span className="text-muted-leaf">Currently 0 real review cases submitted. To review real field video evidence, switch to a live workspace.</span>
            <button className="action secondary text-xs py-1.5 px-3" onClick={() => setDemoMode(false)}>
              Switch to Live workspace
            </button>
          </div>
        </div>
      ) : !cases.length ? (
        <div className="portfolio-empty">
          <ClipboardList size={30}/>
          <h3>No matching cases</h3>
          <p>New requests appear when a farmer asks for review. Clear filters to see all accessible cases.</p>
          <button className="action secondary" onClick={handleResetFilters}>Show all cases</button>
        </div>
      ) : (
        <div className="review-table-wrap" tabIndex={0} role="region" aria-label="Review cases, scroll horizontally for all columns">
          <p className="table-scroll-hint">Scroll across to see all case details and actions.</p>
          <table className="review-table">
            <thead>
              <tr>
                <th>Field / organization</th>
                <th>AI perspective</th>
                <th>Requested</th>
                <th>Review status</th>
                <th><span className="sr-only">Open case</span></th>
              </tr>
            </thead>
            <tbody>
              {cases.map(c => (
                <tr key={c.id}>
                  <td>
                    <Link className="review-field-name" to={`/agronomist/cases/${c.id}`}>{c.fieldName}</Link>
                    <p>{c.farmName} · {c.fpoName}</p>
                    <small>{c.crop}{c.priority === 'high' ? ' · High priority' : ''}</small>
                  </td>
                  <td>
                    <strong>{c.aiIndication}</strong>
                    <p>{c.confidence}% confidence · {c.severity}</p>
                  </td>
                  <td><span>{new Date(c.submittedAt).toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' })}</span></td>
                  <td><ReviewStatusBadge status={c.reviewStatus}/></td>
                  <td><Link className="record-open" to={`/agronomist/cases/${c.id}`}>Review evidence <ExternalLink size={14}/></Link></td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="records-bottom">Showing {cases.length} {cases.length === 1 ? 'case' : 'cases'}<span>Queue counts reflect filters; review history is account-wide</span></div>
        </div>
      )}
    </section>
    <p className="portfolio-disclaimer"><AlertTriangle size={14}/>Model indications are advisory. Inspect the original evidence before recording your assessment.</p>
  </div>;
};

