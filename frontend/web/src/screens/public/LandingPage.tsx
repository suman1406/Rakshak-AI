import React from 'react';
import { Link } from 'react-router-dom';
import { PublicNavbar } from '../../components/layout/PublicNavbar';
import { PublicFooter } from '../../components/layout/PublicFooter';
import { SafetyBanner } from '../../components/shared/SafetyBanner';
import { PRICING_PLANS } from '../../data/mockData';
import {
  Video,
  Layers,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  ArrowRight,
  TrendingUp,
  UserCheck,
  Scan,
  Activity,
  Award,
  ChevronRight,
  HelpCircle,
  BarChart3,
  Building2,
  Lock,
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-field-canvas text-field-ink flex flex-col font-sans">
      <PublicNavbar />

      {/* Hero Section */}
      <section className="relative pt-12 pb-20 md:pt-20 md:pb-32 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
          {/* Left Column: Headline & Action Scope */}
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-soft-healthy border border-emerald-200 text-xs font-semibold text-soft-healthy">
              <Sparkles size={14} className="text-emerald-700" />
              <span>Record your crop. Detect disease. Measure severity.</span>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black tracking-tight text-field-ink leading-[1.1]">
              See what your <br className="hidden sm:inline" />
              <span className="underline decoration-lime-signal decoration-wavy underline-offset-8">crop is telling you</span>.
            </h1>

            <p className="text-base sm:text-lg text-muted-leaf max-w-2xl leading-relaxed">
              Turn a short soybean field video into evidence-backed signals on disease, severity, and what to inspect next.
            </p>

            {/* CTAs */}
            <div className="flex flex-wrap items-center gap-4 pt-2">
              <Link
                to="/login"
                className="px-6 py-3.5 bg-field-ink text-white font-bold text-sm rounded-xl hover:bg-opacity-90 transition shadow-md flex items-center gap-2 group"
              >
                <span>Explore workspaces</span>
                <ArrowRight size={16} className="text-lime-signal group-hover:translate-x-1 transition" />
              </Link>
              <Link
                to="/how-it-works"
                className="px-6 py-3.5 bg-pure-surface text-field-ink border border-structural font-bold text-xs rounded-xl hover:bg-field-canvas transition shadow-xs flex items-center gap-2"
              >
                Explore the platform
                <ChevronRight size={16} className="text-muted-leaf" />
              </Link>
            </div>

            {/* Safety Disclaimer Banner */}
            <div className="pt-2">
              <SafetyBanner compact />
            </div>
          </div>

          {/* Right Column: Visual Product Simulation Card */}
          <div className="lg:col-span-5">
            <div className="bg-pure-surface border border-structural rounded-3xl p-6 shadow-xl relative overflow-hidden space-y-5">
              <div className="flex items-center justify-between pb-3 border-b border-structural">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full bg-alert-red animate-ping" />
                  <span className="font-mono text-xs font-bold text-field-ink">FIELD REVIEW #FASAL-10482</span>
                </div>
                <span className="text-[10px] font-mono bg-soft-healthy text-emerald-800 px-2 py-0.5 rounded font-bold">
                  SOYBEAN
                </span>
              </div>

              {/* Sample Frame Canvas Preview */}
              <div className="relative aspect-16/10 rounded-2xl overflow-hidden bg-field-ink border border-structural">
                <img
                  src="https://images.unsplash.com/photo-1592417817098-8f3d6eb231fc?auto=format&fit=crop&w=800&q=80"
                  alt="Soybean Leaf Detection"
                  className="w-full h-full object-cover opacity-90"
                />

                {/* Simulated Bounding Box Overlay */}
                <div className="absolute top-[28%] left-[24%] w-[38%] h-[40%] border-2 border-alert-red bg-alert-red/20 rounded-lg flex items-start p-1.5">
                  <span className="bg-alert-red text-white text-[9px] font-mono font-bold px-1.5 py-0.5 rounded">
                    Soybean Rust (87%)
                  </span>
                </div>

                <div className="absolute bottom-3 left-3 bg-field-ink/80 backdrop-blur-md px-3 py-1 rounded-lg text-white font-mono text-[10px] flex items-center gap-2">
                  <Scan size={12} className="text-lime-signal" />
                  <span>16 Frames Analyzed • 43 Leaf Regions</span>
                </div>
              </div>

              {/* Result Summary Metrics */}
              <div className="grid grid-cols-3 gap-3 text-center">
                <div className="p-2.5 bg-field-canvas rounded-xl border border-structural">
                  <span className="text-[10px] text-muted-leaf block">AI Indication</span>
                  <span className="font-bold text-xs text-alert-red">Soybean Rust</span>
                </div>
                <div className="p-2.5 bg-field-canvas rounded-xl border border-structural">
                  <span className="text-[10px] text-muted-leaf block">Confidence</span>
                  <span className="font-bold text-xs text-field-ink">87% Score</span>
                </div>
                <div className="p-2.5 bg-field-canvas rounded-xl border border-structural">
                  <span className="text-[10px] text-muted-leaf block">Severity</span>
                  <span className="font-bold text-xs text-warning-orange">Moderate (~20%)</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Workflow Section: Record -> Analyze -> Act carefully */}
      <section className="py-16 bg-pure-surface border-y border-structural">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
          <div className="text-center max-w-2xl mx-auto space-y-3">
            <span className="text-xs font-bold uppercase tracking-wider text-muted-leaf font-mono">Simple 3-Step Process</span>
            <h2 className="text-3xl font-extrabold text-field-ink">How Rakshak AI Works</h2>
            <p className="text-sm text-muted-leaf">
              Designed for field usability in connectivity-constrained rural environments.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-6 bg-field-canvas rounded-2xl border border-structural space-y-4">
              <div className="w-12 h-12 rounded-xl bg-field-ink text-lime-signal flex items-center justify-center font-bold text-lg">
                1
              </div>
              <h3 className="text-lg font-bold text-field-ink">Record</h3>
              <p className="text-xs text-muted-leaf leading-relaxed">
                Capture a 10-15 second video sweeping over upper and lower leaves of soybean plants in your field plot.
              </p>
            </div>

            <div className="p-6 bg-field-canvas rounded-2xl border border-structural space-y-4">
              <div className="w-12 h-12 rounded-xl bg-field-ink text-lime-signal flex items-center justify-center font-bold text-lg">
                2
              </div>
              <h3 className="text-lg font-bold text-field-ink">Analyze</h3>
              <p className="text-xs text-muted-leaf leading-relaxed">
                Computer vision extracts 16 key frames, evaluates 40+ leaf regions, and identifies lesion patterns with confidence metrics.
              </p>
            </div>

            <div className="p-6 bg-field-canvas rounded-2xl border border-structural space-y-4">
              <div className="w-12 h-12 rounded-xl bg-field-ink text-lime-signal flex items-center justify-center font-bold text-lg">
                3
              </div>
              <h3 className="text-lg font-bold text-field-ink">Act carefully</h3>
              <p className="text-xs text-muted-leaf leading-relaxed">
                Receive evidence-based guidance and agronomist verification before spending on bio-fungicides or field interventions.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Trust & objection handling */}
      <section className="py-16 bg-field-canvas border-b border-structural">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid lg:grid-cols-[1fr_1.1fr] gap-10 items-center">
          <div className="space-y-5">
            <span className="eyebrow">Built for the field, reviewed by people</span>
            <h2 className="text-3xl sm:text-4xl font-extrabold text-field-ink">A signal is useful only when you can see why it was raised.</h2>
            <p className="text-sm text-muted-leaf leading-relaxed max-w-xl">Every indication carries its evidence frames, confidence band, and a clear path to agronomist review. That gives growers context before they act.</p>
            <div className="grid sm:grid-cols-3 gap-3 pt-2">
              {[
                ['16', 'evidence frames'],
                ['40+', 'leaf regions'],
                ['1', 'review queue'],
              ].map(([value, label]) => <div key={label} className="surface-card rounded-2xl p-4"><p className="metric-value text-2xl font-black text-field-ink">{value}</p><p className="text-[11px] text-muted-leaf mt-1">{label}</p></div>)}
            </div>
          </div>
          <div className="relative overflow-hidden rounded-3xl border border-structural bg-field-ink min-h-[18rem] shadow-lg">
            <img src="https://kj1bcdn.b-cdn.net/media/62983/jl.jpg?width=1200" alt="Farmer inspecting a green crop field" className="absolute inset-0 h-full w-full object-cover opacity-75" />
            <div className="absolute inset-0 bg-field-ink/35" />
            <div className="absolute left-5 top-5 max-w-[15rem] rounded-2xl border border-white/20 bg-field-ink/85 p-4 text-white backdrop-blur-sm">
              <p className="eyebrow text-lime-signal">Field note / 04</p>
              <p className="mt-2 text-sm font-semibold leading-5">The next best action starts with better evidence.</p>
            </div>
            <div className="absolute bottom-5 right-5 rounded-xl border border-white/20 bg-white/90 px-3 py-2 text-[10px] font-mono font-bold text-field-ink">OBSERVE → REVIEW → ACT</div>
          </div>
        </div>
      </section>

      {/* Feature Deep Dive Sections */}
      <section className="py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-24">
        {/* Multi-frame Intelligence */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="space-y-4">
            <span className="px-3 py-1 bg-soft-healthy text-emerald-800 text-xs font-bold rounded-full">
              Multi-Frame Sampling
            </span>
            <h2 className="text-3xl font-extrabold text-field-ink">
              Multi-frame visual intelligence, not single-photo guesses
            </h2>
            <p className="text-sm text-muted-leaf leading-relaxed">
              Single photographs often miss early fungal pustules or suffer from lighting glare. Rakshak AI breaks down video streams into 16 distinct frame captures to inspect leaf surfaces from multiple angles.
            </p>
            <ul className="space-y-2 text-xs text-field-ink pt-2">
              <li className="flex items-center gap-2">
                <CheckCircle2 size={16} className="text-emerald-600 shrink-0" />
                <span>Extracts 16 high-clarity sampling frames per field video</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 size={16} className="text-emerald-600 shrink-0" />
                <span>Filters out blurred, out-of-focus, or glare-heavy frames automatically</span>
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle2 size={16} className="text-emerald-600 shrink-0" />
                <span>Provides full spatial region bounding boxes for agronomist audit</span>
              </li>
            </ul>
          </div>

          <div className="bg-pure-surface p-6 rounded-2xl border border-structural shadow-sm space-y-3">
            <div className="flex items-center justify-between text-xs font-bold text-field-ink pb-2 border-b border-structural">
              <span>Extracted Evidence Gallery</span>
              <span className="text-muted-leaf font-mono">16 Frames</span>
            </div>
            <div className="grid grid-cols-4 gap-2">
              {Array.from({ length: 8 }).map((_, i) => (
                <div key={i} className="aspect-square rounded-lg overflow-hidden border border-structural relative">
                  <img
                    src="https://images.unsplash.com/photo-1592417817098-8f3d6eb231fc?auto=format&fit=crop&w=300&q=80"
                    alt=""
                    className="w-full h-full object-cover"
                  />
                  <span className="absolute bottom-1 right-1 bg-field-ink/80 text-white text-[9px] font-mono px-1 rounded">
                    #{i + 1}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Disease Confidence & Severity Estimation */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          <div className="order-2 lg:order-1 bg-pure-surface p-6 rounded-2xl border border-structural shadow-sm space-y-4">
            <h4 className="text-xs font-bold text-muted-leaf uppercase tracking-wider">
              Sample AI Probability Output
            </h4>
            <div className="space-y-3 text-xs">
              <div>
                <div className="flex justify-between font-semibold mb-1">
                  <span>Soybean Rust</span>
                  <span className="text-alert-red font-mono">87%</span>
                </div>
                <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                  <div className="bg-alert-red h-full w-[87%] rounded-full" />
                </div>
              </div>
              <div>
                <div className="flex justify-between font-semibold mb-1">
                  <span>Bacterial Blight</span>
                  <span className="text-muted-leaf font-mono">5%</span>
                </div>
                <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                  <div className="bg-warning-orange h-full w-[5%] rounded-full" />
                </div>
              </div>
              <div>
                <div className="flex justify-between font-semibold mb-1">
                  <span>Healthy Canopy</span>
                  <span className="text-muted-leaf font-mono">4%</span>
                </div>
                <div className="w-full bg-gray-100 h-2 rounded-full overflow-hidden">
                  <div className="bg-soft-healthy h-full w-[4%] rounded-full" />
                </div>
              </div>
            </div>
          </div>

          <div className="order-1 lg:order-2 space-y-4">
            <span className="px-3 py-1 bg-amber-50 text-amber-900 text-xs font-bold rounded-full">
              Confidence & Severity
            </span>
            <h2 className="text-3xl font-extrabold text-field-ink">
              Transparent confidence & severity estimations
            </h2>
            <p className="text-sm text-muted-leaf leading-relaxed">
              Rakshak AI doesn’t just output a binary label. It calculates calibrated confidence scores and estimates percentage plant coverage so farmers and agronomists understand exact risk intensity.
            </p>
          </div>
        </div>

        {/* Agronomist Verification Section */}
        <div className="bg-field-ink text-white rounded-3xl p-8 md:p-12 space-y-8">
          <div className="max-w-2xl space-y-3">
            <span className="px-3 py-1 bg-lime-signal text-field-ink text-xs font-bold rounded-full">
              Human-in-the-Loop
            </span>
            <h2 className="text-3xl font-extrabold">Agronomist Verification Queue</h2>
            <p className="text-xs text-slate-300 leading-relaxed">
              AI recommendations are reviewed by expert agronomists before high-cost field actions are executed. Agronomists can confirm, adjust, or mark cases for physical inspection.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-4 text-xs">
            <div className="p-4 bg-white/5 rounded-2xl border border-white/10 space-y-2">
              <span className="text-lime-signal font-mono font-bold text-sm">Step 1</span>
              <p className="font-semibold text-white">AI Case Flagging</p>
              <p className="text-slate-300">High severity or low confidence scans are automatically escalated to the queue.</p>
            </div>
            <div className="p-4 bg-white/5 rounded-2xl border border-white/10 space-y-2">
              <span className="text-lime-signal font-mono font-bold text-sm">Step 2</span>
              <p className="font-semibold text-white">Frame Inspection</p>
              <p className="text-slate-300">Agronomists audit 16 evidence frames and leaf region bounding boxes.</p>
            </div>
            <div className="p-4 bg-white/5 rounded-2xl border border-white/10 space-y-2">
              <span className="text-lime-signal font-mono font-bold text-sm">Step 3</span>
              <p className="font-semibold text-white">Verified Advice</p>
              <p className="text-slate-300">The farmer receives an official agronomist confirmation note with recommended next steps.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Preview Section */}
      <section className="py-16 bg-pure-surface border-t border-structural">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
          <div className="text-center max-w-xl mx-auto space-y-3">
            <span className="text-xs font-bold uppercase tracking-wider text-muted-leaf font-mono">Pilot Pricing</span>
            <h2 className="text-3xl font-extrabold text-field-ink">Transparent Plans for Farms & Collectives</h2>
            <p className="text-xs text-muted-leaf">
              Flexible plans for individual growers, FPOs, and state agricultural departments.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {PRICING_PLANS.map((plan) => (
              <div
                key={plan.id}
                className={`p-6 rounded-2xl border flex flex-col justify-between transition ${
                  plan.isPopular
                    ? 'border-2 border-field-ink bg-white shadow-md relative'
                    : 'border-structural bg-field-canvas'
                }`}
              >
                {plan.isPopular && (
                  <span className="absolute -top-3 left-1/2 -translate-x-1/2 bg-lime-signal text-field-ink text-[10px] font-bold px-3 py-0.5 rounded-full uppercase tracking-wider font-mono">
                    Most Popular
                  </span>
                )}
                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-bold text-field-ink">{plan.name}</h3>
                    <div className="mt-2 flex items-baseline gap-1">
                      <span className="text-3xl font-extrabold text-field-ink">{plan.price}</span>
                      <span className="text-xs text-muted-leaf">{plan.period}</span>
                    </div>
                  </div>
                  <p className="text-xs text-muted-leaf">{plan.targetUser}</p>

                  <ul className="space-y-2 text-xs text-field-ink pt-2 border-t border-structural">
                    {plan.features.map((feat, i) => (
                      <li key={i} className="flex items-center gap-2">
                        <CheckCircle2 size={14} className="text-emerald-600 shrink-0" />
                        <span>{feat}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="pt-6">
                  <Link
                    to="/pricing"
                    className={`block w-full py-2.5 text-center text-xs font-bold rounded-xl transition ${
                      plan.isPopular
                        ? 'bg-field-ink text-white hover:bg-opacity-90'
                        : 'bg-pure-surface border border-structural text-field-ink hover:bg-field-canvas'
                    }`}
                  >
                    {plan.ctaText}
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16 max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="text-center space-y-3 mb-8">
          <span className="eyebrow">Before you start</span>
          <h2 className="text-3xl font-extrabold text-field-ink">Clear answers for a careful rollout</h2>
        </div>
        <div className="divide-y divide-structural rounded-3xl border border-structural bg-pure-surface px-6">
          {[
            ['Is Rakshak AI a confirmed diagnosis?', 'No. It is an AI indication with evidence and confidence. High-risk or uncertain cases can be reviewed by an agronomist.'],
            ['What does a farmer need to capture?', 'A short sweep across the upper, middle, and lower soybean canopy in good light. The app checks video quality before analysis.'],
            ['Can an organization start with a pilot?', 'Yes. Pilot plans are designed for FPO and regional deployments, with scope and support agreed with the field operations team.'],
          ].map(([question, answer]) => <details key={question} className="group py-5"><summary className="cursor-pointer list-none pr-8 text-sm font-bold text-field-ink marker:content-none">{question}<span className="float-right text-muted-leaf transition group-open:rotate-45">+</span></summary><p className="pt-3 text-xs leading-5 text-muted-leaf max-w-2xl">{answer}</p></details>)}
        </div>
      </section>

      {/* Contact CTA */}
      <section className="py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full">
        <div className="bg-soft-healthy border border-emerald-200 rounded-3xl p-8 md:p-12 text-center max-w-4xl mx-auto space-y-6">
          <h2 className="text-3xl font-extrabold text-field-ink">Ready to bring field intelligence to your FPO?</h2>
          <p className="text-sm text-muted-leaf max-w-xl mx-auto">
            Schedule a platform walkthrough with our agricultural specialists or open the workspace.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-4">
            <Link
              to="/login"
              className="px-6 py-3 bg-field-ink text-white font-bold text-xs rounded-xl hover:bg-opacity-90 transition shadow-xs"
            >
              Open workspace
            </Link>
            <Link
              to="/contact"
              className="px-6 py-3 bg-pure-surface text-field-ink border border-structural font-bold text-xs rounded-xl hover:bg-field-canvas transition"
            >
              Contact Fasal Rakshak Team
            </Link>
          </div>
        </div>
      </section>

      <PublicFooter />
    </div>
  );
};
