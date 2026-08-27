import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { Sprout, CheckCircle2, ArrowRight, LayoutDashboard, ClipboardCheck, BarChart3 } from 'lucide-react';

export const OnboardingPage: React.FC = () => {
  const { user, role } = useAuth();
  const navigate = useNavigate();
  const isAgronomist = role === 'agronomist';
  const destination = isAgronomist ? '/agronomist/dashboard' : '/organization/dashboard';
  const features = isAgronomist
    ? [['Review queue', 'Prioritize incoming cases', ClipboardCheck], ['Evidence', 'Inspect multi-frame signals', Sprout], ['Verification', 'Record expert decisions', CheckCircle2]]
    : [['Field health', 'See portfolio risk', BarChart3], ['Farms & fields', 'Drill into local signals', Sprout], ['Reports', 'Export pilot summaries', CheckCircle2]];

  return (
    <div className="min-h-screen bg-field-canvas flex items-center justify-center p-4 sm:p-6 font-sans">
      <main className="max-w-2xl w-full bg-pure-surface border border-structural rounded-3xl p-6 sm:p-10 shadow-lg">
        <div className="flex items-center gap-3 mb-10">
          <div className="w-11 h-11 rounded-2xl bg-field-ink text-lime-signal flex items-center justify-center"><Sprout size={24} /></div>
          <div><p className="font-extrabold text-field-ink">Rakshak AI</p><p className="text-xs text-muted-leaf">Workspace setup</p></div>
        </div>
        <section className="space-y-3">
          <span className="text-[10px] font-mono uppercase tracking-[0.16em] text-muted-leaf">Step 1 of 1</span>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-field-ink text-balance">Your {isAgronomist ? 'review workspace' : 'organization workspace'} is ready.</h1>
          <p className="text-sm leading-6 text-muted-leaf max-w-xl">Welcome, {user?.name || 'demo user'}. This prototype keeps your workspace role fixed for this session so the navigation and data always match your responsibilities.</p>
        </section>
        <div className="grid sm:grid-cols-3 gap-3 my-8">
          {features.map(([title, description, Icon]) => {
            const FeatureIcon = Icon as typeof Sprout;
            return <div key={title as string} className="rounded-2xl bg-field-canvas border border-structural p-4 space-y-3"><FeatureIcon size={19} className="text-field-ink" /><div><p className="text-xs font-bold text-field-ink">{title as string}</p><p className="text-[11px] leading-4 text-muted-leaf mt-1">{description as string}</p></div></div>;
          })}
        </div>
        <div className="flex flex-col sm:flex-row gap-3">
          <button onClick={() => navigate(destination)} className="flex-1 py-3.5 bg-field-ink text-white font-bold text-sm rounded-xl hover:bg-opacity-90 transition flex items-center justify-center gap-2"><LayoutDashboard size={17} className="text-lime-signal" /> Open workspace <ArrowRight size={16} /></button>
          <button onClick={() => navigate('/')} className="py-3.5 px-5 bg-field-canvas border border-structural text-field-ink font-bold text-sm rounded-xl hover:bg-white transition">Return to site</button>
        </div>
      </main>
    </div>
  );
};
