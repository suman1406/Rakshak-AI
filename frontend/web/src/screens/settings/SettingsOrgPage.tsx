import React, { useEffect, useState } from 'react';
import { SettingsLayout } from './SettingsProfilePage';
import { apiClient } from '../../services/apiClient';
import { Link } from 'react-router-dom';

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
  return <SettingsLayout><h2 className="text-xl font-semibold mb-4">Security and consent</h2><div className="space-y-6"><p>Your account and field records are restricted by your role and organization. Video processing requires your consent at upload.</p><p>AI assessments describe visual indications, not confirmed diagnoses. Consult an agronomist when symptoms persist or spread.</p><Link className="text-action" to="/privacy">Read the privacy notice</Link></div></SettingsLayout>;
}
