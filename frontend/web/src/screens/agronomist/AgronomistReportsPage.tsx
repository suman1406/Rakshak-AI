import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Database } from 'lucide-react';
import { apiClient } from '../../services/apiClient';
import { downloadCsv } from '../../services/reportExport';
import { useDemoMode } from '../../context/DemoModeContext';

type Review = { id: string; diagnosis_id: string; field_name: string; reviewed_at: string; is_healthy: boolean; severity_level: number; notes: string | null; elapsed_minutes: number };

export const AgronomistReportsPage: React.FC = () => {
  const { enabled: isDemoMode, setEnabled: setDemoMode } = useDemoMode();
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  async function load() {
    setLoading(true); setError('');
    try {
      if (isDemoMode) {
        setReviews([]);
        setLoading(false);
        return;
      }
      setReviews(await apiClient.getAgronomistReviews());
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not load reviews');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void load(); }, [isDemoMode]);

  return <div className="farmer-workspace">
    <header className="workspace-heading">
      <div>
        <p className="eyebrow">EXPERT AUDIT</p>
        <h1>Your completed reviews</h1>
        <p>{isDemoMode ? 'Demo workspace does not include completed expert reviews.' : 'Latest 500 records. Elapsed time is measured from upload to review, including queue time.'}</p>
      </div>
      {!isDemoMode && <button className="action secondary" disabled={!reviews.length || loading || !!error} onClick={() => downloadCsv('rakshak-reviews.csv', [['Review reference', 'Field', 'Reviewed at', 'Healthy override', 'Visual severity', 'Elapsed minutes', 'Notes'], ...reviews.map(review => [review.id, review.field_name, review.reviewed_at, review.is_healthy, review.severity_level, review.elapsed_minutes, review.notes])])}>Download CSV</button>}
    </header>

    {isDemoMode && (
      <section className="rounded-2xl border border-amber-200 bg-amber-50 p-4 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2.5 text-amber-900 font-semibold">
          <Database size={17} className="shrink-0 text-amber-800" />
          <span>No demo reports are included. Reports are created only from real processed field evidence.</span>
        </div>
        <button className="action secondary text-xs py-1.5 px-3" onClick={() => setDemoMode(false)}>
          Switch to Live workspace
        </button>
      </section>
    )}

    {error && <p role="alert">{error}</p>}
    {!isDemoMode && <button className="text-action" disabled={loading} onClick={() => void load()}>Refresh</button>}

    <section className="workspace-panel">
      {loading ? (
        <p>Loading review records…</p>
      ) : isDemoMode ? (
        <p className="text-muted-leaf">No demo reports are included. Reports are created only from real processed field evidence.</p>
      ) : !reviews.length ? (
        <p>Your completed reviews will appear here.</p>
      ) : (
        <ul className="scan-list">{reviews.map(review => <li key={review.id}><div><strong>{review.field_name}</strong><p>{new Date(review.reviewed_at).toLocaleString()}</p><p>{review.notes || 'No notes recorded'}</p></div><Link className="text-action" to={`/agronomist/cases/${review.diagnosis_id}`}>View evidence</Link></li>)}</ul>
      )}
    </section>
  </div>;
};

