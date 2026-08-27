import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { UserRole } from '../../types';
import { Sprout, Sparkles, UserCheck, Shield, ArrowRight, Lock, Play } from 'lucide-react';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [selectedRole, setSelectedRole] = useState<UserRole>('farmer');

  /*
   * FUTURE FASTAPI INTEGRATION POINT:
   * Submit credentials to POST /api/v1/auth/login
   * Expects JSON: { username: email, password: password }
   * Returns: { access_token: "...", token_type: "bearer", role: "agronomist" }
   */
  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login(selectedRole, email);
    navigate('/onboarding');
  };

  const handleDemoClick = (role: UserRole) => {
    login(role);
    navigate('/onboarding');
  };

  return (
    <div className="min-h-screen bg-field-canvas flex items-center justify-center p-4 sm:p-6 lg:p-8 font-sans">
      <div className="max-w-md w-full space-y-6">
        {/* Logo Branding */}
        <div className="text-center space-y-2">
          <Link to="/" className="inline-flex items-center gap-2.5">
            <div className="w-12 h-12 rounded-2xl bg-field-ink text-lime-signal flex items-center justify-center font-bold text-2xl shadow-sm">
              <Sprout size={26} />
            </div>
          </Link>
          <h1 className="text-2xl font-extrabold text-field-ink">Rakshak AI Login</h1>
          <p className="text-xs text-muted-leaf">Select a demo persona or enter credentials to enter</p>
        </div>

        {/* Demo Mode Notice Banner */}
        <div className="bg-lime-signal/20 border border-lime-signal/40 p-3.5 rounded-2xl flex items-center justify-between text-xs text-field-ink">
          <div className="flex items-center gap-2 font-semibold">
            <Sparkles size={16} className="text-field-ink" />
            <span>Simulated Auth • No backend required</span>
          </div>
          <span className="font-mono text-[10px] bg-field-ink text-white px-2 py-0.5 rounded font-bold">
            DEMO
          </span>
        </div>

        {/* Quick Demo Persona Access Buttons (Required) */}
        <div className="bg-pure-surface border border-structural p-5 rounded-2xl shadow-xs space-y-3">
          <span className="text-[10px] font-mono text-muted-leaf uppercase font-bold tracking-wider block">
            Instant Demo Roles (1-Click Login)
          </span>

          <div className="space-y-2">
            <button
              onClick={() => handleDemoClick('farmer')}
              className="w-full py-3 px-4 bg-emerald-50 hover:bg-emerald-100/80 border border-emerald-200 rounded-xl text-left text-xs font-bold text-emerald-900 flex items-center justify-between transition group"
            >
              <div className="flex items-center gap-2.5">
                <Sprout size={16} className="text-emerald-700" />
                <span>Open Farmer Demo</span>
              </div>
              <ArrowRight size={14} className="text-emerald-700 group-hover:translate-x-1 transition" />
            </button>

            <button
              onClick={() => handleDemoClick('agronomist')}
              className="w-full py-3 px-4 bg-blue-50 hover:bg-blue-100/80 border border-blue-200 rounded-xl text-left text-xs font-bold text-blue-900 flex items-center justify-between transition group"
            >
              <div className="flex items-center gap-2.5">
                <UserCheck size={16} className="text-blue-700" />
                <span>Open Agronomist Demo</span>
              </div>
              <ArrowRight size={14} className="text-blue-700 group-hover:translate-x-1 transition" />
            </button>

            <button
              onClick={() => handleDemoClick('org_admin')}
              className="w-full py-3 px-4 bg-amber-50 hover:bg-amber-100/80 border border-amber-200 rounded-xl text-left text-xs font-bold text-amber-900 flex items-center justify-between transition group"
            >
              <div className="flex items-center gap-2.5">
                <Shield size={16} className="text-amber-700" />
                <span>Open Organization Demo</span>
              </div>
              <ArrowRight size={14} className="text-amber-700 group-hover:translate-x-1 transition" />
            </button>
          </div>
        </div>

        {/* Standard Form Login */}
        <div className="bg-pure-surface border border-structural p-6 rounded-2xl shadow-xs space-y-4 text-xs">
          <div className="flex items-center justify-between pb-2 border-b border-structural">
            <span className="font-bold text-field-ink">Custom Email & Password Login</span>
            <span className="text-[10px] text-muted-leaf">Any inputs accepted</span>
          </div>

          <form onSubmit={handleFormSubmit} className="space-y-4">
            <div>
              <label className="block font-semibold mb-1 text-field-ink">Role Context</label>
              <select
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value as UserRole)}
                className="w-full p-2.5 rounded-xl border border-structural bg-field-canvas text-xs font-medium focus:ring-2 focus:ring-field-ink outline-none"
              >
                <option value="farmer">Farmer (View Field Scans & Reports)</option>
                <option value="agronomist">Agronomist (Review Queue & Evidence Verification)</option>
                <option value="org_admin">Organization Admin (FPO Command Dashboard & Analytics)</option>
              </select>
            </div>

            <div>
              <label className="block font-semibold mb-1 text-field-ink">Email Address</label>
              <input
                type="text"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="e.g. ramesh.patil@example.com (or leave empty)"
                className="w-full p-2.5 rounded-xl border border-structural bg-field-canvas text-xs focus:ring-2 focus:ring-field-ink outline-none"
              />
            </div>

            <div>
              <div className="flex justify-between mb-1">
                <label className="font-semibold text-field-ink">Password</label>
                <Link to="/forgot-password" className="text-muted-leaf hover:underline text-[11px]">
                  Forgot password?
                </Link>
              </div>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="•••••••• (or leave empty)"
                className="w-full p-2.5 rounded-xl border border-structural bg-field-canvas text-xs focus:ring-2 focus:ring-field-ink outline-none"
              />
            </div>

            <div className="pt-2 space-y-2">
              <button
                type="submit"
                className="w-full py-3 bg-field-ink text-white font-bold rounded-xl hover:bg-opacity-90 transition text-xs shadow-xs"
              >
                Sign In with Role
              </button>

              <button
                type="button"
                onClick={() => handleDemoClick(selectedRole)}
                className="w-full py-2.5 bg-field-canvas border border-structural text-field-ink font-bold rounded-xl hover:bg-gray-200 transition text-xs"
              >
                Continue as Demo
              </button>
            </div>
          </form>

          <div className="pt-3 text-center border-t border-structural text-[11px] text-muted-leaf">
            Don't have an account?{' '}
            <Link to="/register" className="font-bold text-field-ink hover:underline">
              Create an account
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
