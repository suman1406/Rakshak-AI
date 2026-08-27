import React from 'react';
import { Link } from 'react-router-dom';
import { PublicNavbar } from '../../components/layout/PublicNavbar';
import { PublicFooter } from '../../components/layout/PublicFooter';
import { PRICING_PLANS } from '../../data/mockData';
import { CheckCircle2, ShieldCheck, Sparkles, HelpCircle } from 'lucide-react';

export const PricingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-field-canvas text-field-ink flex flex-col font-sans">
      <PublicNavbar />

      <main className="flex-1 py-12 md:py-20 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full space-y-12">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto space-y-4">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 bg-lime-signal text-field-ink text-xs font-mono font-bold rounded-full">
            <Sparkles size={12} /> PILOT DEMO PRICING
          </span>
          <h1 className="text-4xl font-extrabold text-field-ink tracking-tight">
            Transparent Plans for Field Health Intelligence
          </h1>
          <p className="text-sm text-muted-leaf max-w-xl mx-auto">
            These are pilot pricing tiers designed for initial FPO rollouts and field deployment testing.
          </p>
        </div>

        {/* Pricing Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {PRICING_PLANS.map((plan) => (
            <div
              key={plan.id}
              className={`p-8 rounded-3xl border flex flex-col justify-between transition ${
                plan.isPopular
                  ? 'border-2 border-field-ink bg-white shadow-xl relative'
                  : 'border-structural bg-pure-surface'
              }`}
            >
              {plan.isPopular && (
                <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-lime-signal text-field-ink text-[10px] font-mono font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                  Recommended for FPOs
                </span>
              )}

              <div className="space-y-6">
                <div>
                  <h2 className="text-xl font-bold text-field-ink">{plan.name}</h2>
                  <p className="text-xs text-muted-leaf mt-1">{plan.targetUser}</p>
                  <div className="mt-4 flex items-baseline gap-1">
                    <span className="text-4xl font-black text-field-ink">{plan.price}</span>
                    <span className="text-xs text-muted-leaf font-medium">{plan.period}</span>
                  </div>
                </div>

                <div className="space-y-2 pt-2 border-t border-structural text-xs">
                  <div className="flex items-center justify-between font-semibold text-field-ink">
                    <span>Monitored Farms:</span>
                    <span className="font-mono text-muted-leaf">{plan.monitoredFarms}</span>
                  </div>
                  <div className="flex items-center justify-between font-semibold text-field-ink">
                    <span>Scans Included:</span>
                    <span className="font-mono text-muted-leaf">{plan.scansIncluded}</span>
                  </div>
                </div>

                <ul className="space-y-2.5 text-xs text-field-ink pt-2 border-t border-structural">
                  {plan.features.map((feat, i) => (
                    <li key={i} className="flex items-start gap-2">
                      <CheckCircle2 size={16} className="text-emerald-600 shrink-0 mt-0.5" />
                      <span>{feat}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="pt-8 space-y-2">
                <Link
                  to="/login"
                  className={`block w-full py-3 text-center text-xs font-bold rounded-xl transition shadow-xs ${
                    plan.isPopular
                      ? 'bg-field-ink text-white hover:bg-opacity-90'
                      : 'bg-field-canvas border border-structural text-field-ink hover:bg-gray-200'
                  }`}
                >
                  {plan.ctaText}
                </Link>
                <p className="text-[10px] text-center text-muted-leaf">No credit card required for pilot demo</p>
              </div>
            </div>
          ))}
        </div>

        {/* Pilot Disclaimer Box */}
        <div className="bg-amber-50 border border-amber-200 rounded-2xl p-6 text-xs text-amber-900 flex items-start gap-3">
          <ShieldCheck size={20} className="text-amber-700 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <span className="font-bold text-amber-950">Pilot Pricing Note:</span>
            <p>
              All prices shown above are demo terms for pilot projects. Custom government grants, state department partnerships, and FPO subsidy structures are available upon request.
            </p>
          </div>
        </div>
      </main>

      <PublicFooter />
    </div>
  );
};
