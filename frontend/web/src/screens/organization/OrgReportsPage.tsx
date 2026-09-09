import React, { useEffect, useState } from 'react';
import { liveWorkspaceApi } from '../../services/liveWorkspaceApi';
import { exportFields } from '../../services/reportExport';
import { Farm } from '../../types';

export const OrgReportsPage: React.FC = () => {
  const [farms, setFarms] = useState<Farm[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  async function load() {
    setLoading(true); setError('');
    try { setFarms(await liveWorkspaceApi.getFarms()); }
    catch (e) { setError(e instanceof Error ? e.message : 'Could not load records'); }
    finally { setLoading(false); }
  }
  useEffect(() => { void load(); }, []);
  const count = farms.reduce((sum, farm) => sum + farm.fields.length, 0);
  return <div className="farmer-workspace"><header className="workspace-heading"><div><p className="eyebrow">ORGANIZATION RECORDS</p><h1>Field reports</h1><p>Download the latest assessment for each field in your organization.</p></div></header><section className="workspace-panel"><h2>Field assessment register</h2>{error ? <p role="alert">{error}</p> : <p>{loading ? 'Loading your records…' : `${count} fields across ${farms.length} farms. The export includes dates, indications and visual severity.`}</p>}<p className="safety-copy">Exports contain private field records. Share them only with authorized members. AI assessments remain advisory.</p><div className="workspace-actions"><button className="action" disabled={loading || !count || !!error} onClick={() => exportFields(farms)}>Download CSV</button><button className="action secondary" disabled={loading} onClick={() => void load()}>Refresh records</button></div></section></div>;
};
