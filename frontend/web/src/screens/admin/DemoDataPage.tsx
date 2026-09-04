import React, { useEffect, useState } from 'react';
import { DatabaseZap } from 'lucide-react';
import { apiClient } from '../../services/apiClient';

export const DemoDataPage: React.FC = () => {
  const [status, setStatus] = useState<{ available: boolean; videos: number; message: string } | null>(null);
  const [busy, setBusy] = useState(false); const [error, setError] = useState('');
  const load = () => apiClient.getDemoDataStatus().then(setStatus).catch((reason) => setError(reason instanceof Error ? reason.message : 'Demo status could not be loaded.'));
  useEffect(() => { load(); }, []);
  const initialize = async () => { setBusy(true); setError(''); try { await apiClient.initializeDemoData(); await load(); } catch (reason) { setError(reason instanceof Error ? reason.message : 'Demo data could not be initialized.'); } finally { setBusy(false); } };
  return <div className="mx-auto max-w-2xl space-y-6"><div><p className="eyebrow">Controlled demonstration</p><h1 className="mt-2 text-3xl font-extrabold text-field-ink">Demo data</h1><p className="mt-2 text-sm text-muted-leaf">This is separate from live operations and only an administrator can initialize it.</p></div><section className="rounded-3xl border border-amber-200 bg-amber-50 p-6 space-y-4"><div className="flex gap-3"><DatabaseZap className="shrink-0 text-amber-800"/><div><h2 className="font-bold text-amber-950">No simulated video intelligence</h2><p className="mt-1 text-sm text-amber-900">The demo creates soybean farms, fields, a cooperative, and pilot pricing. It creates no videos, diagnoses, evidence frames, or generated reports.</p></div></div>{error && <p role="alert" className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-alert-red">{error}</p>}<button disabled={busy || status?.available} onClick={() => void initialize()} className="rounded-xl bg-field-ink px-4 py-3 text-xs font-bold text-white disabled:opacity-60">{status?.available ? 'Demo data initialized' : busy ? 'Initializing…' : 'Initialize demo data'}</button></section>{status && <p className="rounded-xl border border-structural bg-pure-surface p-4 text-sm text-muted-leaf">{status.message}</p>}</div>;
};
