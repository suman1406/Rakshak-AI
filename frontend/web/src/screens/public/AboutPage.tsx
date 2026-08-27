import React from 'react';
import { PublicNavbar } from '../../components/layout/PublicNavbar';
import { PublicFooter } from '../../components/layout/PublicFooter';
import { SafetyBanner } from '../../components/shared/SafetyBanner';
import { Sprout, ShieldCheck, Heart, Award, Users, Target } from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-field-canvas text-field-ink flex flex-col font-sans">
      <PublicNavbar />

      <main className="flex-1 py-12 md:py-20 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto w-full space-y-12">
        <div className="space-y-4">
          <span className="px-3 py-1 bg-soft-healthy text-emerald-800 text-xs font-bold rounded-full">
            About Fasal Rakshak
          </span>
          <h1 className="text-4xl font-extrabold text-field-ink tracking-tight">
            Protecting Soybean Yields Through Evidence-Based AI Intelligence
          </h1>
          <p className="text-base text-muted-leaf leading-relaxed">
            Rakshak AI was created to bridge the gap between rapid computer vision analysis and expert agricultural field advisory in soybean cultivation hubs across India.
          </p>
        </div>

        <SafetyBanner />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-4">
          <div className="bg-pure-surface p-6 rounded-2xl border border-structural space-y-3">
            <div className="w-10 h-10 rounded-xl bg-field-ink text-lime-signal flex items-center justify-center">
              <Target size={20} />
            </div>
            <h3 className="text-lg font-bold text-field-ink">Our Mission</h3>
            <p className="text-xs text-muted-leaf leading-relaxed">
              Empower smallholder farmers and FPO clusters with early, transparent disease signals, reducing unnecessary pesticide expenditures while preserving crop yields.
            </p>
          </div>

          <div className="bg-pure-surface p-6 rounded-2xl border border-structural space-y-3">
            <div className="w-10 h-10 rounded-xl bg-field-ink text-lime-signal flex items-center justify-center">
              <Users size={20} />
            </div>
            <h3 className="text-lg font-bold text-field-ink">Human-In-The-Loop Commitment</h3>
            <p className="text-xs text-muted-leaf leading-relaxed">
              We never replace the human agronomist. AI models generate probabilistically ranked indicators, which are escalated to verified local agronomists for official recommendation.
            </p>
          </div>
        </div>
      </main>

      <PublicFooter />
    </div>
  );
};
