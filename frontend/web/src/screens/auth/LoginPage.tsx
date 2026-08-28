import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowRight, Check, Eye, EyeOff, Sprout } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { PublicNavbar } from '../../components/layout/PublicNavbar';
import { UserRole } from '../../types';

const dashboardFor = (role: UserRole) => role === 'agronomist' ? '/agronomist/dashboard' : '/organization/dashboard';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleFormSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!email.trim() || !password.trim()) {
      setError('Enter your email and password to continue.');
      return;
    }
    setError('');
    setSubmitting(true);
    try {
      const assignedRole = await login(email, password);
      navigate(dashboardFor(assignedRole), { replace: true });
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'We could not sign you in. Check your details and try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return <div className="min-h-screen bg-field-canvas text-field-ink">
    <PublicNavbar />
    <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-20 grid lg:grid-cols-[0.85fr_1.15fr] gap-12 items-start">
      <section className="space-y-6 lg:pt-8">
        <Link to="/" className="inline-flex items-center gap-2.5"><span className="w-11 h-11 rounded-2xl bg-field-ink text-lime-signal flex items-center justify-center"><Sprout size={23} /></span><span className="font-extrabold text-lg">Rakshak AI</span></Link>
        <div className="space-y-3"><p className="text-xs font-mono uppercase tracking-[0.16em] text-muted-leaf">Secure workspace access</p><h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-balance">Work from the signal, not the noise.</h1><p className="text-sm leading-6 text-muted-leaf max-w-md">Sign in with your organization account. Your database-assigned role determines the workspace and permissions available to you.</p></div>
        <ul className="space-y-3 text-sm text-muted-leaf">{['Role-based access from your account', 'Evidence-led crop health signals', 'Human review before field action'].map((item) => <li key={item} className="flex items-center gap-2"><Check size={16} className="text-field-ink" />{item}</li>)}</ul>
      </section>
      <section className="bg-pure-surface border border-structural rounded-3xl p-6 sm:p-8 shadow-lg">
        <div className="space-y-2 mb-7"><h2 className="text-2xl font-extrabold">Sign in</h2><p className="text-sm text-muted-leaf">Use the email associated with your Rakshak AI account.</p></div>
        <form onSubmit={handleFormSubmit} className="space-y-5">
          <div><label htmlFor="login-email" className="block text-sm font-semibold mb-2">Email address</label><input id="login-email" type="email" value={email} onChange={(event) => setEmail(event.target.value)} autoComplete="email" placeholder="name@organization.com" className="w-full p-3 rounded-xl border border-structural bg-field-canvas text-sm outline-none focus:ring-2 focus:ring-field-ink/20" /></div>
          <div><div className="flex justify-between mb-2"><label htmlFor="login-password" className="text-sm font-semibold">Password</label><Link to="/forgot-password" className="text-xs font-semibold text-muted-leaf hover:text-field-ink">Forgot password?</Link></div><div className="relative"><input id="login-password" type={showPassword ? 'text' : 'password'} value={password} onChange={(event) => setPassword(event.target.value)} autoComplete="current-password" placeholder="Enter your password" className="w-full p-3 pr-11 rounded-xl border border-structural bg-field-canvas text-sm outline-none focus:ring-2 focus:ring-field-ink/20" /><button type="button" aria-label={showPassword ? 'Hide password' : 'Show password'} onClick={() => setShowPassword((visible) => !visible)} className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-leaf hover:text-field-ink">{showPassword ? <EyeOff size={17} /> : <Eye size={17} />}</button></div></div>
          {error && <p role="alert" className="rounded-xl border border-red-200 bg-red-50 px-3 py-2.5 text-sm text-alert-red">{error}</p>}
          <button type="submit" disabled={submitting} className="w-full py-3.5 bg-field-ink text-white font-bold rounded-xl hover:bg-opacity-90 disabled:opacity-60 transition flex items-center justify-center gap-2">{submitting ? 'Signing in...' : 'Continue to workspace'} {!submitting && <ArrowRight size={16} className="text-lime-signal" />}</button>
        </form>
        <p className="mt-6 pt-5 border-t border-structural text-sm text-muted-leaf">Need access? <Link to="/contact" className="font-bold text-field-ink hover:underline">Contact your administrator</Link> <span className="mx-1">·</span> <Link to="/register" className="font-bold text-field-ink hover:underline">Request access</Link></p>
      </section>
    </main>
  </div>;
};
