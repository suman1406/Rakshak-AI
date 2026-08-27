import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Sprout } from 'lucide-react';
import { PublicNavbar } from '../../components/layout/PublicNavbar';

export const RegisterPage: React.FC = () => {
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    navigate('/contact');
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
          <p className="text-xs text-muted-leaf">Create your workspace account</p>
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
            className="w-full py-3 bg-field-ink text-white font-bold rounded-xl hover:bg-opacity-90 transition"
          >
            Request access
          </button>
        </form>

        <div className="text-center text-xs text-muted-leaf pt-2 border-t border-structural">
          Already registered?{' '}
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
  const [sent, setSent] = useState(false);

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

        {sent ? (
          <div className="space-y-4">
            <p className="text-emerald-700 bg-emerald-50 p-4 rounded-xl border border-emerald-200">
              If an account exists for this email, password reset instructions will be sent shortly.
            </p>
            <Link to="/login" className="block py-2.5 bg-field-ink text-white font-bold rounded-xl">
              Return to Login
            </Link>
          </div>
        ) : (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              setSent(true);
            }}
            className="space-y-4 text-left"
          >
            <div>
              <label className="block font-semibold mb-1">Email Address</label>
              <input
                type="email"
                required
                placeholder="name@example.com"
                className="w-full p-2.5 rounded-xl border border-structural bg-field-canvas text-xs outline-none"
              />
            </div>
            <button type="submit" className="w-full py-3 bg-field-ink text-white font-bold rounded-xl">
              Send Password Reset Link
            </button>
          </form>
        )}
      </div>
      </div>
    </div>
  );
};
