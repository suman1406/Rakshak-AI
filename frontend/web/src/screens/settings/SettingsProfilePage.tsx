import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { apiClient } from '../../services/apiClient';
import { useAuth } from '../../context/AuthContext';
import { Button } from '../../components/ui/button';
export const SettingsLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const location = useLocation(); const { role } = useAuth();
  const tabs = [{ name: 'Profile', path: '/settings/profile' }, ...(['enterprise','admin','org_admin'].includes(role || '') ? [{ name: 'Organization', path: '/settings/organization' }] : []), { name: 'Scan updates', path: '/settings/notifications' }, { name: 'Security & consent', path: '/settings/security' }];
  return <div className="farmer-workspace settings-workspace"><header className="workspace-heading"><div><h1>Your settings</h1><p>Manage your account and how your records are used.</p></div></header><nav className="settings-tabs" aria-label="Settings sections">{tabs.map(tab => <Link key={tab.path} to={tab.path} aria-current={location.pathname === tab.path ? 'page' : undefined}>{tab.name}</Link>)}</nav><section className="workspace-panel">{children}</section></div>;
};
export const SettingsProfilePage: React.FC = () => {
  const { user, role, refreshUser } = useAuth();
  const [name, setName] = useState(user?.name || ''); const [busy, setBusy] = useState(false); const [error, setError] = useState(''); const [message, setMessage] = useState('');
  async function save(event: React.FormEvent) { event.preventDefault(); setBusy(true); setError(''); setMessage(''); try { await apiClient.updateProfile({ display_name: name.trim() }); await refreshUser(); setMessage('Your profile is saved.'); } catch (e) { setError(e instanceof Error ? e.message : 'Could not save your profile'); } finally { setBusy(false); } }
  return <SettingsLayout><h2>Your profile</h2><form className="workspace-form" onSubmit={save}><label htmlFor="profile-name">Your name<input id="profile-name" value={name} onChange={e => setName(e.target.value)} required maxLength={255} autoComplete="name" /></label><dl className="profile-details"><div><dt>Account</dt><dd>{user?.email}</dd></div><div><dt>Workspace role</dt><dd>{role?.replace('_',' ')}</dd></div></dl>{error && <p role="alert" className="message error">{error}</p>}{message && <p role="status" className="message">{message}</p>}<Button busy={busy} disabled={!name.trim()}>{busy ? 'Saving…' : 'Save profile'}</Button></form></SettingsLayout>;
};
