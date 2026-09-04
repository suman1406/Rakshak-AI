import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { PublicNavbar } from '../../components/layout/PublicNavbar';
import { PublicFooter } from '../../components/layout/PublicFooter';
import { CheckCircle2, ShieldCheck, Sparkles } from 'lucide-react';
import { apiClient } from '../../services/apiClient';

export const PricingPage: React.FC = () => {
  const [annual, setAnnual] = useState(false);
  const [plans, setPlans] = useState<Array<{ code: string; name: string; monthly_price_paise: number | null; annual_price_paise: number | null; farm_limit: number | null; scan_limit: number | null }>>([]);
  const [loadError, setLoadError] = useState('');
  useEffect(() => {
    apiClient.listPublicPlans().then(setPlans).catch(() => setLoadError('Pilot plans are not available right now. Please contact field operations for current rollout options.'));
  }, []);
  const price = (value: number | null) => value == null ? 'Custom' : `₹${(value / 100).toLocaleString('en-IN')}`;
  return (
    <div className="min-h-screen bg-field-canvas text-field-ink flex flex-col font-sans">
      <PublicNavbar />

      <main className="flex-1 py-12 md:py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full space-y-12">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-lime-signal text-field-ink text-xs font-mono font-bold rounded-full">
            <Sparkles size={12} /> PLANS FOR FIELD OPERATIONS
          </span>
          <h1 className="text-4xl font-extrabold text-field-ink tracking-tight">
            Transparent Plans for Field Health Intelligence
          </h1>
          <p className="text-sm text-muted-leaf max-w-xl mx-auto">
            These are pilot pricing tiers designed for initial FPO rollouts and field deployment testing.
          </p>
        </div>

        <div className="flex justify-center">
          <div className="inline-flex items-center gap-1 rounded-full border border-structural bg-pure-surface p-1 text-xs font-bold shadow-2xs" aria-label="Billing frequency">
            <button type="button" onClick={() => setAnnual(false)} className={`rounded-full px-4 py-2 ${!annual ? 'bg-field-ink text-white' : 'text-muted-leaf'}`}>Monthly</button>
            <button type="button" onClick={() => setAnnual(true)} className={`rounded-full px-4 py-2 ${annual ? 'bg-field-ink text-white' : 'text-muted-leaf'}`}>Annual <span className="ml-1 text-[10px] text-lime-signal">Save 20%</span></button>
          </div>
        </div>

        {/* Pricing Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {plans.map((plan, index) => (
            <div
              key={plan.code}
              className={`p-8 rounded-3xl border flex flex-col justify-between transition ${
                index === 1
                  ? 'border-2 border-field-ink bg-white shadow-xl relative'
                  : 'border-structural bg-pure-surface'
              }`}
            >
              {index === 1 && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-lime-signal text-field-ink text-[10px] font-mono font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                  Recommended for FPOs
                </span>
              )}

              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-bold text-field-ink">{plan.name}</h2>
                  <p className="text-xs text-muted-leaf mt-1">Pilot organization access</p>
                  <div className="mt-4 flex items-baseline gap-1">
                    <span className="text-4xl font-black text-field-ink">{price(annual ? plan.annual_price_paise : plan.monthly_price_paise)}</span>
                    <span className="text-xs text-muted-leaf font-medium">{annual ? '/ year' : '/ month'}</span>
                  </div>
                </div>

                <div className="space-y-2 pt-2 border-t border-structural text-xs">
                  <div className="flex items-center justify-between font-semibold text-field-ink">
                    <span>Monitored Farms:</span>
                    <span className="font-mono text-muted-leaf">{plan.farm_limit ?? 'Flexible'}</span>
                  </div>
                  <div className="flex items-center justify-between font-semibold text-field-ink">
                    <span>Scans Included:</span>
                    <span className="font-mono text-muted-leaf">{plan.scan_limit ?? 'Flexible'}</span>
                  </div>
                </div>

                <ul className="space-y-2.5 text-xs text-field-ink pt-2 border-t border-structural">
                  {['Human-approved activation', 'Evidence-led dashboard access', 'No automatic charge'].map((feat, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <CheckCircle2 size={16} className="text-emerald-600 shrink-0 mt-0.5" />
                      <span>{feat}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="pt-8 space-y-2">
                <Link
                  to={`/apply/organization${plan.code ? `?plan=${encodeURIComponent(plan.code)}` : ''}`}
                  className={`block w-full py-3 text-center text-xs font-bold rounded-xl transition shadow-xs ${
                    index === 1
                      ? 'bg-field-ink text-white hover:bg-opacity-90'
                      : 'bg-field-canvas border border-structural text-field-ink hover:bg-gray-200'
                  }`}
                >
                  Request this pilot plan
                </Link>
                <p className="text-[10px] text-center text-muted-leaf">Plans can be tailored to your deployment</p>
              </div>
            </div>
          ))}
          {!loadError && plans.length === 0 && <div className="md:col-span-3 rounded-2xl border border-structural bg-pure-surface p-8 text-center text-sm text-muted-leaf">No pilot plans have been published yet. Contact field operations to scope a rollout.</div>}
          {loadError && <div className="md:col-span-3 rounded-2xl border border-amber-200 bg-amber-50 p-6 text-center text-sm text-amber-900">{loadError}</div>}
        </div>

        {/* Pilot Disclaimer Box */}
        <div className="bg-amber-50 border border-amber-200 rounded-2xl p-6 text-xs text-amber-900 flex items-start gap-3">
          <ShieldCheck size={20} className="text-amber-700 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold text-amber-950">Pilot Pricing Note:</span>
            <p>
              Indicative plans are shown above. Government programs, state partnerships, and FPO deployments can be scoped with our team.
            </p>
          </div>
        </div>

        <div className="grid sm:grid-cols-3 gap-3 text-xs text-muted-leaf">
          <div className="rounded-2xl border border-structural bg-pure-surface p-4"><p className="font-bold text-field-ink">Pilot-first pricing</p><p className="mt-1">Confirm scope and farm volume before a contract starts.</p></div>
          <div className="rounded-2xl border border-structural bg-pure-surface p-4"><p className="font-bold text-field-ink">No automatic charge</p><p className="mt-1">This page does not collect payment details or start a subscription.</p></div>
          <div className="rounded-2xl border border-structural bg-pure-surface p-4"><p className="font-bold text-field-ink">Talk to field ops</p><p className="mt-1">Government and FPO deployments can be tailored with the team.</p></div>
        </div>
      </main>

      <PublicFooter />
    </div>
  );
};
