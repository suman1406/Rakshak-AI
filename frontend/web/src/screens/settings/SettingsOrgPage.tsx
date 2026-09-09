import React, { useEffect, useState } from 'react';
import { SettingsLayout } from './SettingsProfilePage';
import { apiClient } from '../../services/apiClient';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

export function SettingsOrgPage() {
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState('');
  useEffect(() => { apiClient.getB2BDashboard().then(setData).catch(e => setError(e.message)); }, []);
  return <SettingsLayout><h2 className="text-xl font-semibold mb-4">Your organization</h2>{error ? <p role="alert">{error}</p> : !data ? <p>Loading organization records…</p> : <dl className="report-facts"><div><dt>Organization</dt><dd>{data.organization_name || 'No organization assigned'}</dd></div><div><dt>Farms</dt><dd>{data.total_farms}</dd></div><div><dt>Fields</dt><dd>{data.total_fields}</dd></div></dl>}</SettingsLayout>;
}

export function SettingsNotificationsPage() {
  return <SettingsLayout><h2 className="text-xl font-semibold mb-4">Scan updates</h2><p>Processing status and completed assessments are available in your workspace. SMS and WhatsApp delivery are not enabled for this release.</p></SettingsLayout>;
}

export function SettingsSecurityPage() {
  const { logout } = useAuth();
  const [consent, setConsent] = useState<boolean | null>(null);
  const [current, setCurrent] = useState('');
  const [password, setPassword] = useState('');
  const [confirmation, setConfirmation] = useState('');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  useEffect(() => { apiClient.getCurrentUser().then(user => setConsent(user.training_consent)).catch(e => setError(e.message)); }, []);
  async function run(action: () => Promise<unknown>, success: string) {
    setBusy(true); setError(''); setMessage('');
    try { await action(); setMessage(success); } catch (e) { setError(e instanceof Error ? e.message : 'Unable to save changes'); }
    finally { setBusy(false); }
  }
  return <SettingsLayout><h2 className="text-xl font-semibold mb-4">Security and consent</h2><div className="space-y-6">
    {error && <p role="alert">{error}</p>}{message && <p role="status">{message}</p>}
    <section><h3 className="font-semibold mb-2">Optional model training</h3><p className="mb-3">Allow your evidence and expert corrections to be included in future training exports. This is optional and does not affect scan processing. You can withdraw permission for future exports here.</p>
      <label className="flex gap-3 items-start"><input type="checkbox" checked={consent === true} disabled={busy || consent === null} onChange={e => { const accepted = e.target.checked; void run(async () => { await apiClient.updateProfile({ training_consent: accepted }); setConsent(accepted); }, 'Training preference saved'); }} />I agree to optional model-training use</label>
    </section>
    <form className="space-y-3" onSubmit={e => { e.preventDefault(); if (password !== confirmation) { setError('The new passwords do not match'); return; } void run(async () => { await apiClient.changePassword(current, password); logout(); }, 'Password changed'); }}>
      <h3 className="font-semibold">Change password</h3>
      <label className="block">Current password<input className="block border rounded p-3 w-full" type="password" autoComplete="current-password" value={current} onChange={e => setCurrent(e.target.value)} required /></label>
      <label className="block">New password<input className="block border rounded p-3 w-full" type="password" autoComplete="new-password" minLength={8} maxLength={72} value={password} onChange={e => setPassword(e.target.value)} required /></label>
      <label className="block">Repeat new password<input className="block border rounded p-3 w-full" type="password" autoComplete="new-password" value={confirmation} onChange={e => setConfirmation(e.target.value)} required /></label>
      <p>Changing your password signs you out on every device.</p><button className="border rounded px-4 py-3" disabled={busy}>Change password and sign out</button>
    </form>
    <section><h3 className="font-semibold mb-2">Active sessions</h3><p className="mb-3">Sign out on all devices, including this one.</p><button className="border rounded px-4 py-3" disabled={busy} onClick={() => void run(async () => { await apiClient.logoutAll(); logout(); }, 'Sessions signed out')}>Sign out everywhere</button></section>
    <Link className="text-action" to="/privacy">Read the privacy notice</Link></div></SettingsLayout>;
}
