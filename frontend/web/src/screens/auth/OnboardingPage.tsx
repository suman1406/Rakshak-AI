import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { UserRole } from '../../types';
import { Sprout, UserCheck, Shield, ArrowRight, CheckCircle2, Sparkles, LayoutDashboard } from 'lucide-react';

export const OnboardingPage: React.FC = () => {
  const { user, role, switchRole } = useAuth();
  const navigate = useNavigate();
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [selectedRole, setSelectedRole] = useState<UserRole>(role || 'farmer');

  const handleRoleSelect = (newRole: UserRole) => {
    setSelectedRole(newRole);
    switchRole(newRole);
  };

  const handleFinishOnboarding = () => {
    if (selectedRole === 'farmer') navigate('/farmer/dashboard');
    else if (selectedRole === 'agronomist') navigate('/agronomist/dashboard');
    else navigate('/organization/dashboard');
  };

  return (
    <div className="min-h-screen bg-field-canvas flex items-center justify-center p-4 sm:p-6 lg:p-8 font-sans">
      <div className="max-w-xl w-full bg-pure-surface border border-structural rounded-3xl p-6 sm:p-10 shadow-lg space-y-8">
        {/* Step Progress Bar */}
        <div className="flex items-center justify-between text-xs font-mono text-muted-leaf border-b border-structural pb-4">
          <span className="font-bold text-field-ink">ONBOARDING STEP {step} OF 3</span>
          <div className="flex items-center gap-1.5">
            <span className={`w-2.5 h-2.5 rounded-full ${step >= 1 ? 'bg-lime-signal ring-2 ring-field-ink' : 'bg-gray-200'}`} />
            <span className={`w-2.5 h-2.5 rounded-full ${step >= 2 ? 'bg-lime-signal ring-2 ring-field-ink' : 'bg-gray-200'}`} />
            <span className={`w-2.5 h-2.5 rounded-full ${step >= 3 ? 'bg-lime-signal ring-2 ring-field-ink' : 'bg-gray-200'}`} />
          </div>
        </div>

        {/* Screen 1: Welcome */}
        {step === 1 && (
          <div className="space-y-6 text-center">
            <div className="w-16 h-16 rounded-2xl bg-field-ink text-lime-signal flex items-center justify-center mx-auto shadow-md">
              <Sprout size={32} />
            </div>

            <div className="space-y-2">
              <h1 className="text-3xl font-extrabold text-field-ink">Welcome to Rakshak AI</h1>
              <p className="text-sm text-muted-leaf max-w-md mx-auto">
                Your AI-powered crop disease detection and field health intelligence portal by Fasal Rakshak.
              </p>
            </div>

            <div className="p-4 bg-field-canvas rounded-2xl border border-structural text-left text-xs space-y-2 text-muted-leaf">
              <p className="font-bold text-field-ink">What you can do in this platform:</p>
              <p>• Submit short soybean field videos for automated multi-frame disease detection.</p>
              <p>• Review agronomist-verified evidence frames & severity estimations.</p>
              <p>• Monitor district and FPO-wide crop disease trends.</p>
            </div>

            <button
              onClick={() => setStep(2)}
              className="w-full py-3.5 bg-field-ink text-white font-bold text-sm rounded-xl hover:bg-opacity-90 transition flex items-center justify-center gap-2 shadow-xs"
            >
              <span>Next: Choose How You Work</span>
              <ArrowRight size={16} className="text-lime-signal" />
            </button>
          </div>
        )}

        {/* Screen 2: Choose How You Work */}
        {step === 2 && (
          <div className="space-y-6">
            <div className="text-center space-y-1">
              <h1 className="text-2xl font-extrabold text-field-ink">Choose how you work</h1>
              <p className="text-xs text-muted-leaf">Select the role persona to customize your workspace dashboard</p>
            </div>

            <div className="space-y-3">
              {/* Farmer Card */}
              <div
                onClick={() => handleRoleSelect('farmer')}
                className={`p-4 rounded-2xl border cursor-pointer transition flex items-start gap-4 ${
                  selectedRole === 'farmer'
                    ? 'border-2 border-field-ink bg-emerald-50/60 shadow-xs'
                    : 'border-structural bg-pure-surface hover:border-gray-300'
                }`}
              >
                <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center shrink-0">
                  <Sprout size={20} />
                </div>
                <div className="flex-1 space-y-1">
                  <div className="flex items-center justify-between">
                    <h3 className="font-bold text-sm text-field-ink">Farmer Persona</h3>
                    {selectedRole === 'farmer' && <CheckCircle2 size={18} className="text-emerald-700" />}
                  </div>
                  <p className="text-xs text-muted-leaf">
                    Submit field scan videos, track crop health scores, and view agronomist reports.
                  </p>
                </div>
              </div>

              {/* Agronomist Card */}
              <div
                onClick={() => handleRoleSelect('agronomist')}
                className={`p-4 rounded-2xl border cursor-pointer transition flex items-start gap-4 ${
                  selectedRole === 'agronomist'
                    ? 'border-2 border-field-ink bg-blue-50/60 shadow-xs'
                    : 'border-structural bg-pure-surface hover:border-gray-300'
                }`}
              >
                <div className="w-10 h-10 rounded-xl bg-blue-100 text-blue-800 flex items-center justify-center shrink-0">
                  <UserCheck size={20} />
                </div>
                <div className="flex-1 space-y-1">
                  <div className="flex items-center justify-between">
                    <h3 className="font-bold text-sm text-field-ink">Agronomist Persona</h3>
                    {selectedRole === 'agronomist' && <CheckCircle2 size={18} className="text-blue-700" />}
                  </div>
                  <p className="text-xs text-muted-leaf">
                    Review incoming field cases, inspect 16 evidence frames, and submit verified diagnostic notes.
                  </p>
                </div>
              </div>

              {/* Org Admin Card */}
              <div
                onClick={() => handleRoleSelect('org_admin')}
                className={`p-4 rounded-2xl border cursor-pointer transition flex items-start gap-4 ${
                  selectedRole === 'org_admin'
                    ? 'border-2 border-field-ink bg-amber-50/60 shadow-xs'
                    : 'border-structural bg-pure-surface hover:border-gray-300'
                }`}
              >
                <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center shrink-0">
                  <Shield size={20} />
                </div>
                <div className="flex-1 space-y-1">
                  <div className="flex items-center justify-between">
                    <h3 className="font-bold text-sm text-field-ink">Organization Admin</h3>
                    {selectedRole === 'org_admin' && <CheckCircle2 size={18} className="text-amber-700" />}
                  </div>
                  <p className="text-xs text-muted-leaf">
                    Monitor 4,000+ farms across FPOs, track district disease outbreaks, and export analytics.
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3 pt-2">
              <button
                onClick={() => setStep(1)}
                className="py-3 px-4 bg-field-canvas border border-structural text-xs font-bold rounded-xl text-field-ink hover:bg-gray-200 transition"
              >
                Back
              </button>
              <button
                onClick={() => setStep(3)}
                className="flex-1 py-3.5 bg-field-ink text-white font-bold text-sm rounded-xl hover:bg-opacity-90 transition flex items-center justify-center gap-2 shadow-xs"
              >
                <span>Continue with {selectedRole.replace('_', ' ')}</span>
                <ArrowRight size={16} className="text-lime-signal" />
              </button>
            </div>
          </div>
        )}

        {/* Screen 3: Workspace Ready */}
        {step === 3 && (
          <div className="space-y-6 text-center">
            <div className="w-16 h-16 rounded-full bg-soft-healthy text-emerald-800 flex items-center justify-center mx-auto shadow-md">
              <CheckCircle2 size={36} />
            </div>

            <div className="space-y-2">
              <h1 className="text-3xl font-extrabold text-field-ink">Your workspace is ready</h1>
              <p className="text-sm text-muted-leaf">
                Configured for <span className="font-bold text-field-ink capitalize">{user?.name || 'Demo User'}</span> as{' '}
                <span className="font-bold text-field-ink capitalize">{selectedRole.replace('_', ' ')}</span>.
              </p>
            </div>

            <div className="bg-field-canvas p-5 rounded-2xl border border-structural space-y-3 text-left text-xs">
              <div className="flex items-center justify-between border-b border-structural pb-2">
                <span className="text-muted-leaf font-medium">Selected Role:</span>
                <span className="font-bold text-field-ink capitalize">{selectedRole.replace('_', ' ')}</span>
              </div>
              <div className="flex items-center justify-between border-b border-structural pb-2">
                <span className="text-muted-leaf font-medium">Target Destination:</span>
                <span className="font-mono font-bold text-field-ink">
                  {selectedRole === 'farmer'
                    ? '/farmer/dashboard'
                    : selectedRole === 'agronomist'
                    ? '/agronomist/dashboard'
                    : '/organization/dashboard'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-leaf font-medium">Data Mode:</span>
                <span className="font-bold text-emerald-700">Deterministic Mock Active</span>
              </div>
            </div>

            <button
              onClick={handleFinishOnboarding}
              className="w-full py-3.5 bg-field-ink text-white font-bold text-sm rounded-xl hover:bg-opacity-90 transition flex items-center justify-center gap-2 shadow-sm"
            >
              <LayoutDashboard size={18} className="text-lime-signal" />
              <span>Open Dashboard</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
