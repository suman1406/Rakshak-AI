import React, { useEffect, useState } from 'react';
import { DatabaseZap, Database } from 'lucide-react';
import { apiClient } from '../../services/apiClient';
import { useDemoMode } from '../../context/DemoModeContext';

export const DemoDataPage: React.FC = () => {
  const { enabled, setEnabled, refresh } = useDemoMode();
  const [status, setStatus] = useState<{ available: boolean; videos: number; message: string } | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');

  const load = () => apiClient.getDemoDataStatus().then(setStatus).catch((reason) => setError(reason instanceof Error ? reason.message : 'Demo status could not be loaded.'));

  useEffect(() => { load(); }, []);

  const initialize = async () => {
    setBusy(true); setError('');
    try {
      await apiClient.initializeDemoData();
      await load();
      await refresh();
      setEnabled(true);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Demo data could not be initialized.');
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <p className="eyebrow">Controlled demonstration</p>
        <h1 className="mt-2 text-3xl font-extrabold text-field-ink">Demo data</h1>
        <p className="mt-2 text-sm text-muted-leaf">
          Initialize once, then every authenticated development user can independently switch between the shared demo and their live workspace.
        </p>
      </div>

      <section className="rounded-3xl border border-amber-200 bg-amber-50 p-6 space-y-4">
        <div className="flex gap-3">
          <DatabaseZap className="shrink-0 text-amber-800"/>
          <div>
            <h2 className="font-bold text-amber-950">No simulated video intelligence</h2>
            <p className="mt-1 text-sm text-amber-900">
              The demo creates soybean farms, fields, a cooperative, and pilot pricing. It creates no videos, diagnoses, evidence frames, or generated reports.
            </p>
          </div>
        </div>

        {error && <p role="alert" className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-alert-red">{error}</p>}

        <div className="flex flex-wrap gap-3">
          <button disabled={busy || Boolean(status?.available)} onClick={() => void initialize()} className="rounded-xl bg-field-ink px-4 py-3 text-xs font-bold text-white disabled:opacity-60">
            {status?.available ? 'Demo data initialized' : busy ? 'Initializing…' : 'Initialize demo data'}
          </button>
          {status?.available && (
            <button onClick={() => setEnabled(!enabled)} className="rounded-xl border border-amber-300 bg-white px-4 py-3 text-xs font-bold text-amber-950 flex items-center gap-2">
              <Database size={14} />
              <span>{enabled ? 'Switch to Live Workspace' : 'View Demo Workspace'}</span>
            </button>
          )}
        </div>
      </section>

      {status?.available && (
        <section className="rounded-3xl border border-structural bg-pure-surface p-6 space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="font-bold text-field-ink text-sm">Demo Workspace / Demo Member</h2>
            <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-[11px] font-bold text-amber-900">Synthetic Demo Member</span>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs pt-1">
            <div>
              <span className="text-[10px] text-muted-leaf uppercase font-mono block">Name</span>
              <span className="font-bold text-field-ink">Rakshak Demo Farmer</span>
            </div>
            <div>
              <span className="text-[10px] text-muted-leaf uppercase font-mono block">Email</span>
              <a href="mailto:farmer@rakshak.local" className="font-mono text-field-ink hover:underline">farmer@rakshak.local</a>
            </div>
            <div>
              <span className="text-[10px] text-muted-leaf uppercase font-mono block">Role</span>
              <span className="font-semibold text-field-ink">Farmer</span>
            </div>
            <div>
              <span className="text-[10px] text-muted-leaf uppercase font-mono block">Organization</span>
              <span className="font-semibold text-field-ink">Rakshak Demonstration Cooperative</span>
            </div>
            <div>
              <span className="text-[10px] text-muted-leaf uppercase font-mono block">Farms</span>
              <span className="font-mono font-bold text-field-ink">6 farms</span>
            </div>
            <div>
              <span className="text-[10px] text-muted-leaf uppercase font-mono block">Fields</span>
              <span className="font-mono font-bold text-field-ink">12 fields</span>
            </div>
          </div>
        </section>
      )}

      {status && <p className="rounded-xl border border-structural bg-pure-surface p-4 text-sm text-muted-leaf">{status.message}</p>}
    </div>
  );
};

