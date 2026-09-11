import React, { useEffect, useState } from 'react';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { CheckCircle2 } from 'lucide-react';
import { apiClient } from '../../services/apiClient';
import { AuthShell } from '../../components/ui/auth-shell';
import { Button } from '../../components/ui/button';

const ORG_TYPES = [['fpo', 'Farmer producer organization'], ['insurer', 'Insurer'], ['input_company', 'Input company'], ['bank', 'Bank or lender'], ['gov', 'Government program'], ['research', 'Research institution'], ['other', 'Other organization']];
export const ApplicationPage: React.FC = () => {
  const { kind } = useParams<{ kind: 'agronomist' | 'organization' }>();
  const [search] = useSearchParams();
  const applicationType = kind === 'agronomist' ? 'agronomist' : 'organization';
  const [plans, setPlans] = useState<Array<{ code: string; name: string }>>([]);
  const [planError, setPlanError] = useState('');
  const [name, setName] = useState(''); const [email, setEmail] = useState(''); const [phrase, setPhrase] = useState('');
  const [organizationName, setOrganizationName] = useState(''); const [organizationType, setOrganizationType] = useState('fpo'); const [plan, setPlan] = useState(search.get('plan') || '');
  const [billing, setBilling] = useState<'monthly' | 'annual'>(search.get('billing') === 'annual' ? 'annual' : 'monthly');
  const [consent, setConsent] = useState(false); const [error, setError] = useState(''); const [receipt, setReceipt] = useState<{ reference: string; message: string } | null>(null); const [submitting, setSubmitting] = useState(false);
  useEffect(() => {
    if (applicationType !== 'organization') return;
    let active = true;
    apiClient.listPublicPlans().then(items => { if (active) { setPlans(items); setPlan(current => items.some(item => item.code === current) ? current : ''); } }).catch(() => { if (active) { setPlan(''); setPlanError('Plans could not be loaded. You can still apply and discuss a plan with the team.'); } });
    return () => { active = false; };
  }, [applicationType]);
  async function submit(event: React.FormEvent) {
    event.preventDefault(); setError('');
    if (new TextEncoder().encode(phrase).length > 72) { setError('Use a password of at most 72 bytes. Non-English characters can take more than one byte.'); return; }
    setSubmitting(true);
    try { setReceipt(await apiClient.submitApplication({ application_type: applicationType, display_name: name.trim(), email: email.trim(), access_phrase: phrase, consent_to_data_processing: consent, ...(applicationType === 'organization' ? { organization_name: organizationName.trim(), organization_type: organizationType, requested_plan_code: plan || undefined, requested_billing_interval: billing } : {}) })); }
    catch (reason) { setError(reason instanceof Error ? reason.message : 'We could not submit your application.'); }
    finally { setSubmitting(false); }
  }
  if (receipt) return <AuthShell title="Your application is saved." description="The team will review your request before enabling access."><div role="status" className="workspace-form"><CheckCircle2 size={32}/><p>Reference <strong className="request-reference">{receipt.reference}</strong></p><p>{receipt.message}</p><Button asChild><Link to="/login">Return to sign in</Link></Button><p>Need to follow up? <Link to="/contact">Contact the team</Link> with your reference.</p></div></AuthShell>;
  return <AuthShell title={applicationType === 'agronomist' ? 'Bring your expertise.' : 'Bring your field team.'} description={applicationType === 'agronomist' ? 'Apply for an agronomist workspace to review crop evidence.' : 'Request a shared workspace for your organization.'}><form className="workspace-form" onSubmit={submit}>
    <label>Your name<input required maxLength={255} autoComplete="name" value={name} onChange={e => setName(e.target.value)}/></label>
    <label>Email address<input required type="email" maxLength={320} autoComplete="email" value={email} onChange={e => setEmail(e.target.value)}/></label>
    <label>Choose a password<input required minLength={8} maxLength={72} type="password" autoComplete="new-password" value={phrase} onChange={e => setPhrase(e.target.value)}/></label><p className="helper-copy">At least 8 characters. You will use this to sign in once your request is approved.</p>
    {applicationType === 'organization' && <><label>Organization name<input required maxLength={255} autoComplete="organization" value={organizationName} onChange={e => setOrganizationName(e.target.value)}/></label><label>Organization type<select value={organizationType} onChange={e => setOrganizationType(e.target.value)}>{ORG_TYPES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>{plans.length > 0 && <label>Requested plan<select value={plan} onChange={e => setPlan(e.target.value)}><option value="">Discuss with the team</option>{plans.map(item => <option key={item.code} value={item.code}>{item.name}</option>)}</select></label>}<label>Requested billing period<select value={billing} onChange={e => setBilling(e.target.value as 'monthly' | 'annual')}><option value="monthly">Monthly</option><option value="annual">Annual</option></select></label>{planError && <p className="helper-copy" role="status">{planError}</p>}</>}
    <label className="consent-control"><input required checked={consent} onChange={e => setConsent(e.target.checked)} type="checkbox"/><span>I agree to data processing for reviewing and operating this request. <Link to="/privacy">Read the privacy notice.</Link></span></label>
    {error && <p role="alert" className="message error">{error}</p>}<Button busy={submitting} disabled={!consent || !name.trim() || (applicationType === 'organization' && !organizationName.trim())}>{submitting ? 'Submitting…' : 'Submit for review'}</Button>
    </form><div className="auth-alternate"><p>An administrator reviews every application. This request does not collect payment or activate a subscription.</p><p>Already approved? <Link to="/login">Sign in</Link></p></div></AuthShell>;
};
