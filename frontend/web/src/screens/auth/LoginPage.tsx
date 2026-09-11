import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { ArrowRight, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { AuthShell } from '../../components/ui/auth-shell';
import { Button } from '../../components/ui/button';
import { UserRole } from '../../types';
const dashboardFor = (role: UserRole) => role === 'farmer' ? '/farmer' : role === 'agronomist' ? '/agronomist/dashboard' : role === 'admin' ? '/admin/dashboard' : '/organization/dashboard';
export const LoginPage: React.FC = () => {
  const { login, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const admin = location.pathname === '/admin/access';
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [visible, setVisible] = useState(false);
  async function submit(event: React.FormEvent) {
    event.preventDefault(); setError(''); setBusy(true);
    try { const role = await login(email.trim(), password); if (admin && role !== 'admin') { logout(); setError('This account does not have administrator access.'); return; } navigate(dashboardFor(role), { replace: true }); }
    catch (e) { setError(e instanceof Error ? e.message : 'Could not sign in. Please try again.'); }
    finally { setBusy(false); }
  }
  return <AuthShell title={admin ? 'Administrator sign in' : 'Welcome back.'} description={admin ? 'Use your personal administrator account.' : 'Your fields and observations are waiting for you.'}>
    {location.state?.registered && <div className="message" role="status">Your farmer account is ready. Sign in to add your first field.</div>}
    <form className="workspace-form" onSubmit={submit}><label htmlFor="login-email">Email or phone<input id="login-email" autoComplete="username" required value={email} onChange={e => setEmail(e.target.value)} /></label><div><div className="label-row"><label htmlFor="login-password">Password</label>{!admin && <Link to="/forgot-password">Need help signing in?</Link>}</div><div className="password-control"><input id="login-password" type={visible ? 'text' : 'password'} autoComplete="current-password" required value={password} onChange={e => setPassword(e.target.value)} /><Button type="button" variant="ghost" size="icon" aria-label={visible ? 'Hide password' : 'Show password'} onClick={() => setVisible(!visible)}>{visible ? <EyeOff size={18} /> : <Eye size={18} />}</Button></div></div>{error && <div className="message error" role="alert">{error}</div>}<Button type="submit" busy={busy}>{busy ? 'Signing in…' : 'Continue to workspace'}{!busy && <ArrowRight size={18} />}</Button></form>{!admin && <div className="auth-alternate"><p>New to Rakshak? <Link to="/register">Create a farmer account</Link></p><p>Working with a team? <Link to="/onboarding">Apply for expert or organization access</Link></p></div>}
  </AuthShell>;
};
