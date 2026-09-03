import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sprout } from 'lucide-react';
import { PublicNavbar } from '../../components/layout/PublicNavbar';
import { apiClient } from '../../services/apiClient';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!apiClient.isConfigured()) {
      setError('Registration service is not configured. Set NEXT_PUBLIC_API_URL and try again.');
      return;
    }
    setError('');
    setSubmitting(true);
    try {
      await apiClient.register({ display_name: name.trim(), email: email.trim(), password });
      navigate('/login', { replace: true, state: { registered: true } });
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'We could not create the account. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-field-canvas font-sans">
      <PublicNavbar />
      <div className="flex items-center justify-center p-4 py-12">
      <div className="max-w-md w-full bg-pure-surface border border-structural p-8 rounded-3xl shadow-sm space-y-6">
        <div className="text-center space-y-2">
          <Link to="/" className="inline-flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-field-ink text-lime-signal flex items-center justify-center font-bold">
              <Sprout size={22} />
            </div>
          </Link>
          <h1 className="text-2xl font-extrabold text-field-ink">Register for Rakshak AI</h1>
          <p className="text-xs text-muted-leaf">Create a farmer account for the Rakshak mobile app</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div>
            <label className="block font-semibold mb-1">Full Name</label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Ramesh Patil"
              className="w-full p-2.5 rounded-xl border border-structural bg-field-canvas text-xs outline-none"
            />
          </div>

          <div>
            <label className="block font-semibold mb-1">Password</label>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
              placeholder="At least 8 characters"
              className="w-full p-2.5 rounded-xl border border-structural bg-field-canvas text-xs outline-none"
            />
          </div>

          {error && <p role="alert" className="rounded-xl border border-red-200 bg-red-50 p-3 text-alert-red">{error}</p>}

          <div>
            <label className="block font-semibold mb-1">Email Address</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="ramesh@example.com"
              className="w-full p-2.5 rounded-xl border border-structural bg-field-canvas text-xs outline-none"
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-3 bg-field-ink text-white font-bold rounded-xl hover:bg-opacity-90 disabled:opacity-60 transition"
          >
            {submitting ? 'Creating account...' : 'Create farmer account'}
          </button>
        </form>

        <div className="text-center text-xs text-muted-leaf pt-2 border-t border-structural">
          Already registered for a workspace?{' '}
          <Link to="/login" className="font-bold text-field-ink hover:underline">
            Sign in
          </Link>
        </div>
      </div>
      </div>
    </div>
  );
};

export const ForgotPasswordPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-field-canvas font-sans">
      <PublicNavbar />
      <div className="flex items-center justify-center p-4 py-12">
      <div className="max-w-md w-full bg-pure-surface border border-structural p-8 rounded-3xl shadow-sm space-y-6 text-xs text-center">
        <Link to="/" className="inline-flex items-center gap-2">
          <div className="w-10 h-10 rounded-xl bg-field-ink text-lime-signal flex items-center justify-center font-bold">
            <Sprout size={22} />
          </div>
        </Link>
        <h1 className="text-2xl font-extrabold text-field-ink">Reset Password</h1>

        <p className="text-muted-leaf leading-relaxed">
          Password reset is not available in this deployment yet. Contact your workspace administrator or the Fasal Rakshak support team to regain access.
        </p>
        <Link to="/contact" className="block py-2.5 bg-field-ink text-white font-bold rounded-xl">Contact support</Link>
        <Link to="/login" className="block py-2.5 border border-structural font-bold rounded-xl">Return to login</Link>
      </div>
      </div>
    </div>
  );
};
