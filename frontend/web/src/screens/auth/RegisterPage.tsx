import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import { AuthShell } from '../../components/ui/auth-shell';
import { Button } from '../../components/ui/button';
import { apiClient } from '../../services/apiClient';
export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const [name, setName] = useState(''); const [email, setEmail] = useState(''); const [password, setPassword] = useState(''); const [consent, setConsent] = useState(false); const [busy, setBusy] = useState(false); const [error, setError] = useState('');
  async function submit(event: React.FormEvent) {
    event.preventDefault(); setError(''); setBusy(true);
    try { await apiClient.register({ display_name: name.trim(), email: email.trim(), password, consent_to_data_processing: consent }); navigate('/login', { replace: true, state: { registered: true } }); }
    catch (e) { setError(e instanceof Error ? e.message : 'Could not create your account. Please try again.'); }
    finally { setBusy(false); }
  }
  return <AuthShell title="Start with your field." description="Create your farmer account. Add a field, then record your first observation."><form className="workspace-form" onSubmit={submit}><label htmlFor="register-name">Your name<input id="register-name" required maxLength={255} autoComplete="name" value={name} onChange={e => setName(e.target.value)} /></label><label htmlFor="register-email">Email address<input id="register-email" type="email" required autoComplete="email" value={email} onChange={e => setEmail(e.target.value)} /></label><label htmlFor="register-password">Password<input id="register-password" type="password" required minLength={8} maxLength={72} autoComplete="new-password" value={password} onChange={e => setPassword(e.target.value)} aria-describedby="password-guidance" /></label><p id="password-guidance" className="helper-copy">Use at least 8 characters.</p><label className="consent-control"><input type="checkbox" required checked={consent} onChange={e => setConsent(e.target.checked)} /><span>I agree to account and field-data processing as described in the <Link to="/privacy">privacy notice</Link>. Optional training use is a separate choice.</span></label>{error && <div className="message error" role="alert">{error}</div>}<Button type="submit" busy={busy} disabled={!consent || !name.trim()}>{busy ? 'Creating account…' : 'Create farmer account'}{!busy && <ArrowRight size={18} />}</Button></form><div className="auth-alternate"><p>Already have an account? <Link to="/login">Sign in</Link></p><p>Joining as an agronomist or organization? <Link to="/onboarding">Choose your workspace</Link></p></div></AuthShell>;
};
export const ForgotPasswordPage: React.FC = () => <AuthShell title="Let's get you back in." description="If you cannot sign in, contact the team for account-recovery support."><p>Automatic email recovery is not enabled for this pilot. For your privacy, changing account access requires verification by the support team.</p><div className="workspace-form"><Button asChild><Link to="/contact">Contact support <ArrowRight size={18} /></Link></Button><Button asChild variant="secondary"><Link to="/login">Return to sign in</Link></Button></div></AuthShell>;
