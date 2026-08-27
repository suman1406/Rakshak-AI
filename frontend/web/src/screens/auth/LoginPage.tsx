import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { UserRole } from '../../types';
import { Sprout, ArrowRight, Check } from 'lucide-react';
import { PublicNavbar } from '../../components/layout/PublicNavbar';

const workspaces: { role: UserRole; title: string; description: string }[] = [
  { role: 'agronomist', title: 'Agronomist review', description: 'Review cases, inspect evidence, and record expert decisions.' },
  { role: 'org_admin', title: 'Organization analytics', description: 'Monitor farms, fields, risk signals, and reports.' },
];

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [selectedRole, setSelectedRole] = useState<UserRole>('agronomist');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError('Enter your email and password to continue.');
      return;
    }
    setError('');
    setSubmitting(true);
    try {
      await login(selectedRole, email, password);
      navigate('/onboarding');
    } catch {
      setError('We could not sign you in. Check your details and try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-field-canvas text-field-ink">
      <PublicNavbar />
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-20 grid lg:grid-cols-[0.85fr_1.15fr] gap-12 items-start">
        <section className="space-y-6 lg:pt-8">
          <Link to="/" className="inline-flex items-center gap-2.5">
            <span className="w-11 h-11 rounded-2xl bg-field-ink text-lime-signal flex items-center justify-center"><Sprout size={23} /></span>
            <span className="font-extrabold text-lg">Rakshak AI</span>
          </Link>
          <div className="space-y-3">
            <p className="text-xs font-mono uppercase tracking-[0.16em] text-muted-leaf">Secure workspace access</p>
            <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-balance">Work from the signal, not the noise.</h1>
            <p className="text-sm leading-6 text-muted-leaf max-w-md">Sign in to review crop-health evidence or understand the health of your organization’s monitored fields.</p>
          </div>
          <ul className="space-y-3 text-sm text-muted-leaf">
            {['Evidence-led crop health signals', 'Role-specific access and navigation', 'Human review before field action'].map((item) => <li key={item} className="flex items-center gap-2"><Check size={16} className="text-field-ink" />{item}</li>)}
          </ul>
        </section>

        <section className="bg-pure-surface border border-structural rounded-3xl p-6 sm:p-8 shadow-lg">
          <div className="space-y-2 mb-7"><h2 className="text-2xl font-extrabold">Sign in</h2><p className="text-sm text-muted-leaf">Choose your workspace, then enter your account details.</p></div>
          <form onSubmit={handleFormSubmit} className="space-y-5">
            <fieldset className="space-y-3"><legend className="text-sm font-bold mb-2">Workspace</legend>{workspaces.map((workspace) => <button key={workspace.role} type="button" onClick={() => setSelectedRole(workspace.role)} className={`w-full text-left p-4 rounded-2xl border transition ${selectedRole === workspace.role ? 'border-field-ink bg-soft-healthy' : 'border-structural bg-field-canvas hover:border-muted-leaf'}`}><span className="flex items-start justify-between gap-4"><span><span className="block text-sm font-bold">{workspace.title}</span><span className="block text-xs text-muted-leaf mt-1">{workspace.description}</span></span>{selectedRole === workspace.role && <Check size={18} className="shrink-0 mt-0.5" />}</span></button>)}</fieldset>
            <div><label htmlFor="login-email" className="block text-sm font-semibold mb-2">Email address</label><input id="login-email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} autoComplete="email" placeholder="name@organization.com" className="w-full p-3 rounded-xl border border-structural bg-field-canvas text-sm outline-none focus:ring-2 focus:ring-field-ink/20" /></div>
            <div><div className="flex justify-between mb-2"><label htmlFor="login-password" className="text-sm font-semibold">Password</label><Link to="/forgot-password" className="text-xs font-semibold text-muted-leaf hover:text-field-ink">Forgot password?</Link></div><input id="login-password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete="current-password" placeholder="Enter your password" className="w-full p-3 rounded-xl border border-structural bg-field-canvas text-sm outline-none focus:ring-2 focus:ring-field-ink/20" /></div>
            {error && <p role="alert" className="rounded-xl border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-alert-red">{error}</p>}
            <button type="submit" disabled={submitting} className="w-full py-3.5 bg-field-ink text-white font-bold rounded-xl hover:bg-opacity-90 disabled:opacity-60 transition flex items-center justify-center gap-2">{submitting ? 'Signing in...' : 'Continue to workspace'} {!submitting && <ArrowRight size={16} className="text-lime-signal" />}</button>
          </form>
          <p className="mt-6 pt-5 border-t border-structural text-sm text-muted-leaf">Need access? <Link to="/register" className="font-bold text-field-ink hover:underline">Create an account</Link></p>
        </section>
      </main>
    </div>
  );
};
