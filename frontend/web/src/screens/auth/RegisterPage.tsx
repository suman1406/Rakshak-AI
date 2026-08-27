import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { UserRole } from '../../types';
import { Sprout, ArrowRight } from 'lucide-react';

export const RegisterPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [roleChoice, setRoleChoice] = useState<UserRole>('farmer');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login(roleChoice, email);
    navigate('/onboarding');
  };

  return (
    <div className="min-h-screen bg-field-canvas flex items-center justify-center p-4 font-sans">
      <div className="max-w-md w-full bg-pure-surface border border-structural p-8 rounded-3xl shadow-sm space-y-6">
        <div className="text-center space-y-2">
          <Link to="/" className="inline-flex items-center gap-2">
            <div className="w-10 h-10 rounded-xl bg-field-ink text-lime-signal flex items-center justify-center font-bold">
              <Sprout size={22} />
            </div>
          </Link>
          <h1 className="text-2xl font-extrabold text-field-ink">Register for Rakshak AI</h1>
          <p className="text-xs text-muted-leaf">Create a simulated account for testing</p>
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

          <div>
            <label className="block font-semibold mb-1">Role Persona</label>
            <select
              value={roleChoice}
              onChange={(e) => setRoleChoice(e.target.value as UserRole)}
              className="w-full p-2.5 rounded-xl border border-structural bg-field-canvas text-xs outline-none font-medium"
            >
              <option value="farmer">Farmer</option>
              <option value="agronomist">Agronomist</option>
              <option value="org_admin">Organization Admin</option>
            </select>
          </div>

          <button
            type="submit"
            className="w-full py-3 bg-field-ink text-white font-bold rounded-xl hover:bg-opacity-90 transition"
          >
            Create Account & Enter Demo
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
  );
};

export const ForgotPasswordPage: React.FC = () => {
  const [sent, setSent] = useState(false);

  return (
    <div className="min-h-screen bg-field-canvas flex items-center justify-center p-4 font-sans">
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
              Demo reset link dispatched. In demo mode, you can sign in directly using any password.
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
  );
};
