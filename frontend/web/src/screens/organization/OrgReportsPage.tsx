import React, { useEffect, useState } from 'react';
import { Database } from 'lucide-react';
import { liveWorkspaceApi } from '../../services/liveWorkspaceApi';
import { exportFields } from '../../services/reportExport';
import { useDemoMode } from '../../context/DemoModeContext';
import { Farm } from '../../types';

export const OrgReportsPage: React.FC = () => {
  const { enabled: isDemoMode, setEnabled: setDemoMode } = useDemoMode();
  const [farms, setFarms] = useState<Farm[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  async function load() {
    setLoading(true); setError('');
    try {
      if (isDemoMode) {
        setFarms([]);
        setLoading(false);
        return;
      }
      setFarms(await liveWorkspaceApi.getFarms());
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not load records');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { void load(); }, [isDemoMode]);

  const count = farms.reduce((sum, farm) => sum + farm.fields.length, 0);

  return <div className="farmer-workspace">
    <header className="workspace-heading">
      <div>
        <p className="eyebrow">ORGANIZATION RECORDS</p>
        <h1>Field reports</h1>
        <p>{isDemoMode ? 'Demo workspace contains no generated report files.' : 'Download the latest assessment for each field in your organization.'}</p>
      </div>
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

    <section className="workspace-panel">
      <h2>Field assessment register</h2>
      {error ? (
        <p role="alert">{error}</p>
      ) : isDemoMode ? (
        <p className="text-muted-leaf">No demo reports are included. Reports are created only from real processed field evidence.</p>
      ) : (
        <p>{loading ? 'Loading your records…' : `${count} fields across ${farms.length} farms. The export includes dates, indications and visual severity.`}</p>
      )}
      {!isDemoMode && <p className="safety-copy">Exports contain private field records. Share them only with authorized members. AI assessments remain advisory.</p>}
      <div className="workspace-actions">
        <button className="action" disabled={isDemoMode || loading || !count || !!error} onClick={() => exportFields(farms)}>Download CSV</button>
        {!isDemoMode && <button className="action secondary" disabled={loading} onClick={() => void load()}>Refresh records</button>}
      </div>
    </section>
  </div>;
};

